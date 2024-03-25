import streamlit as st
import os
from utils import HRSearch, JobData, InterviewQuestionGenerator, CandidateData
import pandas as pd
import time

st.set_page_config(layout="wide")


HRSearchObject = HRSearch()
JobDataObject = JobData("data/jd_data.json")
CandidateDataObject = CandidateData("data/candidate_record_list.json")
interview_generator = InterviewQuestionGenerator()


def search_candidates(all_candidates_data):
    # Constructing table header with bold formatting
    table_header = "<thead><tr style='text-align: left;'><th style='font-weight: bold;'>Name</th><th style='font-weight: bold;'>Search&nbsp;Score</th><th style='font-weight: bold;'>Profile Summary</th></tr></thead>"

    # Constructing table body
    table_body = "<tbody>"
    for candidate_data in all_candidates_data:
        table_body += f"<tr><td>{candidate_data['candidate_name']}</td><td style='text-align: center;'>{round(candidate_data['@search.score'], 2)}</td><td>{candidate_data['candidate_summary']}</td></tr>"
    table_body += "</tbody>"

    # Combining table header and body
    table_html = f"<table>{table_header}{table_body}</table>"

    # Displaying table using markdown component
    st.markdown(table_html, unsafe_allow_html=True)


def rank_candidates(all_candidates_data):
    ranked_candidates_info = [
        {
            "Name": candidate_data["candidate_name"],
            "SemanticScore": f"{round(candidate_data['SemanticScore']*100,2)}%",
            "EducationGrade": candidate_data["EducationGrade"],
            "ExperienceGrade": candidate_data["ExperienceGrade"],
            "OverallScore": f'{candidate_data["OverallScore"]}%',
            "Profile Summary": candidate_data["candidate_summary"],
        }
        for candidate_data in all_candidates_data
    ]
    # st.table(ranked_candidates_info)

    # Constructing table header with bold formatting
    table_header = "<thead><tr style='text-align: center;'><th style='font-weight: bold;'>Name</th><th style='font-weight: bold; text-align: center;'>Semantic&nbsp;Score</th><th style='font-weight: bold;'>Education&nbsp;Grade</th><th style='font-weight: bold;'>Experience&nbsp;Grade</th><th style='font-weight: bold;'>Overall&nbsp;Score</th><th style='font-weight: bold;'>Profile Summary</th></tr></thead>"

    # # Constructing table body
    table_body = "<tbody>"
    for candidate_data in ranked_candidates_info:
        table_body += f"<tr><td style='text-align: center;'>{candidate_data['Name']}</td><td style='text-align: center;'>{candidate_data['SemanticScore']}</td><td style='text-align: center;'>{candidate_data['EducationGrade']}</td><td style='text-align: center;'>{candidate_data['ExperienceGrade']}</td><td style='text-align: center;'>{candidate_data['OverallScore']}</td><td style='text-align: left;'>{candidate_data['Profile Summary']}</td></tr>"
    table_body += "</tbody>"

    # Combining table header and body
    table_html = f"<table>{table_header}{table_body}</table>"

    # Displaying table using markdown component
    st.markdown(table_html, unsafe_allow_html=True)


def quiz_questions(JD, CV):
    InterviewQuestionsObject = interview_generator.generate_interview_questions(JD, CV)
    if not InterviewQuestionsObject:
        return None

    multiple_choice_questions = InterviewQuestionsObject[0].multiple_choice_questions
    descriptive_questions = InterviewQuestionsObject[0].descriptive_questions

    # Run the code for valid response
    st.header("Descriptive Questions")
    for i, DescriptiveQuestionObject in enumerate(descriptive_questions, start=1):
        st.write(f"{i}. {DescriptiveQuestionObject.question}")
        st.text_area(f"Answer {i}", height=100)

    st.header("Multiple Choice Questions")
    for i, MultipleChoiceObject in enumerate(multiple_choice_questions, start=1):
        st.radio(
            # Question
            f"{i}. {MultipleChoiceObject.question}",
            # MCQs
            tuple(
                f"{chr(65 + i)}) {item}"
                for i, item in enumerate(MultipleChoiceObject.choices)
            ),
        )


def retrieve_document_path(resume_name):
    # return next(
    #     (r["pdf"] for r in candidate_profiles if r["name"] == resume_name), None
    # )
    return None


def main():
    st.sidebar.title("Main Menu")
    st.sidebar.info(
        "Navigate through the menu to explore different features of the Candidate Management System."
    )

    choice = st.sidebar.selectbox(
        "Choose a feature", ["Home", "Search", "Ranking", "Assessment", "Info"]
    )

    if choice == "Home":
        st.title("Welcome to TalentHub! 🚀")
        st.markdown("""
            This platform assists HR professionals in managing, ranking, and assessing potential job candidates effectively.
            
            **Select a feature from the sidebar** to start exploring:
            - **Search**: Find candidates by keywords.
            - **Ranking**: View candidates ranked by their qualifications.
            - **Assessment**: Conduct assessments and download resumes.
            - **Info**: Learn more about this tool.
            """)
        image_url = "https://fjwp.s3.amazonaws.com/blog/wp-content/uploads/2019/11/29144739/HR-career-1024x512.png"
        st.image(image_url, caption="Empower Your HR Process", use_column_width=True)

    elif choice == "Search":
        st.title("🔍 Candidate Search")
        st.markdown(
            "Find the perfect candidate by searching with keywords related to skills, experience, or other criteria."
        )
        search_term = st.text_input(
            "Enter a keyword to start the search:", placeholder="Sales and Marketing"
        )
        if search_term:
            all_candidates_data = HRSearchObject.full_text_search(search_term)
            st.subheader(f"Results for '{search_term}':")
            search_candidates(all_candidates_data)

    elif choice == "Ranking":
        st.title("📊 Candidate Ranking")
        st.markdown(
            "Rank candidates based on their scores to easily identify the top talents."
        )
        job_positions = JobDataObject.get_positions()
        job_position = st.selectbox("Choose a category to filter by:", job_positions)

        job_position_record = JobDataObject.get_record_by_position(job_position)
        st.markdown(f"**Experience:** {job_position_record['Experience']}")
        # st.markdown(f"**Roles & Responsibilities:** {job_position_record['Roles & Responsibilities']}")

        all_candidates_data = HRSearchObject.search_candidates_by_job_description(
            jd_id=job_position_record["JD_ID"]
        )
        rank_candidates(all_candidates_data)

    elif choice == "Assessment":
        # st.title("Candidate Assessment")
        st.title("📝 Candidate Assessment")
        st.markdown(
            "Select a candidate to view their detailed profile, download resumes, and assess their fit for the role."
        )
        job_positions = JobDataObject.get_positions()
        candidate_name_dict = CandidateDataObject.get_candidate_names()

        selected_profile = st.selectbox(
            "Select a Job Profile:",
            job_positions,
        )
        selected_candidate = st.selectbox(
            "Select a candidate Profile:", candidate_name_dict.keys()
        )

        if selected_candidate and selected_profile:
            document_path = retrieve_document_path(selected_candidate)
            if document_path:
                with open(document_path, "rb") as file:
                    st.download_button(
                        "Download Resume",
                        file,
                        file_name=document_path,
                        mime="application/pdf",
                    )
        # Create a Streamlit button
        if (
            st.button("Generate Assessment!")
            and selected_candidate
            and selected_profile
        ):
            CandidateRecord = CandidateDataObject.get_record_by_id(
                candidate_id=candidate_name_dict[selected_candidate]
            )
            JDRecord = JobDataObject.get_record_by_position(position=selected_profile)
            JD = JDRecord["JD_Content"]
            CV = CandidateRecord["MD_Content"]
            with st.spinner("Wait for it..."):
                quiz_questions(JD, CV)

    elif choice == "Info":
        st.title("📘 About This System")
        st.markdown("""
            This Candidate Management System is a comprehensive tool designed to optimize the recruitment process.
            
            Features include:
            - Searching for candidates by keywords.
            - Ranking candidates based on their skills and experience.
            - Assessing candidates through interactive quizzes and detailed profiles.
            
            Developed to streamline your HR tasks and enhance the recruitment workflow.
            """)


if __name__ == "__main__":
    main()
