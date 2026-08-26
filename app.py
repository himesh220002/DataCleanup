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

st.sidebar.header("📁 Existing Data")
source_type = st.sidebar.radio("Load From Server", ["None", "Raw Data", "Processed Data"])

raw_dir = "data/raw"
proc_dir = "data/processed"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(proc_dir, exist_ok=True)

target_filename = None
is_processed = False
file_path = None

# Always display upload option on the main page
uploaded_file = st.file_uploader("Upload a new dataset (CSV/Excel/JSON)", type=["csv", "xlsx", "json"])

if uploaded_file is not None:
    file_path = os.path.join(raw_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    target_filename = uploaded_file.name
    st.success(f"File {uploaded_file.name} uploaded successfully!")
elif source_type == "Raw Data":
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith(('.csv', '.xlsx', '.json'))]
    if raw_files:
        target_filename = st.sidebar.selectbox("Select Raw File", raw_files)
        if target_filename:
            file_path = os.path.join(raw_dir, target_filename)
    else:
        st.sidebar.warning("No raw files found.")
elif source_type == "Processed Data":
    proc_files = [f for f in os.listdir(proc_dir) if f.endswith(('.csv', '.xlsx', '.json'))]
    if proc_files:
        target_filename = st.sidebar.selectbox("Select Processed File", proc_files)
        if target_filename:
            file_path = os.path.join(proc_dir, target_filename)
            is_processed = True
    else:
        st.sidebar.warning("No processed files found.")

if file_path and target_filename:
    if target_filename.endswith('.csv'):
        df_display = pd.read_csv(file_path, nrows=20)
    elif target_filename.endswith('.json'):
        df_display = pd.read_json(file_path)
        df_display = df_display.head(20)
    else:
        df_display = pd.read_excel(file_path, nrows=20)
        
    st.subheader(f"{'Processed' if is_processed else 'Raw'} Data Preview")
    st.dataframe(df_display)
    
    if not is_processed:
        if st.button("🚀 Run Data Cleaning Pipeline"):
            with st.spinner("Executing 8-Phase Cleaning Pipeline..."):
                pipeline = DataCleaningPipeline(raw_data_dir=raw_dir, processed_data_dir=proc_dir)
                
                date_columns = [c.strip() for c in date_cols_input.split(',')] if date_cols_input else None
                
                # Execute pipeline
                # Ensure output has .csv extension regardless of input
                base_name = os.path.splitext(target_filename)[0]
                output_filename = f"clean_{base_name}.csv"
                
                clean_results = pipeline.run_pipeline(
                    filename=target_filename,
                    date_columns=date_columns,
                    scale_method=scale_method,
                    output_filename=output_filename
                )
                
                # Save to session state so downloading doesn't clear the results
                # Store only head() to save memory
                st.session_state['clean_results'] = {
                    'ml_ready': clean_results['ml_ready'].head(20),
                    'analyst_ready': clean_results['analyst_ready'].head(20),
                    'smart_ready': clean_results['smart_ready'].head(20)
                }
                st.session_state['uploaded_filename'] = target_filename
                st.rerun()

    if 'clean_results' in st.session_state:
        clean_results = st.session_state['clean_results']
        filename = st.session_state['uploaded_filename']
        base_name = os.path.splitext(filename)[0]
        csv_filename = f"{base_name}.csv"
        
        df_ml = clean_results['ml_ready']
        df_analyst = clean_results['analyst_ready']
        df_smart = clean_results['smart_ready']
        
        st.subheader("🧠 ML-Ready Data Preview")
        st.markdown("Features are scaled, normalized, and optimized for model training.")
        st.dataframe(df_ml)
        
        st.subheader("📊 Analyst-Ready Data Preview")
        st.markdown("Features retain original scale, human-readable casing, and untampered identifiers.")
        st.dataframe(df_analyst)
        
        st.subheader("✨ Smart-Ready Data Preview")
        st.markdown("Anomalies are fixed intelligently, missing values are imputed with useful values, and columns are logically rearranged.")
        st.dataframe(df_smart)
        
        # Generate Download Links
        col1, col2, col3 = st.columns(3)
        with col1:
            ml_path = os.path.join(proc_dir, f"ml_clean_{csv_filename}")
            if os.path.exists(ml_path):
                with open(ml_path, "rb") as f:
                    st.download_button(
                        label="📥 Download ML-Ready Dataset",
                        data=f,
                        file_name=f"ml_ready_{csv_filename}",
                        mime="text/csv",
                    )
        with col2:
            analyst_path = os.path.join(proc_dir, f"analyst_clean_{csv_filename}")
            if os.path.exists(analyst_path):
                with open(analyst_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Analyst-Ready Dataset",
                        data=f,
                        file_name=f"analyst_ready_{csv_filename}",
                        mime="text/csv",
                    )
        with col3:
            smart_path = os.path.join(proc_dir, f"smart_clean_{csv_filename}")
            if os.path.exists(smart_path):
                with open(smart_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Smart-Ready Dataset",
                        data=f,
                        file_name=f"smart_ready_{csv_filename}",
                        mime="text/csv",
                    )
            
        st.success("Pipeline Execution Complete!")
        
        if st.button("🧹 Clear Results"):
            st.session_state.pop('clean_results', None)
            st.session_state.pop('uploaded_filename', None)
            st.rerun()

else:
    
    st.markdown("---")
    st.subheader("💡 How it Works: Example Transformation")
    st.markdown("The Enterprise Data Cleanup Engine automatically transforms messy, inconsistent data into ML-ready and Analyst-ready formats.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Raw Messy Data (Input)**")
        mock_raw = pd.DataFrame({
            "Name": ["john doe", "JANE SMITH", "john doe ", "alice"],
            "Age": [25, 200, None, 30],
            "Date": ["12/31/2022", "2023-01-01", "12-31-2022", "invalid"],
            "Salary": ["$50,000", "60000", "50000", "70k"]
        })
        st.dataframe(mock_raw, width='stretch')
    with col2:
        st.markdown("**2. Smart-Ready Data (Output)**")
        mock_clean = pd.DataFrame({
            "Name": ["John Doe", "Jane Smith", "Alice"],
            "Age": [25.0, 30.0, 30.0],
            "Date": ["2022-12-31", "2023-01-01", "None"],
            "Salary": [50000.0, 60000.0, 70000.0]
        })
        st.dataframe(mock_clean, width='stretch')
        
    st.markdown("- **Deduplication:** Fuzzy matching and exact duplicate removal.\\n- **Anomaly Fixing:** Outlier detection and intelligent value replacement.\\n- **Normalization:** Standardizing formats like dates, text casing, and currencies.\\n- **Scaling:** Preparing numerical columns for machine learning algorithms.")
