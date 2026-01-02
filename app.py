import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.set_page_config(
    page_title="Wolf Smart Data Analyzer",
    layout="wide"
)

st.title("🐺 Wolf Smart Data Analyzer")
st.write(
    """
Upload one or more datasets.  
This tool cleans data, analyzes schema quality, detects relationships,
classifies tables, and generates a Data Dictionary.
"""
)

# ================================
# FILE LOADER WITH SMART ENCODING
# ================================
def load_csv_safely(file):
    encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]

    for enc in encodings:
        try:
            return pd.read_csv(file, encoding=enc)
        except UnicodeDecodeError:
            continue

    # Final fallback (prevents crash)
    return pd.read_csv(file, encoding="latin1", errors="ignore")


def load_file(file):
    filename = file.name.lower()

    if filename.endswith(".csv"):
        return load_csv_safely(file)

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(file)

    elif filename.endswith(".json"):
        return pd.read_json(file)

    else:
        st.error(f"Unsupported file format: {filename}")
        return None


# ================================
# FILE UPLOAD SECTION
# ================================
uploaded_files = st.file_uploader(
    "Upload datasets (CSV / Excel / JSON)",
    accept_multiple_files=True,
    type=["csv", "xlsx", "xls", "json"]
)

datasets = {}

if uploaded_files:
    st.success(f"Uploaded {len(uploaded_files)} file(s).")

    for file in uploaded_files:
        try:
            df = load_file(file)

            if df is not None and not df.empty:
                datasets[file.name] = df
                st.write(f"✅ Loaded `{file.name}` — {df.shape[0]} rows × {df.shape[1]} columns")
            else:
                st.warning(f"⚠ `{file.name}` is empty or unreadable")

        except Exception as e:
            st.error(f"❌ Could not read {file.name} — {e}")


st.divider()


# ==========================================
# PROCESS EACH DATASET
# ==========================================
if datasets:

    for name, df in datasets.items():
        st.subheader(f"📂 Dataset: {name}")

        with st.expander("🔎 Preview (Top 50 Rows)", expanded=False):
            st.dataframe(df.head(50), use_container_width=True)

        # =============================
        # AUTO DATA CLEANING
        # =============================
        st.subheader("🧹 Data Cleaning Report")

        null_count = df.isna().sum().sum()
        dup_count = df.duplicated().sum()

        col_nulls = df.isna().sum()

        st.write("**Null Summary**")
        st.write(col_nulls)

        st.info(
            f"Total Missing Values: **{null_count}**  \n"
            f"Duplicate Rows: **{dup_count}**"
        )

        # Remove duplicates automatically
        if dup_count > 0:
            df = df.drop_duplicates()
            st.success("Removed duplicate rows.")

        # =============================
        # COLUMN TYPE ANALYSIS
        # =============================
        st.subheader("📑 Schema Overview")

        schema = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing Values": df.isna().sum(),
            "Unique Values": df.nunique()
        })

        st.dataframe(schema, use_container_width=True)

        # =============================
        # TABLE CLASSIFICATION
        # =============================
        st.subheader("📂 Table Type Classification")

        table_type = "Generic Table"

        col_names = ",".join(df.columns).lower()

        if "date" in col_names or "time" in col_names:
            table_type = "Time-Series Data"
        elif "id" in col_names:
            table_type = "Entity Table"
        elif "amount" in col_names or "price" in col_names:
            table_type = "Financial Table"
        elif "name" in col_names or "email" in col_names:
            table_type = "Customer / People Table"

        st.success(f"Detected Table Type → **{table_type}**")

        # =============================
        # DATA DICTIONARY
        # =============================
        st.subheader("📘 Auto-Generated Data Dictionary")

        dictionary = pd.DataFrame({
            "Column": df.columns,
            "Description": ["(Auto-generated — user may edit)" for _ in df.columns],
            "Datatype": df.dtypes.astype(str),
            "Example Value": [str(df[col].dropna().iloc[0]) if df[col].notna().any() else "" for col in df.columns]
        })

        st.dataframe(dictionary, use_container_width=True)

        csv_export = dictionary.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Data Dictionary (CSV)",
            csv_export,
            file_name=f"{name}_data_dictionary.csv",
            mime="text/csv"
        )

        st.divider()

else:
    st.info("Upload files to begin processing.")
