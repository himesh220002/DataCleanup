import streamlit as st
import pandas as pd
import os
import sys

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from pipelines.data_cleaning_pipeline import DataCleaningPipeline

st.set_page_config(page_title="Data Cleanup Engine", layout="wide")

st.title("🧹 Enterprise Data Cleanup Engine")
st.markdown("Upload your raw dataset and let the automated ML-powered pipeline clean, deduplicate, and scale it.")

from typing import cast, Literal

# Sidebar Configuration
st.sidebar.header("⚙️ Pipeline Configuration")
scale_method = cast(Literal["standard", "minmax"], st.sidebar.selectbox("Scaling Method", ["standard", "minmax"]))
date_cols_input = st.sidebar.text_input("Date Columns (comma separated)", "date")
fuzzy_threshold = st.sidebar.slider("Fuzzy Matching Threshold (%)", 50, 100, 90)

uploaded_file = st.file_uploader("Upload Raw Dataset (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    raw_dir = "data/raw"
    proc_dir = "data/processed"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    
    file_path = os.path.join(raw_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"File {uploaded_file.name} uploaded successfully!")
    
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(file_path)
    else:
        df_raw = pd.read_excel(file_path)
        
    st.subheader("Raw Data Preview")
    st.dataframe(df_raw.head())
    
    if st.button("🚀 Run Data Cleaning Pipeline"):
        with st.spinner("Executing 8-Phase Cleaning Pipeline..."):
            pipeline = DataCleaningPipeline(raw_data_dir=raw_dir, processed_data_dir=proc_dir)
            
            date_columns = [c.strip() for c in date_cols_input.split(',')] if date_cols_input else None
            
            # Execute pipeline
            clean_results = pipeline.run_pipeline(
                filename=uploaded_file.name,
                date_columns=date_columns,
                scale_method=scale_method,
                output_filename=f"clean_{uploaded_file.name}"
            )
            
            # Save to session state so downloading doesn't clear the results
            st.session_state['clean_results'] = clean_results
            st.session_state['uploaded_filename'] = uploaded_file.name
            st.rerun()

    if 'clean_results' in st.session_state:
        clean_results = st.session_state['clean_results']
        filename = st.session_state['uploaded_filename']
        
        df_ml = clean_results['ml_ready']
        df_analyst = clean_results['analyst_ready']
        df_smart = clean_results['smart_ready']
        
        st.subheader("🧠 ML-Ready Data Preview")
        st.markdown("Features are scaled, normalized, and optimized for model training.")
        st.dataframe(df_ml.head())
        
        st.subheader("📊 Analyst-Ready Data Preview")
        st.markdown("Features retain original scale, human-readable casing, and untampered identifiers.")
        st.dataframe(df_analyst.head())
        
        st.subheader("✨ Smart-Ready Data Preview")
        st.markdown("Anomalies are fixed intelligently, missing values are imputed with useful values, and columns are logically rearranged.")
        st.dataframe(df_smart.head())
        
        # Generate Download Links
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_ml = df_ml.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download ML-Ready Dataset",
                data=csv_ml,
                file_name=f"ml_ready_{filename}",
                mime="text/csv",
            )
        with col2:
            csv_analyst = df_analyst.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Analyst-Ready Dataset",
                data=csv_analyst,
                file_name=f"analyst_ready_{filename}",
                mime="text/csv",
            )
        with col3:
            csv_smart = df_smart.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Smart-Ready Dataset",
                data=csv_smart,
                file_name=f"smart_ready_{filename}",
                mime="text/csv",
            )
            
        st.success("Pipeline Execution Complete!")
        
        if st.button("🧹 Clear Results"):
            st.session_state.pop('clean_results', None)
            st.session_state.pop('uploaded_filename', None)
            st.rerun()
