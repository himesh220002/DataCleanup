import re

with open('pages/1_Student_Intelligence.py', 'r') as f:
    content = f.read()

# 1. Imports
content = content.replace('import sys\n', 'import sys\nimport openai\n')

# 2. Schema and ID Normalizer
old_schema = "    # Engagement Index"
new_schema = """    # --- Schema Normalization for Resiliency ---
    col_map = {}
    for c in df_smart.columns:
        c_lower = c.lower().replace(' ', '').replace('_', '')
        if 'attendence' in c_lower or 'attendance' in c_lower: col_map[c] = 'Attendance (%)'
        elif 'unittest1' in c_lower or 'unit1' in c_lower: col_map[c] = 'Unit Test 1'
        elif 'unittest2' in c_lower or 'unit2' in c_lower: col_map[c] = 'Unit Test 2'
        elif 'unittest3' in c_lower or 'unit3' in c_lower: col_map[c] = 'Unit Test 3'
        elif 'halfyrly' in c_lower or 'halfyearly' in c_lower: col_map[c] = 'Half Yearly'
        elif c_lower == 'class': col_map[c] = 'Class'
        elif c_lower == 'section': col_map[c] = 'Section'
        elif c_lower == 'name': col_map[c] = 'Name'
        elif c_lower == 'id': col_map[c] = 'ID'
        elif c_lower == 'subject': col_map[c] = 'Subject'
        elif 'hometution' in c_lower or 'hometuition' in c_lower: col_map[c] = 'Home Tuition (Y/N)'
    df_smart = df_smart.rename(columns=col_map)
    
    # Standardize ID to be unique per Student, not per Row
    if all(c in df_smart.columns for c in ['Class', 'Section', 'Name', 'ID']):
        if df_smart.groupby(['Class', 'Section', 'Name'])['ID'].nunique().max() > 1:
            group_id = df_smart.groupby(['Class', 'Section', 'Name']).ngroup() + 1
            df_smart['ID'] = df_smart['Class'].astype(str) + "_" + df_smart['Section'].astype(str) + "_" + group_id.astype(str)

    # Engagement Index"""
content = content.replace(old_schema, new_schema)

# 3. Dynamic Rank and Intervention Logic
old_rank = """    # --- Interactive Filtering ---"""
new_rank = """    if all(c in df_smart.columns for c in ['Class', 'Section', 'Subject']):
        df_smart['Rank'] = df_smart.groupby(['Class', 'Section', 'Subject'])['Avg Test Score'].rank(ascending=False, method='min').astype(int)
    else:
        df_smart['Rank'] = df_smart['Avg Test Score'].rank(ascending=False, method='min').astype(int)

    def get_intervention(row):
        avg_score = row.get('Avg Test Score', 100)
        ut3_score = row.get('Unit Test 3', 40)
        engagement = row.get('Engagement Index', 100)
        risk_factors = []
        if pd.notnull(avg_score) and avg_score < 50: risk_factors.append("Low Avg Score")
        if pd.notnull(ut3_score) and ut3_score < 16: risk_factors.append("Low UT3")
        if pd.notnull(engagement) and engagement < 40: risk_factors.append("Low Engagement")
        if not risk_factors: return "On Track"
        elif len(risk_factors) >= 2: return "Critical Risk: Parent-Teacher Meeting & Core Remedial"
        elif "Low Engagement" in risk_factors: return "Behavioral Risk: Immediate Focus & Motivation Intervention"
        elif "Low UT3" in risk_factors: return "Recent Drop: Extra Doubt Sessions for UT3 Concepts"
        else: return "Academic Risk: Assign Extra Practice & Monitor"

    df_smart['Intervention Recommendation'] = df_smart.apply(get_intervention, axis=1)

    # --- Interactive Filtering ---"""
content = content.replace(old_rank, new_rank)

# 4. At Risk UI
old_atrisk = """        # Risk Filter: < 75% attendance OR Unit Test 3 < 70
        if 'Attendance (%)' in df_filtered.columns and 'Unit Test 3' in df_filtered.columns:
            at_risk = df_filtered[(df_filtered['Attendance (%)'] < 75) | (df_filtered['Unit Test 3'] < 70)].copy()
            
            if not at_risk.empty:
                at_risk['Intervention Recommendation'] = at_risk.apply(
                    lambda row: "Schedule Extra Doubt Session" if ('Doubt Asking Rate' in row and row['Doubt Asking Rate'] < 0.4) else "Focus & Homework Monitoring", axis=1
                )
                
                # Reorder columns for display
                avail_cols = [c for c in ['ID', 'Name', 'Class', 'Section', 'Subject', 'Attendance (%)', 'Unit Test 3', 'Avg Test Score', 'Engagement Index', 'Intervention Recommendation'] if c in at_risk.columns]
                st.dataframe(at_risk[avail_cols], use_container_width=True)
            else:
                st.success("No students are currently marked as at-risk in this filtered view.")
        else:
            st.info("Required columns for Risk Predictor not found.")"""

new_atrisk = """        if 'Intervention Recommendation' in df_filtered.columns:
            at_risk = df_filtered[df_filtered['Intervention Recommendation'] != 'On Track'].copy()
            if not at_risk.empty:
                avail_cols = [c for c in ['ID', 'Name', 'Class', 'Section', 'Subject', 'Avg Test Score', 'Unit Test 3', 'Engagement Index', 'Intervention Recommendation'] if c in at_risk.columns]
                st.dataframe(at_risk[avail_cols], use_container_width=True)
            else:
                st.success("No students are currently marked as at-risk in this filtered view.")
        else:
            st.info("Required columns for Risk Predictor not found.")"""
content = content.replace(old_atrisk, new_atrisk)

# 5. df_download intervention
content = content.replace("            if 'Attendance (%)' in df_download.columns and 'Unit Test 3' in df_download.columns:\n                 df_download['Intervention'] = df_download.apply(\n                    lambda row: (\"Schedule Extra Doubt Session\" if row.get('Doubt Asking Rate', 1) < 0.4 else \"Focus Monitoring\") \n                    if (row['Attendance (%)'] < 75 or row['Unit Test 3'] < 70) else \"On Track\", axis=1\n                 )", 
                          "            if 'Intervention Recommendation' in df_download.columns:\n                 df_download['Intervention'] = df_download['Intervention Recommendation']")

# 6. Tab 2 Replacement
old_tab2_start = """            if not df_download.empty and 'Name' in df_download.columns:
                if 'ID' in df_download.columns:
                    search_options = df_download.apply(lambda row: f"{row['ID']} - {row['Name']}", axis=1).unique().tolist()
                    selected_val = st.selectbox("Search Student (by Name or ID):", options=search_options)
                    selected_id = str(selected_val).split(" - ")[0]
                    student_data = df_download[df_download['ID'].astype(str) == selected_id].iloc[0]
                else:
                    student_names = df_download['Name'].unique().tolist()
                    selected_student_name = st.selectbox("Select Student:", options=student_names)
                    student_data = df_download[df_download['Name'] == selected_student_name].iloc[0]
                
                st.markdown("---")
                st.subheader(f"🎯 Detailed View: {student_data.get('Name', 'Unknown')}")
                
                # Prepare data for Radar Chart
                
                def get_col_val(keyword, default=0):
                    cols = [c for c in student_data.index if keyword in c]
                    return student_data[cols[0]] if cols else default
                    
                # Scale metrics out of 100
                metrics = {
                    'Attendance': get_col_val('Attendance'),
                    'Avg Test Score': student_data.get('Avg Test Score', 0),
                    'Focus (Scaled)': get_col_val('Focus') * 10,
                    'Homework (Scaled)': get_col_val('Homework') * 10,
                    'Q&A (Scaled)': get_col_val('Q&A') * 10,
                    'Exam Prep (Scaled)': get_col_val('Exam Prep') * 10,
                    'Special Problems': get_col_val('Special Problems Completion')
                }
                
                # Filter out any metrics that don't exist in the df
                valid_metrics = {k: v for k, v in metrics.items() if pd.notnull(v)}
                
                if valid_metrics:
                    radar_df = pd.DataFrame(dict(
                        r=list(valid_metrics.values()),
                        theta=list(valid_metrics.keys())
                    ))
                    
                    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0,100], 
                                        color_discrete_sequence=['#00f2fe'])
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 242, 254, 0.2)')
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    # 2nd Graph: Cross-Subject Scoring
                    all_subjects_df = df_smart[df_smart['Name'] == student_data.get('Name', '')].copy()
                    fig_subj = None
                    
                    if not all_subjects_df.empty and 'Subject' in all_subjects_df.columns and 'Avg Test Score' in all_subjects_df.columns:
                        subj_scores = all_subjects_df.groupby('Subject')['Avg Test Score'].mean().reset_index()
                        
                        fig_subj = px.line_polar(subj_scores, r='Avg Test Score', theta='Subject', line_close=True, range_r=[0,100],
                                                 color_discrete_sequence=['#ff007f'])
                        fig_subj.update_traces(fill='toself', fillcolor='rgba(255, 0, 127, 0.2)')
                        fig_subj.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, 100])
                            ),
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white')
                        )
                    
                    col_r1, col_r2, col_r3 = st.columns([1.5, 1.5, 1])
                    with col_r1:
                        st.markdown("**Personal Potential Zones**")
                        st.plotly_chart(fig, use_container_width=True)
                    with col_r2:
                        st.markdown("**Cross-Subject Scores**")
                        if fig_subj:
                            st.plotly_chart(fig_subj, use_container_width=True)
                        else:
                            st.info("No cross-subject data available.")
                    with col_r3:
                        st.write("### Quick Stats")
                        st.write(f"**Class:** {student_data.get('Class', 'N/A')}")
                        st.write(f"**Section:** {student_data.get('Section', 'N/A')}")
                        st.write(f"**Subject:** {student_data.get('Subject', 'N/A')}")
                        st.write(f"**Rank:** {student_data.get('Rank', 'N/A')}")
                        st.write(f"**Engagement Index:** {student_data.get('Engagement Index', 0):.1f}/100")
                        st.info(student_data.get('Intervention', 'On Track'))
                else:
                    st.warning("Insufficient data to plot radar chart.")"""

new_tab2 = """            if not df_download.empty and 'Name' in df_download.columns:
                if 'ID' in df_download.columns:
                    search_options = df_download.apply(lambda row: f"{row['ID']} - {row['Name']}", axis=1).unique().tolist()
                    selected_val = st.selectbox("Search Student (by Name or ID):", options=search_options)
                    selected_id = str(selected_val).split(" - ")[0]
                    all_student_rows = df_smart[df_smart['ID'].astype(str) == selected_id]
                else:
                    student_names = df_download['Name'].unique().tolist()
                    selected_student_name = st.selectbox("Select Student:", options=student_names)
                    all_student_rows = df_smart[df_smart['Name'] == selected_student_name]
                    
                subjects = all_student_rows['Subject'].dropna().unique().tolist()
                subject_options = ['Overall (Average)'] + subjects
                selected_subj = st.selectbox("Select Subject Filter:", options=subject_options)
                
                if selected_subj == 'Overall (Average)':
                    student_data = all_student_rows.select_dtypes(include='number').mean()
                    first_row = all_student_rows.iloc[0]
                    for col in all_student_rows.columns:
                        if col not in student_data.index:
                            student_data[col] = first_row[col]
                    student_data['Subject'] = 'Overall'
                else:
                    student_data = all_student_rows[all_student_rows['Subject'] == selected_subj].iloc[0]
                
                st.markdown("---")
                st.subheader(f"🎯 Detailed View: {student_data.get('Name', 'Unknown')} ({student_data.get('Subject', 'Overall')})")
                
                def get_col_val(keyword, default=0):
                    cols = [c for c in student_data.index if keyword.lower() in c.lower()]
                    if cols:
                        try:
                            val = student_data[cols[0]]
                            return float(val) if pd.notnull(val) and str(val).strip() != "" and str(val).lower() != "n/a" else default
                        except (ValueError, TypeError):
                            return default
                    return default
                    
                metrics = {
                    'Attendance': get_col_val('Attendance'),
                    'Avg Test Score': student_data.get('Avg Test Score', 0),
                    'Focus (Scaled)': get_col_val('Focus') * 10,
                    'Homework (Scaled)': get_col_val('Homework') * 10,
                    'Q&A (Scaled)': get_col_val('Q&A') * 10,
                    'Exam Prep (Scaled)': get_col_val('Exam Prep') * 10,
                    'Special Problems': get_col_val('Special Problems Completion')
                }
                
                valid_metrics = {k: v for k, v in metrics.items() if pd.notnull(v)}
                if valid_metrics:
                    radar_df = pd.DataFrame(dict(
                        r=list(valid_metrics.values()),
                        theta=list(valid_metrics.keys())
                    ))
                    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0,100], color_discrete_sequence=['#00f2fe'])
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 242, 254, 0.2)')
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=80, r=80, t=40, b=40))
                    
                    radar_subjects_df = all_student_rows.copy()
                    fig_subj = None
                    if not radar_subjects_df.empty and 'Subject' in radar_subjects_df.columns and 'Avg Test Score' in radar_subjects_df.columns:
                        subj_scores = radar_subjects_df.groupby('Subject')['Avg Test Score'].mean().reset_index()
                        if len(subj_scores) >= 3:
                            fig_subj = px.line_polar(subj_scores, r='Avg Test Score', theta='Subject', line_close=True, range_r=[0,100], color_discrete_sequence=['#ff007f'])
                            fig_subj.update_traces(fill='toself', fillcolor='rgba(255, 0, 127, 0.2)')
                            fig_subj.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=80, r=80, t=40, b=40))
                        else:
                            fig_subj = px.bar(subj_scores, x='Subject', y='Avg Test Score', range_y=[0,100], color_discrete_sequence=['#ff007f'])
                            fig_subj.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=40, r=40, t=40, b=40))
                    
                    col_r1, col_r2, col_r3 = st.columns([1.5, 1.5, 1])
                    with col_r1:
                        st.markdown("**Personal Potential Zones**")
                        st.plotly_chart(fig, use_container_width=True)
                    with col_r2:
                        st.markdown("**Cross-Subject Scores**")
                        if fig_subj: st.plotly_chart(fig_subj, use_container_width=True)
                        else: st.info("No cross-subject data available.")
                    with col_r3:
                        st.write("### Quick Stats")
                        st.write(f"**Class:** {student_data.get('Class', 'N/A')}")
                        st.write(f"**Section:** {student_data.get('Section', 'N/A')}")
                        st.write(f"**Subject:** {student_data.get('Subject', 'N/A')}")
                        st.write(f"**Rank:** {student_data.get('Rank', 'N/A')}")
                        st.write(f"**Engagement Index:** {student_data.get('Engagement Index', 0):.1f}/100")
                        st.info(student_data.get('Intervention Recommendation', student_data.get('Intervention', 'On Track')))
                        
                    st.markdown("---")
                    st.subheader("📚 All Subjects Breakdown")
                    table_cols = ['Subject', 'Attendance (%)', 'Unit Test 1', 'Unit Test 2', 'Unit Test 3', 'Half Yearly', 'Avg Test Score', 'Engagement Index']
                    avail_table_cols = [c for c in table_cols if c in all_student_rows.columns]
                    st.dataframe(all_student_rows[avail_table_cols], use_container_width=True, hide_index=True)
                    st.markdown("---")
                    
                    all_subjects_df = all_student_rows.copy()
                    st.subheader(f"📋 Comprehensive Academic Profile (Averaged Across {len(all_subjects_df)} Subjects)")
                    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                    numeric_avg = all_subjects_df.select_dtypes(include='number').mean()
                    def get_raw_val(keyword, default="N/A"):
                        cols = [c for c in numeric_avg.index if keyword.lower() in c.lower()]
                        if cols: return f"{numeric_avg[cols[0]]:.1f}" if pd.notnull(numeric_avg[cols[0]]) else default
                        cols = [c for c in student_data.index if keyword.lower() in c.lower()]
                        return student_data[cols[0]] if cols and pd.notnull(student_data[cols[0]]) else default
                        
                    with m_col1:
                        st.metric("Avg Attendance", f"{get_raw_val('Attendance')}%")
                        st.metric("Avg Focus", f"{get_raw_val('Focus')}/10")
                        st.metric("Avg Homework", f"{get_raw_val('Homework')}/10")
                    with m_col2:
                        st.metric("Avg Unit Test 1", f"{get_raw_val('Unit Test 1')}/40")
                        st.metric("Avg Unit Test 2", f"{get_raw_val('Unit Test 2')}/40")
                        st.metric("Avg Unit Test 3", f"{get_raw_val('Unit Test 3')}/40")
                    with m_col3:
                        st.metric("Avg Half Yearly", f"{get_raw_val('Half Yearly')}/100")
                        st.metric("Avg Q&A", f"{get_raw_val('Q&A')}/10")
                        st.metric("Avg Exam Prep", f"{get_raw_val('Exam Prep')}/10")
                    with m_col4:
                        st.metric("Avg Doubt Asking Rate", f"{get_raw_val('Doubt')}")
                        st.metric("Avg Special Problems", f"{get_raw_val('Special Problems')}%")
                        st.metric("Home Tuition", f"{get_raw_val('Home Tuition')}")
                        
                    st.markdown("---")
                    if st.button("✨ Generate AI Action Plan"):
                        api_key = os.getenv("NVIDIA_API_KEY")
                        if not api_key and hasattr(st, "secrets") and "nvidia_api_key" in st.secrets: api_key = st.secrets["nvidia_api_key"]
                        if not api_key: st.error("NVIDIA API Key is missing. Please set NVIDIA_API_KEY in your environment or Streamlit secrets.")
                        else:
                            with st.spinner("Generating personalized AI Action Plan..."):
                                try:
                                    client = openai.OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
                                    prompt = f\"\"\"You are an expert educational AI assistant.
Generate a structured, organized action plan for the student {student_data.get('Name')} (Class {student_data.get('Class')}).
Here are their average metrics across {len(all_subjects_df)} subjects:
Attendance: {get_raw_val('Attendance')}%
Avg Test Score: {get_raw_val('Avg Test Score')}%
Engagement Index: {get_raw_val('Engagement Index')}/100
Intervention Status: {student_data.get('Intervention Recommendation', 'On Track')}

Respond EXACTLY in this format (use emojis and bold text):
🏷️ **Student Profile**
Current Status: [Identify them briefly based on metrics, e.g. "Struggling but Motivated"]
🌟 **Academic Standing**: [Brief comment on scores]

💬 **Home Actions (For Parents)**
- [Action 1: specific to their metrics]
- [Action 2: specific to their metrics]
- [Action 3: specific to their metrics]

🏫 **School Actions (With Teachers)**
- [Action 1: specific to their metrics]
- [Action 2: specific to their metrics]
- [Action 3: specific to their metrics]\"\"\"
                                    response = client.chat.completions.create(
                                        model="meta/llama-3.3-70b-instruct",
                                        messages=[{"role": "user", "content": prompt}],
                                        temperature=0.7, max_tokens=600
                                    )
                                    st.success("Plan Generated Successfully!")
                                    st.markdown(response.choices[0].message.content)
                                except Exception as e: st.error(f"Failed to generate AI plan: {e}")
                else:
                    st.warning("Insufficient data to plot radar chart.")"""
content = content.replace(old_tab2_start, new_tab2)

with open('pages/1_Student_Intelligence.py', 'w') as f:
    f.write(content)
