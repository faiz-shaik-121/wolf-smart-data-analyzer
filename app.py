import streamlit as st
import pandas as pd
import numpy as np
import json
import chardet

from io import StringIO
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
# UNIVERSAL SAFE CSV LOADER (Mobile + Govt Data + Excel Exports)
# ------------------------------------------------------------
def load_csv_safely(uploaded_file):

    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
        "iso-8859-1",
        "iso-8859-15"
    ]

    for enc in encodings_to_try:
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding=enc, engine="python")
        except Exception:
            continue

    # last fallback — ignore bad bytes
    uploaded_file.seek(0)
    return pd.read_csv(
        uploaded_file,
        encoding="latin1",
        engine="python",
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
# DATASET LOADER ROUTER
# ------------------------------------------------------------
def load_dataset(file):

    suffix = Path(file.name).suffix.lower()

    try:
        if suffix == ".csv":
            return load_csv_safely(file)

        elif suffix in (".xls", ".xlsx"):
            return pd.read_excel(file)

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

    tab_overview, tab_schema, tab_dictionary = st.tabs(
        ["📌 Overview", "📊 Schema Quality", "📘 Data Dictionary"]
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

                column_info = {
                    "Column": col,
                    "Type": str(df[col].dtype),
                    "Example Value": str(df[col].dropna().iloc[0]) if df[col].notna().any() else None,
                    "Null %": round(df[col].isna().mean() * 100, 2)
                }

                dictionary.append(column_info)

            dict_df = pd.DataFrame(dictionary)

            st.dataframe(dict_df, use_container_width=True)

            st.download_button(
                label="⬇ Download Data Dictionary",
                data=dict_df.to_csv(index=False),
                file_name=f"{name}_data_dictionary.csv",
                mime="text/csv",
            )

            st.write("---")

else:
    st.info("📂 Upload datasets to begin.")

