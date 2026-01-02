import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Wolf Smart Data Analyzer",
    layout="wide",
)

st.title("🐺 Wolf Smart Data Analyzer")

st.write(
    """
Upload one or more datasets.  
This tool cleans data, analyzes schema quality, detects relationships, 
classifies tables, and generates a Data Dictionary.
"""
)


# ------------------------------------------------------------
# UNIVERSAL DATA LOADER
# Handles:
# - Real CSV
# - CSV saved from Excel
# - Mixed encodings
# - XLS / XLSX
# - Mobile uploads
# - Government datasets
# ------------------------------------------------------------
def load_any_table(uploaded_file):

    def rewind():
        uploaded_file.seek(0)

    # ---------- TRY NORMAL CSV FIRST ----------
    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
        "iso-8859-1",
    ]

    for enc in encodings:
        try:
            rewind()
            return pd.read_csv(
                uploaded_file,
                encoding=enc,
                engine="python"
            )
        except Exception:
            pass

    # ---------- IF CSV FAILS → TRY EXCEL ----------
    try:
        rewind()
        return pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception:
        pass

    # ---------- LAST RESORT (RECOVER WHATEVER IS POSSIBLE) ----------
    rewind()
    return pd.read_csv(
        uploaded_file,
        engine="python",
        encoding="latin1",
        on_bad_lines="skip"
    )


# ------------------------------------------------------------
# JSON LOADER
# ------------------------------------------------------------
def load_json_safely(uploaded_file):
    raw = uploaded_file.read().decode("utf-8", errors="ignore")
    data = json.loads(raw)
    return pd.json_normalize(data)


# ------------------------------------------------------------
# FILE ROUTER
# ------------------------------------------------------------
def load_dataset(file):

    suffix = Path(file.name).suffix.lower()

    try:
        if suffix in [".csv", ".xls", ".xlsx"]:
            return load_any_table(file)

        elif suffix == ".json":
            return load_json_safely(file)

        else:
            st.error(f"❌ Unsupported file type: {suffix}")
            return None

    except Exception as e:
        st.error(f"❌ Failed to load {file.name}\n\n{e}")
        return None


# ------------------------------------------------------------
# FILE UPLOADER UI
# ------------------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload datasets (CSV / Excel / JSON)",
    type=["csv", "xls", "xlsx", "json"],
    accept_multiple_files=True
)

datasets = {}

if uploaded_files:
    for file in uploaded_files:
        df = load_dataset(file)

        if df is None:
            continue

        datasets[file.name] = df

    st.success("✅ Files loaded successfully!")


# ------------------------------------------------------------
# PROCESS DATASETS
# ------------------------------------------------------------
if datasets:

    tab_overview, tab_schema, tab_dictionary, tab_model = st.tabs(
        ["📌 Overview", "📊 Schema Quality", "📘 Data Dictionary", "🧩 Model View Diagram"]
    )

    # --------------------------------------------------------
    # 1️⃣ OVERVIEW
    # --------------------------------------------------------
    with tab_overview:
        st.subheader("📌 Dataset Overview")

        for name, df in datasets.items():

            st.markdown(f"### 📁 {name}")
            st.write("Shape:", df.shape)
            st.dataframe(df.head())
            st.write("---")

    # --------------------------------------------------------
    # 2️⃣ SCHEMA QUALITY
    # --------------------------------------------------------
    with tab_schema:
        st.subheader("📊 Schema & Data Health")

        for name, df in datasets.items():

            st.markdown(f"### 🧩 {name}")

            summary = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Null Count": df.isna().sum(),
                "Null %": (df.isna().mean() * 100).round(2),
                "Unique Values": df.nunique()
            })

            st.dataframe(summary, use_container_width=True)
            st.write("---")

    # --------------------------------------------------------
    # 3️⃣ DATA DICTIONARY
    # --------------------------------------------------------
    with tab_dictionary:
        st.subheader("📘 Auto-Generated Data Dictionary")

        for name, df in datasets.items():

            st.markdown(f"### 📁 {name}")

            dictionary = []

            for col in df.columns:
                dictionary.append({
                    "Column": col,
                    "Type": str(df[col].dtype),
                    "Example Value": str(df[col].dropna().iloc[0]) if df[col].notna().any() else None,
                    "Null %": round(df[col].isna().mean() * 100, 2)
                })

            dict_df = pd.DataFrame(dictionary)

            st.dataframe(dict_df, use_container_width=True)

            st.download_button(
                "⬇ Download Data Dictionary",
                dict_df.to_csv(index=False),
                file_name=f"{name}_data_dictionary.csv",
                mime="text/csv"
            )

            st.write("---")

    # --------------------------------------------------------
    # 4️⃣ MODEL VIEW — RELATIONSHIP DIAGRAM
    # --------------------------------------------------------
    with tab_model:
        st.subheader("🧩 Table Relationship Model View")

        from graphviz import Digraph

        graph = Digraph()
        graph.attr(rankdir="LR", bgcolor="#0e1117")

        # Detect likely primary keys
        pk_keywords = ["id", "key", "code"]

        table_pk_map = {}

        for name, df in datasets.items():

            cols = list(df.columns)

            # Find candidate primary key
            pk = None
            for c in cols:
                lc = c.lower()
                if any(k in lc for k in pk_keywords) and df[c].is_unique:
                    pk = c
                    break

            table_pk_map[name] = pk

            # Draw table node
            label = f"<<B>{name}</B><BR ALIGN='LEFT'/>" + "<BR/>".join(cols) + ">"
            graph.node(name, label=label, shape="box", color="cyan")

        # Detect relationships
        relations_found = False

        for t1, df1 in datasets.items():
            for t2, df2 in datasets.items():

                if t1 == t2:
                    continue

                pk = table_pk_map[t2]
                if pk is None:
                    continue

                # If table1 contains column referencing table2 pk
                for col in df1.columns:
                    if col.lower() == pk.lower():
                        graph.edge(t1, t2, label=col)
                        relations_found = True

        if relations_found:
            st.graphviz_chart(graph, use_container_width=True)
        else:
            st.info("ℹ No relational links detected — tables appear independent.")

else:
    st.info("📂 Upload datasets to begin.")
