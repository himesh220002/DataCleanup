import streamlit as st
import pandas as pd
import altair as alt
import os
import sys

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pipelines.data_cleaning_pipeline import DataCleaningPipeline

st.set_page_config(page_title="Student Intelligence System", layout="wide")

col_title, col_button = st.columns([4, 1])

with col_title:
    st.title("🎓 Student Performance Intelligence System")
    st.markdown("An automated AI/ML architecture for education risk-forecasting and engagement analytics.")

# --- View Sample Data Modal ---
@st.dialog("Sample Data Preview (2 Random Rows)")
def show_sample_data(file_path):
    try:
        sample_df = pd.read_csv(file_path)
        if len(sample_df) >= 2:
            sample_df = sample_df.sample(n=2)
        st.dataframe(sample_df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load sample data: {e}")

with col_button:
    st.write("") # Vertical spacing
    st.write("") 
    if st.button("👀 View Sample Data", use_container_width=True):
        sample_file_path = os.path.join("data/raw", "student_sample_2_students.csv")
        if os.path.exists(sample_file_path):
            show_sample_data(sample_file_path)
        else:
            st.warning(f"Sample file not found: {sample_file_path}")

# --- Data Upload & Execution Flow ---
st.sidebar.header("📁 Data Source")

raw_dir = "data/raw"
proc_dir = "data/processed"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(proc_dir, exist_ok=True)

source_type = st.sidebar.radio("Select Source Type", ["Upload New File", "Select Existing Raw Data", "Select Existing Processed Data"])

target_filename = None
is_processed = False

if source_type == "Upload New File":
    uploaded_file = st.sidebar.file_uploader("Upload Student Dataset (CSV/Excel)", type=["csv", "xlsx"])
    if uploaded_file is not None:
        file_path = os.path.join(raw_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        target_filename = uploaded_file.name
    else:
        st.sidebar.info("Please upload a file.")

elif source_type == "Select Existing Raw Data":
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv') or f.endswith('.xlsx')]
    if raw_files:
        target_filename = st.sidebar.selectbox("Select Raw File", raw_files)
    else:
        st.sidebar.warning("No raw files found.")

elif source_type == "Select Existing Processed Data":
    proc_files = [f for f in os.listdir(proc_dir) if f.endswith('.csv')]
    if proc_files:
        target_filename = st.sidebar.selectbox("Select Processed File", proc_files)
        is_processed = True
    else:
        st.sidebar.warning("No processed files found.")

if target_filename:
    button_label = "⚡ Load Processed Dashboard" if is_processed else "🚀 Run Intelligence Analysis"
    if st.sidebar.button(button_label):
        if is_processed:
            with st.spinner("Loading Processed Data directly..."):
                try:
                    df = pd.read_csv(os.path.join(proc_dir, target_filename))
                    st.session_state['student_results'] = {'smart_ready': df}
                    st.session_state['student_filename'] = target_filename
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading processed file: {e}")
        else:
            with st.spinner("Processing Data through Cleanup Pipeline..."):
                pipeline = DataCleaningPipeline(raw_data_dir=raw_dir, processed_data_dir=proc_dir)
                try:
                    clean_results = pipeline.run_pipeline(
                        filename=target_filename,
                        output_filename=f"clean_{target_filename}"
                    )
                    st.session_state['student_results'] = clean_results
                    st.session_state['student_filename'] = target_filename
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing pipeline: {e}")

if 'student_results' in st.session_state:
    df_smart = st.session_state['student_results']['smart_ready'].copy()
    filename = st.session_state['student_filename']
    
    # --- Feature Engineering ---
    # Engagement Index (Focus + Homework + Q&A)
    # Robustly find column names (handles non-breaking hyphens)
    focus_cols = [c for c in df_smart.columns if 'Focus' in c]
    hw_cols = [c for c in df_smart.columns if 'Homework' in c]
    qa_cols = [c for c in df_smart.columns if 'Q&A' in c]
    
    if focus_cols and hw_cols and qa_cols:
        df_smart['Engagement Index'] = ((df_smart[focus_cols[0]] + df_smart[hw_cols[0]] + df_smart[qa_cols[0]]) / 30) * 100
    else:
        df_smart['Engagement Index'] = 0.0
        
    # Calculate Avg Test Score
    ut_cols = [c for c in df_smart.columns if 'Unit Test' in c]
    if len(ut_cols) > 0:
        df_smart['Avg Test Score'] = df_smart[ut_cols].mean(axis=1)
    else:
        df_smart['Avg Test Score'] = 0.0
        
    # --- Interactive Filtering ---
    st.sidebar.header("🎯 Dashboard Filters")
    
    if 'Class' in df_smart.columns:
        classes = sorted(df_smart['Class'].dropna().unique().tolist())
        selected_classes = st.sidebar.multiselect("Select Class", options=classes, default=classes)
    else:
        selected_classes = []
        
    if 'Section' in df_smart.columns:
        sections = sorted(df_smart['Section'].dropna().unique().tolist())
        selected_sections = st.sidebar.multiselect("Select Section", options=sections, default=sections)
    else:
        selected_sections = []

    # Apply Filters
    df_filtered = df_smart.copy()
    if selected_classes and 'Class' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Class'].isin(selected_classes)]
    if selected_sections and 'Section' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Section'].isin(selected_sections)]
        
    if df_filtered.empty:
        st.warning("No students match the selected filters.")
    else:
        # --- Insights Construction ---
        st.header("📊 Executive Dashboard")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Filtered Students", len(df_filtered))
        
        avg_att = df_filtered['Attendance (%)'].mean() if 'Attendance (%)' in df_filtered.columns else 0
        col2.metric("Avg Attendance", f"{avg_att:.1f}%")
        
        avg_eng = df_filtered['Engagement Index'].mean()
        col3.metric("Avg Engagement", f"{avg_eng:.1f}/100")
        
        avg_score = df_filtered['Avg Test Score'].mean() if 'Avg Test Score' in df_filtered.columns else 0
        col4.metric("Avg Test Score", f"{avg_score:.1f}%")
        
        if 'Avg Test Score' in df_filtered.columns and not df_filtered.empty:
            mean_score = df_filtered['Avg Test Score'].mean()
            median_score = df_filtered['Avg Test Score'].median()
            mode_scores = df_filtered['Avg Test Score'].mode()
            mode_score = mode_scores.iloc[0] if not mode_scores.empty else 0
            st.caption(f"**Overall Test Score Stats:** Mean: {mean_score:.1f}% | Median: {median_score:.1f}% | Mode: {mode_score:.1f}%")

        st.divider()

        st.subheader("🔍 At-Risk Predictor & Recommendations")
        # Risk Filter: < 75% attendance OR Unit Test 3 < 70
        if 'Attendance (%)' in df_filtered.columns and 'Unit Test 3' in df_filtered.columns:
            at_risk = df_filtered[(df_filtered['Attendance (%)'] < 75) | (df_filtered['Unit Test 3'] < 70)].copy()
            
            if not at_risk.empty:
                at_risk['Intervention Recommendation'] = at_risk.apply(
                    lambda row: "Schedule Extra Doubt Session" if ('Doubt Asking Rate' in row and row['Doubt Asking Rate'] < 0.4) else "Focus & Homework Monitoring", axis=1
                )
                
                # Reorder columns for display
                avail_cols = [c for c in ['ID', 'Name', 'Class', 'Section', 'Attendance (%)', 'Unit Test 3', 'Avg Test Score', 'Engagement Index', 'Intervention Recommendation'] if c in at_risk.columns]
                st.dataframe(at_risk[avail_cols], use_container_width=True)
            else:
                st.success("No students are currently marked as at-risk in this filtered view.")
        else:
            st.info("Required columns for Risk Predictor not found.")

        st.divider()

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("📈 Attendance vs Rank Correlation")
            if 'Attendance (%)' in df_filtered.columns and 'Rank' in df_filtered.columns and 'Section' in df_filtered.columns:
                # Recalculate rank dynamically based on the filtered subset
                df_filtered['Dynamic Rank'] = df_filtered['Rank'].rank(method='dense').astype(int)
                
                # Determine max rank for y-axis scaling
                max_rank = df_filtered['Dynamic Rank'].max() if not df_filtered.empty else 1
                
                scatter_chart = alt.Chart(df_filtered).mark_circle(size=80).encode(
                    x=alt.X('Attendance (%):Q', scale=alt.Scale(domain=[40, 100])),
                    y=alt.Y('Dynamic Rank:Q', 
                            scale=alt.Scale(reverse=True, domain=[1, max_rank]),
                            axis=alt.Axis(tickMinStep=1, format='d')),
                    color='Section:N',
                    tooltip=[c for c in ['Name', 'Attendance (%)', 'Dynamic Rank', 'Section'] if c in df_filtered.columns]
                ).interactive()
                st.altair_chart(scatter_chart, use_container_width=True)
            else:
                st.info("Chart data missing.")

        with col_chart2:
            st.subheader("🔥 Average Engagement by Section")
            if 'Section' in df_filtered.columns:
                bar_chart = alt.Chart(df_filtered).mark_bar().encode(
                    x='Section:N',
                    y='mean(Engagement Index):Q',
                    color='Section:N',
                    tooltip=['Section', 'mean(Engagement Index)']
                )
                st.altair_chart(bar_chart, use_container_width=True)
            else:
                st.info("Chart data missing.")

        st.divider()

        st.subheader("✨ Filtered Engagement Dataset")
        st.markdown("Download the filtered subset along with the calculated Engagement Index and Intervention tracking.")
        
        # Add Intervention Recommendation to main dataframe for download
        df_download = df_filtered.copy().reset_index(drop=True)
        df_download.index = df_download.index + 1
        if 'Attendance (%)' in df_download.columns and 'Unit Test 3' in df_download.columns:
             df_download['Intervention'] = df_download.apply(
                lambda row: ("Schedule Extra Doubt Session" if row.get('Doubt Asking Rate', 1) < 0.4 else "Focus Monitoring") 
                if (row['Attendance (%)'] < 75 or row['Unit Test 3'] < 70) else "On Track", axis=1
             )
        
        st.dataframe(df_download.head(10), use_container_width=True)
        
        csv_data = df_download.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Engagement Dataset",
            data=csv_data,
            file_name=f"filtered_engagement_{filename}",
            mime="text/csv",
        )
        
        if st.sidebar.button("🧹 Clear Results"):
            st.session_state.pop('student_results', None)
            st.session_state.pop('student_filename', None)
            st.rerun()
