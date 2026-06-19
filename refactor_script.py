import re

with open("pages/1_Student_Intelligence.py", "r") as f:
    content = f.read()

# 1. Add st.tabs
old_header = 'st.header("📊 Executive Dashboard")'
new_header = '''tab1, tab2 = st.tabs(["📊 Classroom Overview", "👤 Individual Student Deep-Dive"])
        with tab1:
            st.header("📊 Executive Dashboard")'''

content = content.replace(old_header, new_header)

# 2. Indent everything from col1 to st.divider() under tab1
# It's easier to just indent the entire block until the end, then split tab2 out.
lines = content.split('\n')
in_overview = False
for i, line in enumerate(lines):
    if line.strip() == 'st.header("📊 Executive Dashboard")':
        in_overview = True
    elif in_overview and line.strip() == 'st.markdown("**Select a student row below to view their detailed performance radar (Circular Potential Zones):**")':
        in_overview = False
    elif in_overview:
        if line.startswith('        '):
            lines[i] = '    ' + line

content = '\n'.join(lines)

# 3. Inject tab2 logic at the place where student selection happens
old_selection = '''        st.markdown("**Select a student row below to view their detailed performance radar (Circular Potential Zones):**")
        
        event = st.dataframe(
            df_download, 
            use_container_width=True, 
            selection_mode="single-row", 
            on_select="rerun", 
            key="student_selection"
        )
        
        selected_rows = getattr(event, 'selection', event).rows if hasattr(getattr(event, 'selection', event), 'rows') else event.selection.rows # type: ignore
        if selected_rows:
            selected_idx = selected_rows[0]
            if selected_idx < len(df_download):
                student_data = df_download.iloc[selected_idx]'''

new_selection = '''        with tab2:
            st.header("👤 Individual Student Deep-Dive")
            if not df_download.empty and 'Name' in df_download.columns:
                student_names = df_download['Name'].unique().tolist()
                selected_student_name = st.selectbox("Select Student:", options=student_names)
                student_data = df_download[df_download['Name'] == selected_student_name].iloc[0]'''

content = content.replace(old_selection, new_selection)

# 4. Outdent the deep dive logic by one level since it was nested under `if selected_rows:`
# We can just leave it as is or fix the indentation. Since it was indented 4 levels (16 spaces), 
# now it's under `with tab2:` (12 spaces) -> wait, `student_data = ...` is 16 spaces. So the existing 16 space indentation for `st.markdown("---")` works perfectly!

with open("pages/1_Student_Intelligence.py", "w") as f:
    f.write(content)

