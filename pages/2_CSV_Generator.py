import streamlit as st
import csv
import random
import os
import pandas as pd

st.set_page_config(page_title="CSV Data Generators", layout="wide")

st.title("🗂️ Synthetic Data Generators")
st.markdown("Generate robust, diverse datasets for testing and analytics pipelines.")

tab1, tab2 = st.tabs(["🎓 Student Performance Dataset", "🔜 Future Generators"])

with tab1:
    st.header("Student Intelligence Synthetic Data")
    st.markdown("Generates a comprehensive school-wide dataset containing randomized student profiles, grades, and engagement metrics.")
    
    st.markdown("### ⚙️ Dynamic Configuration")
    col1, col2 = st.columns(2)
    with col1:
        max_students = st.number_input("Max Students per Section", min_value=1, max_value=500, value=40)
        classes_input = st.text_input("Classes (comma-separated)", value="8, 9, 10, 11, 12")
        junior_sub_input = st.text_input("Junior Subjects (Class <= 10)", value="Maths, Science, Social, English, Hindi, Arts")
    with col2:
        output_filename = st.text_input("Output Filename", value="complete_school_dataset.csv")
        sections_input = st.text_input("Sections (comma-separated)", value="A, B, C")
        senior_sub_input = st.text_input("Senior Subjects (Class > 10)", value="Maths, Physics, Chemistry, Biology, English, Social, Painting")
        
    if st.button("🚀 Generate Student Dataset", type="primary"):
        with st.spinner("Generating complex school hierarchy..."):
            # 1. School Structure Setup (Parsed dynamically from user input)
            classes = [int(c.strip()) for c in classes_input.split(',') if c.strip().isdigit()]
            sections = [s.strip() for s in sections_input.split(',') if s.strip()]
            
            # Subject Pools
            class_10_subjects = [s.strip() for s in junior_sub_input.split(',') if s.strip()]
            high_school_subjects = [s.strip() for s in senior_sub_input.split(',') if s.strip()]
            
            # Names list to pull from randomly (combining first and last names)
            # 80 Unique First Names (Increased 4x)
            first_names = [
                "Rahul", "Priya", "Arjun", "Sneha", "Karan", "Ananya", "Rohan", "Meera", "Aditya", "Neha", 
                "Aman", "Riya", "Dev", "Tanya", "Aarav", "Ishita", "Manav", "Pooja", "Amit", "Kriti",
                "Vikram", "Kavya", "Rohan", "Divya", "Siddharth", "Anjali", "Yash", "Ridhi", "Kabir", "Shreya",
                "Rudra", "Isha", "Gaurav", "Tanvi", "Varun", "Mehak", "Kunwar", "Prisha", "Hrithik", "Nisha",
                "Abhishek", "Aanchal", "Mayank", "Swati", "Rishabh", "Ritu", "Deepak", "Payal", "Sanjay", "Jyoti",
                "Rajesh", "Kiran", "Vijay", "Lata", "Anil", "Suman", "Arun", "Aarti", "Manoj", "Komal",
                "Sameer", "Nupur", "Pranav", "Alka", "Tushar", "Priti", "Vivek", "Sonia", "Alok", "Barkha",
                "Akash", "Kajal", "Sandeep", "Monika", "Pankaj", "Richa", "Saurabh", "Poonam", "Manish", "Sakshi"
                ]

            # 80 Unique Last Names (Increased 4x)
            last_names = [
                "Sharma", "Das", "Mehta", "Roy", "Gupta", "Singh", "Verma", "Iqbal", "Kumar", "Patel", 
                "Joshi", "Sen", "Malhotra", "Kapoor", "Jain", "Bose", "Khanna", "Nair", "Reddy", "Choudhury",
                "Mishra", "Pandey", "Yadav", "Trivedi", "Dwivedi", "Bajpai", "Agrawal", "Bansal", "Goel", "Garg",
                "Saxena", "Srivastava", "Sinha", "Prasad", "Ranjan", "Kashyap", "Thakur", "Chauhan", "Rathore", "Rajput",
                "Chatterjee", "Mukherjee", "Banerjee", "Chakraborty", "Ganguly", "Ghosh", "Sen", "Dutta", "Mitra", "Pal",
                "Kulkarni", "Deshmukh", "Joshi", "Patil", "Pawar", "Gaekwad", "Shinde", "Mahajan", "Nair", "Menon",
                "Pillai", "Iyer", "Iyengar", "Rao", "Murthy", "Naidu", "Chetty", "Balakrishnan", "Acharya", "Bhatt",
                "Gill", "Dhillon", "Sidhu", "Grewal", "Sandhu", "Johal", "Chawla", "Malik", "Bhasin", "Suri"
                ]

            
            # CSV Columns Matching Your Dashboard Schema
            headers = [
                "Class", "Section", "Subject", "Name", "ID", "Roll Number", "Attendance (%)", 
                "Unit Test 1", "Unit Test 2", "Unit Test 3", "Home Tuition (Y/N)", 
                "Focus (0-10)", "Homework (0-10)", "Q&A (0-10)", "Doubt Asking Rate", 
                "Exam Prep (0-10)", "Special Problems Completion (%)"
            ]
            
            all_rows = []
            
            # 2. Loop through the school hierarchy
            for cls in classes:
                for sec in sections:
                    # Loop through student numbers 1 to max_students for this specific section
                    for student_num in range(1, max_students + 1):
                        
                        # Formulate the Name and keep it identical for all this student's subjects
                        student_name = f"{random.choice(first_names)} {random.choice(last_names)}"
                        
                        # ID format: Class_Section_Integer (e.g., 8_A_10)
                        student_id = f"{cls}_{sec}_{student_num}"
                        
                        # Roll Number format based on formula (e.g., 80110 for class 8, section 1, student 10)
                        sec_digit = "01" if sec == 'A' else "02" if sec == 'B' else "03"
                        student_num_padded = f"{student_num:02d}"
                        roll_number = f"{cls}{sec_digit}{student_num_padded}"
                        
                        # Select the correct subject list based on the Class level (<= 10 gets Junior subjects)
                        subjects = class_10_subjects if cls <= 10 else high_school_subjects
                        
                        # Create a row for EACH subject for this unique student
                        for sub in subjects:
                            row = {
                                "Class": cls,
                                "Section": sec,
                                "Subject": sub,
                                "Name": student_name,         # Stays exactly the same
                                "ID": student_id,             # Stays exactly the same
                                "Roll Number": roll_number,   # Stays exactly the same
                                "Attendance (%)": random.randint(65, 100),
                                "Unit Test 1": random.randint(40, 100),
                                "Unit Test 2": random.randint(40, 100),
                                "Unit Test 3": random.randint(40, 100),
                                "Home Tuition (Y/N)": random.choice(['Y', 'N']),
                                "Focus (0-10)": random.randint(3, 10),
                                "Homework (0-10)": random.randint(3, 10),
                                "Q&A (0-10)": random.randint(2, 10),
                                "Doubt Asking Rate": round(random.uniform(0.1, 1.0), 1),
                                "Exam Prep (0-10)": random.randint(3, 10),
                                "Special Problems Completion (%)": random.randint(30, 100)
                            }
                            all_rows.append(row)
            
            # Ensure raw data dir exists
            raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
            os.makedirs(raw_dir, exist_ok=True)
            
            output_path = os.path.join(raw_dir, output_filename)
            
            # 3. Write all generated data rows to a CSV file
            with open(output_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_rows)
                
            st.success(f"🎉 Successfully generated {len(all_rows)} row entries for the entire school!")
            st.info(f"📁 Saved file directly to your system at: `data/raw/{output_filename}`")
            
            # Display sample and provide download
            df = pd.DataFrame(all_rows)
            st.write("### Data Preview")
            st.dataframe(df.head(15), width=None) # width=None replaces the deprecated use_container_width
            
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Generated CSV manually",
                data=csv_data,
                file_name=output_filename,
                mime="text/csv",
            )

with tab2:
    st.info("Additional CSV Generators (e.g. Employee Analytics, E-Commerce Data) can be added here in the future.")
