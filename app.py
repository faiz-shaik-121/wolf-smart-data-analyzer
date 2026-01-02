import streamlit as st
import pandas as pd
import numpy as np
from graphviz import Digraph

st.set_page_config(
    page_title="Smart Data Analyzer — Model & Data Dictionary",
    layout="wide"
)

st.title("🐺 Wolf Smart Data Analyzer")

st.write(
    "Upload one or more datasets. "
    "This tool cleans data, analyzes schema quality, "
    "detects relationships, classifies tables, "
    "and generates a Data Dictionary."
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_files = st.file_uploader(
    "Upload datasets (CSV / Excel / JSON)",
    type=["csv", "xlsx", "json"],
    accept_multiple_files=True
)

datasets = {}

def load_file(file):

    name = file.name

    try:
        if name.endswith(".csv"):
            return pd.read_csv(file)

        elif name.endswith(".xlsx"):
            return pd.read_excel(file)

        elif name.endswith(".json"):
            return pd.read_json(file)

        else:
            st.warning(f"Unsupported file type: {name}")
            return None

    except Exception as e:
        st.error(f"❌ Could not read {name} — {e}")
        return None


if uploaded_files:
    for file in uploaded_files:
        df = load_file(file)
        if df is not None:
            datasets[file.name] = df.copy()



# =========================================================
# STRONG DATA CLEANING PIPELINE
# =========================================================

def clean_dataset(df):

    df = df.copy()

    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()

    df.columns = [c.strip() for c in df.columns]

    # strip whitespace + remove line breaks
    for col in df.columns:
        try:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("\n", " ")
                .str.strip()
            )
        except:
            pass

    # convert numeric-like text
    for col in df.columns:
        try:
            df[col] = (
                df[col]
                .str.replace(",", "")
                .str.replace("%", "")
                .str.replace("₹", "")
                .str.replace("$", "")
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="ignore")
        except:
            pass

    # convert possible date fields
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="ignore")
        except:
            pass

    return df, duplicate_count



# =========================================================
# QUALITY REPORT
# =========================================================

def quality_report(df):

    return pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(df[c].dtype) for c in df.columns],
        "Missing Values": df.isnull().sum().values,
        "Missing %": np.round((df.isnull().sum() / len(df)) * 100, 2),
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Primary Key Candidate": [
            df[c].nunique() == len(df) for c in df.columns
        ]
    })



# =========================================================
# DATA DICTIONARY ENGINE
# =========================================================

def generate_data_dictionary(df):

    rows = []

    for col in df.columns:

        sample_value = df[col].dropna().iloc[0] if df[col].dropna().size > 0 else None

        unique_ratio = round(df[col].nunique() / len(df), 3)

        role = "Unknown"

        # heuristics
        name = col.lower()

        if "id" in name or "code" in name or "key" in name:
            role = "Identifier / Key Field"

        elif np.issubdtype(df[col].dtype, np.number):
            role = "Numeric Metric"

        elif np.issubdtype(df[col].dtype, np.datetime64):
            role = "Date / Time Field"

        elif df[col].nunique() < len(df) * 0.2:
            role = "Categorical Attribute"

        if df[col].nunique() == len(df):
            role = "Primary Key Candidate"

        rows.append([
            col,
            str(df[col].dtype),
            sample_value,
            df[col].nunique(),
            unique_ratio,
            role
        ])

    return pd.DataFrame(
        rows,
        columns=[
            "Column",
            "Data Type",
            "Sample Value",
            "Unique Count",
            "Uniqueness Ratio",
            "Detected Role"
        ]
    )



# =========================================================
# FACT vs DIMENSION TABLE CLASSIFIER
# =========================================================

def classify_table(df):

    numeric_cols = df.select_dtypes(include=["int64","float64"]).shape[1]
    row_count = len(df)

    if row_count > 1000 and numeric_cols > 2:
        return "FACT TABLE"

    if df.shape[1] <= 6:
        return "DIMENSION TABLE"

    return "REFERENCE / MIXED"



# =========================================================
# RELATIONSHIP DETECTION + MODEL VIEW
# =========================================================

def detect_relationships_and_graph(datasets):

    dot = Digraph()
    relations = []
    table_roles = []

    # draw tables + detect type
    for name, df in datasets.items():

        table_type = classify_table(df)

        table_roles.append([name, table_type, len(df)])

        cols = "\n".join(list(df.columns))

        dot.node(name, f"{name}\n({table_type})\n\n{cols}", shape="box")

    # detect shared columns
    for t1, df1 in datasets.items():
        for t2, df2 in datasets.items():

            if t1 == t2:
                continue

            common_cols = set(df1.columns).intersection(df2.columns)

            for col in common_cols:

                try:
                    overlap = len(
                        set(df1[col]).intersection(set(df2[col]))
                    )
                    strength = round(
                        (overlap / max(len(df1), len(df2))) * 100, 2
                    )
                except:
                    strength = 0

                relations.append([t1, t2, col, strength])

                dot.edge(
                    t1,
                    t2,
                    label=f"{col} ({strength}%)"
                )

    rel_df = pd.DataFrame(
        relations,
        columns=["Table A", "Table B", "Linked Field", "Match Strength %"]
    )

    role_df = pd.DataFrame(
        table_roles,
        columns=["Table", "Detected Type", "Row Count"]
    )

    return rel_df, role_df, dot



# =========================================================
# PROCESS DATASETS (TAB VIEW)
# =========================================================

if len(datasets) > 0:

    tabs = st.tabs(list(datasets.keys()))

    for i, name in enumerate(datasets):

        df_raw = datasets[name]

        with tabs[i]:

            st.subheader(f"📁 {name}")

            st.write("### 🔍 Raw Preview")
            st.dataframe(df_raw.head(), use_container_width=True)

            df_clean, removed_dupes = clean_dataset(df_raw)

            st.write("### 🧼 Cleaned Dataset")
            st.dataframe(df_clean.head(), use_container_width=True)

            st.divider()

            # Overview metrics
            st.write("### 🟦 Dataset Overview")

            c1, c2, c3, c4 = st.columns(4)

            with c1: st.metric("Rows", df_clean.shape[0])
            with c2: st.metric("Columns", df_clean.shape[1])
            with c3: st.metric("Duplicate Rows Removed", removed_dupes)
            with c4: st.metric("Missing Cells", int(df_clean.isnull().sum().sum()))

            st.divider()

            # Quality report
            st.write("### 🧩 Data Quality Report")

            qr = quality_report(df_clean)

            st.dataframe(qr, use_container_width=True)

            st.divider()

            # DATA DICTIONARY
            st.write("### 🧠 Data Dictionary")

            dd = generate_data_dictionary(df_clean)

            st.dataframe(dd, use_container_width=True)

            st.divider()

            # Download cleaned file
            csv_bytes = df_clean.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇ Download Cleaned Dataset",
                data=csv_bytes,
                file_name=f"cleaned_{name}.csv",
                mime="text/csv"
            )



# =========================================================
# GLOBAL MODEL VIEW + TABLE CLASSIFICATION
# =========================================================

if len(datasets) >= 2:

    st.divider()
    st.write("## 🧠 Model View — Table Relationships & Classification")

    rel_df, role_df, graph = detect_relationships_and_graph(datasets)

    st.write("### 🟡 Table Type Classification")
    st.dataframe(role_df, use_container_width=True)

    if len(rel_df) == 0:
        st.info("No relationships detected.")
    else:
        st.write("### 🔗 Relationship Mapping")
        st.dataframe(rel_df, use_container_width=True)

    st.write("### 📐 Model Diagram")
    st.graphviz_chart(graph)

elif len(datasets) == 1:
    st.info("Upload 2 or more datasets to generate Model View.")
