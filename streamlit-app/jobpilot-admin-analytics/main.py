
# -----------------------------
# JobPilot Authentication
# -----------------------------

import streamlit as st
import streamlit_authenticator as stauth

from auth_db import (
    init_auth_db,
    register_user,
    login_user,
    list_users,
    set_user_role,
)

from user_data_db import (
    init_user_data_db,
    save_user_item,
    get_user_items,
)

init_auth_db()
init_user_data_db()


# Replace this hash with the hash generated for your password
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": "$2b$12$REPLACE_WITH_YOUR_HASH"
        }
    }
}


authenticator = stauth.Authenticate(
    credentials,
    "jobpilot_auth_cookie",
    "jobpilot_auth_signature",
    cookie_expiry_days=7,
)


name, authentication_status, username = authenticator.login(
    location="main"
)


if authentication_status is False:
    st.error("Username or password is incorrect.")
    st.stop()


if authentication_status is None:
    st.warning("Please enter your username and password.")
    st.stop()


if authentication_status:
    authenticator.logout(
        "Logout",
        "sidebar",
    )

    st.sidebar.success(f"Logged in: {name}")

    # Your dashboard code continues below


# --- User-specific data page ---
with st.sidebar.expander("My Personal Data"):
    st.caption("Your saved items are linked to your account.")
    personal_kind = st.selectbox("Content type", ["note", "resume", "application", "interview"])
    personal_title = st.text_input("Title", key="personal_title")
    personal_content = st.text_area("Content", key="personal_content")
    if st.button("Save personal content"):
        if personal_title.strip():
            save_user_item(st.session_state.jp_user["id"], personal_kind, personal_title, personal_content)
            st.success("Saved to your account.")
        else:
            st.warning("Enter a title.")
    st.divider()
    st.write("Your saved content")
    items = get_user_items(st.session_state.jp_user["id"])
    if items:
        for item in items[:10]:
            st.markdown(f"**{item['title']}**  \n`{item['item_type']}`")
            if item["content"]:
                st.caption(item["content"][:180])
    else:
        st.caption("No saved content yet.")
# --- End user-specific data page ---



from utils.document_generator import create_docx_file
from ai.job_application_service import (
    generate_resume_recommendations,
    generate_tailored_resume,
    generate_cover_letter,
)
from ai.resume_improver import (
    improve_resume_for_job,
)
from ai.llm_service import (
    generate_ai_interview_questions,
    generate_model_answer,
)
import streamlit as st
import os
import time
from automation.agent_runner import discover_and_match, load_jobs, export_jobs_csv

from pathlib import Path

from services.interview_service import (
    save_interview_question,
    get_interview_questions,
    update_interview_answer,
    delete_interview_question,
)

from ai.interview_generator import (
    generate_interview_questions,
)

from services.resume_service import (
    save_resume_version,
    get_all_resume_versions,
)

from ai.job_matcher import (
    calculate_match_score,
)

from ai.skill_analyzer import (
    analyze_skill_gap,
)

from ai.job_ranker import (
    calculate_job_priority,
)

from services.job_service import (
    save_job,
    get_all_jobs,
)

from services.application_service import (
    save_application,
    get_all_applications,
    update_application_status,
    delete_application,
)




BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "resumes").mkdir(exist_ok=True)
(DATA_DIR / "jobs").mkdir(exist_ok=True)
(DATA_DIR / "applications").mkdir(exist_ok=True)


st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🚀",
    layout="wide",
)
 
# --- JobPilot visual system ---
st.markdown("""
<style>
/* ---------- JobPilot accessible light theme ---------- */
:root {
    --jp-bg: #f4f7fb;
    --jp-surface: #ffffff;
    --jp-border: #d9e2ef;
    --jp-text: #172033;
    --jp-muted: #52627a;
    --jp-primary: #2563eb;
    --jp-primary-dark: #1d4ed8;
}

[data-testid="stAppViewContainer"] {
    background: var(--jp-bg);
    color: var(--jp-text);
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Make all normal text readable on white surfaces */
.stMarkdown, .stMarkdown p, .stMarkdown li,
.stText, .stCaption, label, p, li, span,
[data-testid="stText"], [data-testid="stCaption"] {
    color: var(--jp-text);
}
small, .stCaption, [data-testid="stCaption"] {
    color: var(--jp-muted) !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #10213f !important;
    letter-spacing: -0.03em;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102044 0%, #1e3a8a 100%);
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #dbeafe !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 9px 12px;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.12);
}

/* Inputs and dropdowns: dark text on light controls */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #172033 !important;
    border-color: #cbd5e1 !important;
}
input, textarea {
    color: #172033 !important;
    caret-color: #2563eb !important;
}
input::placeholder, textarea::placeholder {
    color: #718096 !important;
    opacity: 1 !important;
}
div[data-baseweb="select"] * {
    color: #172033 !important;
}
ul[role="listbox"], li[role="option"] {
    background: #ffffff !important;
    color: #172033 !important;
}
li[role="option"]:hover {
    background: #eaf2ff !important;
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #1d4ed8 !important;
    border-radius: 10px;
    font-weight: 700;
    min-height: 2.5rem;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #1d4ed8 !important;
    color: #ffffff !important;
}
.stButton > button p, .stFormSubmitButton > button p {
    color: #ffffff !important;
}

/* Cards and metrics */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--jp-border);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 16px rgba(15,23,42,.05);
}
[data-testid="stMetricLabel"] {
    color: #52627a !important;
    font-weight: 700;
}
[data-testid="stMetricValue"] {
    color: #10213f !important;
}
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* Alerts, expanders and containers */
[data-testid="stAlert"] p,
[data-testid="stExpander"] p,
[data-testid="stExpander"] label {
    color: #172033 !important;
}
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #d9e2ef;
    border-radius: 12px;
}

/* Hero */
.jp-hero {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5);
    color: #ffffff;
    padding: 28px 32px;
    border-radius: 20px;
    margin-bottom: 24px;
    box-shadow: 0 12px 30px rgba(37,99,235,.18);
}
.jp-hero h1 { color: #ffffff !important; margin: 0; font-size: 2.1rem; }
.jp-hero p { color: #e0e7ff !important; margin: .5rem 0 0; font-size: 1.05rem; }

/* Links and code */
a { color: #1d4ed8 !important; font-weight: 600; }
code {
    color: #1e3a8a !important;
    background: #eaf2ff !important;
    border-radius: 5px;
    padding: 2px 5px;
}
</style>
""", unsafe_allow_html=True)

# Safe session-state initialization
for key in [
    "resume_recommendation",
    "tailored_resume",
    "cover_letter",
    "resume_improvement_result",
]:
    if key not in st.session_state:
        st.session_state[key] = ""


st.markdown("""
<div class="jp-hero">
  <h1>🚀 JobPilot AI</h1>
  <p>Your intelligent workspace for discovering jobs, tailoring resumes, tracking applications, and preparing for interviews.</p>
</div>
""", unsafe_allow_html=True)


# Sidebar Navigation
st.sidebar.title("JobPilot AI")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Resume Library",
        "Find Jobs",
        "Automatic Job Search",
        "Applications",
        "Interview Preparation",
        "Resume Improvement",
        "Job Application",
    ] + (["Admin Dashboard"] if st.session_state.jp_user.get("role") == "admin" else []),
)

if page == "Admin Dashboard":
    st.title("🛡️ Admin Dashboard")
    st.caption("Manage users, application access, and platform analytics. Admin actions are restricted to admin accounts.")

    # ---------------- Admin analytics ----------------
    st.subheader("📈 Platform Analytics")
    try:
        from app.database import (
            SessionLocal,
            ResumeVersion,
            Job,
            Application,
            InterviewPreparation,
        )

        with SessionLocal() as analytics_db:
            total_resumes = analytics_db.query(ResumeVersion).count()
            total_jobs = analytics_db.query(Job).count()
            total_applications = analytics_db.query(Application).count()
            total_interviews = analytics_db.query(InterviewPreparation).count()

        users = list_users()
        total_users = len(users)

        metric_cols = st.columns(5)
        metric_cols[0].metric("Registered users", total_users)
        metric_cols[1].metric("Resumes", total_resumes)
        metric_cols[2].metric("Jobs", total_jobs)
        metric_cols[3].metric("Applications", total_applications)
        metric_cols[4].metric("Interview prep", total_interviews)

        st.divider()
        st.subheader("👥 User Overview")
        if users:
            admin_count = sum(1 for user in users if user.get("role") == "admin")
            regular_count = total_users - admin_count
            st.write(f"**Admins:** {admin_count}  |  **Regular users:** {regular_count}")
            st.dataframe(users, use_container_width=True, hide_index=True)
        else:
            st.info("No registered users found.")

    except Exception as exc:
        st.error(f"Unable to load platform analytics: {exc}")

    st.divider()
    st.subheader("🔐 Change user role")
    users = list_users()
    if users:
        labels = {f"{u['name']} — {u['email']}": u for u in users}
        selected = st.selectbox("User", list(labels), key="admin_selected_user")
        target = labels[selected]
        new_role = st.selectbox(
            "Role",
            ["user", "admin"],
            index=0 if target.get("role", "user") == "user" else 1,
            key="admin_selected_role"
        )
        if st.button("Save role"):
            if target["id"] == st.session_state.jp_user["id"] and new_role != "admin":
                st.error("You cannot remove your own admin access from this screen.")
            else:
                set_user_role(target["id"], new_role)
                st.success("Role updated. The user must log in again to refresh their session role.")
                st.rerun()
if page == "Dashboard":
    
    st.title("📊 JobPilot AI Dashboard")

    st.write(
        "Track your job applications and interview preparation progress."
    )

    applications = get_all_applications()

    total_applications = len(applications)

    applied_count = sum(
        1
        for application in applications
        if application.status == "Applied"
    )

    assessment_count = sum(
        1
        for application in applications
        if application.status == "Assessment"
    )

    interview_count = sum(
        1
        for application in applications
        if application.status == "Interview"
    )

    selected_count = sum(
        1
        for application in applications
        if application.status == "Selected"
    )

    rejected_count = sum(
        1
        for application in applications
        if application.status == "Rejected"
    )

    withdrawn_count = sum(
        1
        for application in applications
        if application.status == "Withdrawn"
    )

    total_questions = 0
    completed_questions = 0
    in_progress_questions = 0

    for application in applications:

        questions = get_interview_questions(
            application_id=application.id
        )

        total_questions += len(questions)

        completed_questions += sum(
            1
            for question in questions
            if question.preparation_status
            == "Completed"
        )

        in_progress_questions += sum(
            1
            for question in questions
            if question.preparation_status
            == "In Progress"
        )

    st.subheader("📌 Application Overview")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Applications",
            total_applications,
        )

    with col2:

        st.metric(
            "Interview Calls",
            interview_count,
        )

    with col3:

        st.metric(
            "Selected",
            selected_count,
        )
        
    success_rate = 0

    if total_applications > 0:

        success_rate = round(
            (
                selected_count
                / total_applications
            ) * 100,
            2,
        )
    col7, col8 = st.columns(2)

    with col7:

        st.metric(
            "Success Rate",
            f"{success_rate}%",
        )

    with col8:

        st.metric(
            "Rejected Applications",
            rejected_count,
    )

    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "Applied",
            applied_count,
        )

    with col5:

        st.metric(
            "Assessment",
            assessment_count,
        )

    with col6:

        st.metric(
            "Rejected",
            rejected_count,
        )

    st.divider()

    st.subheader("📈 Application Status")

    status_data = {
        "Status": [
            "Applied",
            "Assessment",
            "Interview",
            "Selected",
            "Rejected",
            "Withdrawn",
        ],
        "Count": [
            applied_count,
            assessment_count,
            interview_count,
            selected_count,
            rejected_count,
            withdrawn_count,
        ],
    }

    st.bar_chart(
        status_data,
        x="Status",
        y="Count",
    )

    st.divider()

    st.subheader("🎯 Interview Preparation Progress")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Questions",
            total_questions,
        )

    with col2:

        st.metric(
            "In Progress",
            in_progress_questions,
        )

    with col3:

        st.metric(
            "Completed",
            completed_questions,
        )

    if total_questions > 0:

        preparation_progress = (
            completed_questions / total_questions
        )

        st.progress(
            preparation_progress
        )

        st.write(
            f"Preparation Progress: "
            f"{round(preparation_progress * 100, 2)}%"
        )

    else:

        st.info(
            "Generate interview questions to start preparation."
        )

    st.divider()

    st.subheader("📝 Recent Applications")

    if not applications:

        st.info(
            "No applications found."
        )

    else:

        recent_applications = applications[:5]

        for application in recent_applications:

            st.write(
                f"**{application.company_name}** - "
                f"{application.job_title}"
            )

            st.write(
                f"Status: `{application.status}`"
            )

            st.write(
                f"Resume Used: "
                f"{application.resume_version_name}"
            )

            st.divider()


elif page == "Resume Library":

    st.header("📄 Resume Library")

    st.write(
        "Upload and preserve every resume version "
        "used during job applications."
    )

    st.subheader("Upload New Resume")

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"],
    )

    if uploaded_file is not None:

        version_name = st.text_input(
            "Resume Version Name",
            placeholder=(
                "Example: Data Analyst Resume - SQL Focus"
            ),
        )

        notes = st.text_area(
            "Notes",
            placeholder=(
                "Example: Used for Data Analyst applications"
            ),
        )

        if st.button("Save Resume Version"):

            if not version_name.strip():

                st.error(
                    "Please enter a resume version name."
                )

            else:

                resume = save_resume_version(
                    uploaded_file=uploaded_file,
                    version_name=version_name,
                    notes=notes,
                )

                st.success(
                    f"Resume saved successfully: "
                    f"Version ID {resume.id}"
                )

                st.rerun()

    st.divider()

    st.subheader("Saved Resume Versions")

    resumes = get_all_resume_versions()

    if not resumes:

        st.warning(
            "No resume versions saved yet."
        )

    else:

        for resume in resumes:

            with st.expander(
                f"Version {resume.id}: "
                f"{resume.version_name}"
            ):

                st.write(
                    f"**Original file:** "
                    f"{resume.original_filename}"
                )

                st.write(
                    f"**File type:** "
                    f"{resume.file_type}"
                )

                st.write(
                    f"**Created at:** "
                    f"{resume.created_at}"
                )

                if resume.notes:

                    st.write(
                        f"**Notes:** {resume.notes}"
                    )

                st.divider()

                st.subheader(
                    "Extracted Resume Text"
                )

                if resume.resume_text:

                    st.text_area(
                        "Resume Content",
                        value=resume.resume_text,
                        height=300,
                        key=f"resume_text_{resume.id}",
                    )

                else:

                    st.warning(
                        "No extracted text available."
                    )

                st.divider()

                file_path = Path(
                    resume.stored_file_path
                )

                if file_path.exists():

                    with open(
                        file_path,
                        "rb",
                    ) as file:

                        file_bytes = file.read()

                    st.download_button(
                        label=(
                            "Download Exact Submitted Resume"
                        ),
                        data=file_bytes,
                        file_name=(
                            resume.original_filename
                        ),
                        mime="application/octet-stream",
                        key=f"download_resume_{resume.id}",
                    )

                else:

                    st.error(
                        "Original resume file not found."
                    )   


elif page == "Automatic Job Search":
    st.title("🤖 Automatic Job Search")
    st.caption("Automatically discover, rank, save and refresh relevant jobs.")

    st.sidebar.subheader("Automatic Search Settings")
    auto_enabled = st.sidebar.checkbox("Enable automatic refresh", value=False)
    refresh_minutes = st.sidebar.number_input(
        "Refresh interval (minutes)", min_value=15, max_value=1440, value=60, step=15
    )
    roles = st.text_input(
        "Job roles (comma separated)",
        value="Data Analyst, Business Analyst, Salesforce Developer"
    )
    location = st.text_input("Location", value="India / Remote")
    limit = st.slider("Maximum jobs to collect", 10, 100, 50)
    resume_text = st.text_area(
        "Paste your resume text once for matching",
        height=180,
        placeholder="Paste your resume content here..."
    )

    if "auto_last_run" not in st.session_state:
        st.session_state.auto_last_run = 0.0

    now = time.time()
    due = now - st.session_state.auto_last_run >= refresh_minutes * 60
    run_now = st.button("🔎 Search Jobs Now", type="primary")

    if auto_enabled and due:
        run_now = True

    if run_now:
        if not resume_text.strip():
            st.warning("Paste your resume text before starting automatic search.")
        else:
            with st.spinner("Finding and matching jobs..."):
                rows = discover_and_match(
                    resume_text,
                    [r.strip() for r in roles.split(",") if r.strip()],
                    location,
                    limit,
                )
            st.session_state.auto_last_run = time.time()
            st.success(f"Found and processed {len(rows)} jobs.")
            if rows:
                st.dataframe(rows, use_container_width=True)
            else:
                st.info(
                    "No jobs returned. Configure an authorized provider in .env "
                    "using JOB_SEARCH_API_URL and JOB_SEARCH_API_KEY."
                )

    st.subheader("💾 Saved / Discovered Jobs")
    saved = load_jobs()
    if saved:
        st.dataframe(saved, use_container_width=True)
        csv_path = export_jobs_csv()
        with open(csv_path, "rb") as f:
            st.download_button(
                "Download saved jobs CSV",
                f,
                file_name="job_matches.csv",
                mime="text/csv",
            )
    else:
        st.info("No saved jobs yet. Start a search above.")

    if auto_enabled:
        st.info(
            f"Automatic refresh is enabled. Keep this app running; the next refresh "
            f"is due after approximately {refresh_minutes} minutes."
        )

elif page == "Find Jobs":
    
    st.header("🔎 Find Jobs")

    st.write(
        "Save job descriptions manually for now. "
        "Automatic job discovery will be added later."
    )

    st.subheader("Add New Job")

    with st.form("add_job_form"):

        company_name = st.text_input(
            "Company Name"
        )

        job_title = st.text_input(
            "Job Title"
        )

        job_url = st.text_input(
            "Job URL"
        )

        location = st.text_input(
            "Location",
            placeholder="Remote / Pune / Bengaluru",
        )

        employment_type = st.selectbox(
            "Employment Type",
            [
                "Full-time",
                "Part-time",
                "Internship",
                "Contract",
                "Unknown",
            ],
        )

        source = st.selectbox(
            "Job Source",
            [
                "LinkedIn",
                "Naukri",
                "Indeed",
                "Company Website",
                "Other",
            ],
        )

        job_description = st.text_area(
            "Job Description",
            height=300,
        )

        submitted = st.form_submit_button(
            "Save Job"
        )

        if submitted:

            if not company_name.strip():

                st.error(
                    "Company name is required."
                )

            elif not job_title.strip():

                st.error(
                    "Job title is required."
                )

            elif not job_description.strip():

                st.error(
                    "Job description is required."
                )

            else:

                job = save_job(
                    company_name=company_name,
                    job_title=job_title,
                    job_url=job_url,
                    location=location,
                    employment_type=employment_type,
                    job_description=job_description,
                    source=source,
                )

                st.success(
                    f"Job saved successfully. "
                    f"Job ID: {job.id}"
                )

                st.rerun()

    st.divider()

    st.subheader("Saved Jobs")

    jobs = get_all_jobs()
    
    st.divider()

    st.subheader(
        "📊 Rank Jobs Against Your Resume"
    )

    if not jobs:

        st.info(
            "No saved jobs available for ranking."
        )

    else:

        resumes = get_all_resume_versions()

        if not resumes:

            st.warning(
                "Please upload a resume first."
            )

        else:

            resume_options = {
                f"Version {resume.id}: "
                f"{resume.version_name}": resume
                for resume in resumes
            }

            selected_resume_label = st.selectbox(
                "Select Resume for Job Ranking",
                options=list(
                    resume_options.keys()
                ),
                key="ranking_resume_selector",
            )

            selected_resume = resume_options[
                selected_resume_label
            ]

            if st.button(
                "Rank All Saved Jobs",
                key="rank_all_jobs_button",
            ):

                if not selected_resume.resume_text:

                    st.error(
                        "Selected resume has no extracted text."
                    )

                else:

                    ranking_results = []

                    for job in jobs:

                        result = calculate_job_priority(
                            resume_text=selected_resume.resume_text,
                            job_description=job.job_description,
                        )

                        ranking_results.append(
                            {
                                "Job ID": job.id,
                                "Company": job.company_name,
                                "Job Title": job.job_title,
                                "Location": job.location or "Not specified",
                                "Text Match": result[
                                    "text_match_score"
                                ],
                                "Skill Coverage": result[
                                    "skill_coverage"
                                ],
                                "Priority Score": result[
                                    "priority_score"
                                ],
                            }
                        )

                    ranking_results.sort(
                        key=lambda item: item[
                            "Priority Score"
                        ],
                        reverse=True,
                    )

                    st.session_state[
                        "ranking_results"
                    ] = ranking_results

            if (
                "ranking_results"
                in st.session_state
            ):

                st.subheader(
                    "🏆 Job Ranking Results"
                )

                st.dataframe(
                    st.session_state[
                        "ranking_results"
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "Priority Score = "
                    "40% text match + 60% skill coverage"
                )
    
    
    

    if not jobs:

        st.info(
            "No jobs saved yet."
        )

    else:

        for job in jobs:

            with st.expander(
                f"Job {job.id}: "
                f"{job.job_title} - "
                f"{job.company_name}"
            ):

                st.write(
                    f"**Company:** "
                    f"{job.company_name}"
                )

                st.write(
                    f"**Title:** "
                    f"{job.job_title}"
                )

                st.write(
                    f"**Location:** "
                    f"{job.location or 'Not specified'}"
                )

                st.write(
                    f"**Employment Type:** "
                    f"{job.employment_type}"
                )

                st.write(
                    f"**Source:** "
                    f"{job.source}"
                )

                if job.job_url:

                    st.write(
                        f"**Job URL:** "
                        f"{job.job_url}"
                    )

                st.write(
                    f"**Created at:** "
                    f"{job.created_at}"
                )

                st.subheader(
                    "Job Description"
                )

                st.text_area(
                    "Description",
                    value=job.job_description,
                    height=300,
                    key=f"job_description_{job.id}",
                )
                st.divider()

                st.subheader(
                    "Resume Match"
                )

                resumes = get_all_resume_versions()

                if not resumes:

                    st.warning(
                        "Please upload a resume first."
                    )

                else:

                    resume_options = {
                        f"Version {resume.id}: "
                        f"{resume.version_name}": resume
                        for resume in resumes
                    }

                    selected_resume_label = st.selectbox(
                        "Choose Resume Version",
                        options=list(
                            resume_options.keys()
                        ),
                        key=f"resume_selector_{job.id}",
                    )

                    selected_resume = resume_options[
                        selected_resume_label
                    ]

                    if not selected_resume.resume_text:

                        st.warning(
                            "Selected resume has no extracted text."
                        )

                    else:

                        if st.button(
                            "Calculate Resume Match",
                            key=f"match_button_{job.id}",
                        ):

                            score = calculate_match_score(
                                resume_text=selected_resume.resume_text,
                                job_description=job.job_description,
                            )

                            st.metric(
                                label="Resume–Job Match Score",
                                value=f"{score}%",
                            )
                            
                            st.divider()

                            st.subheader(
                                "Skill Gap Analysis"
                            )

                            skill_result = analyze_skill_gap(
                                resume_text=selected_resume.resume_text,
                                job_description=job.job_description,
                            )

                            st.metric(
                                label="Skill Coverage",
                                value=(
                                    f'{skill_result["coverage_score"]}%'
                                ),
                            )

                            col1, col2 = st.columns(2)

                            with col1:

                                st.write(
                                    "**Matched Skills**"
                                )

                                if skill_result["matched_skills"]:

                                    for skill in skill_result[
                                        "matched_skills"
                                    ]:

                                        st.success(
                                            skill
                                        )

                                else:

                                    st.info(
                                        "No matched skills found."
                                    )

                            with col2:

                                st.write(
                                    "**Missing Skills**"
                                )

                                if skill_result["missing_skills"]:

                                    for skill in skill_result[
                                        "missing_skills"
                                    ]:

                                        st.warning(
                                            skill
                                        )

                                else:

                                    st.success(
                                        "No missing skills detected."
                                    )

                            if score >= 70:

                                st.success(
                                    "Strong text similarity."
                                )

                            elif score >= 40:

                                st.warning(
                                    "Moderate text similarity."
                                )

                            else:

                                st.error(
                                    "Low text similarity."
                                )
                            


elif page == "Applications":
    
    st.title("📨 Applications")

    st.write(
        "Track your job applications and the exact resume version used."
    )

    jobs = get_all_jobs()
    resumes = get_all_resume_versions()
    applications = get_all_applications()

    st.divider()

    st.subheader("➕ Add New Application")

    if not jobs:
        st.warning(
            "Please save at least one job in the Find Jobs page first."
        )

    elif not resumes:
        st.warning(
            "Please upload at least one resume in the Resume Library first."
        )

    else:

        job_options = {
            f"{job.company_name} - {job.job_title}": job
            for job in jobs
        }

        resume_options = {
            f"Version {resume.id}: {resume.version_name}": resume
            for resume in resumes
        }

        with st.form("application_form"):

            selected_job_label = st.selectbox(
                "Select Job",
                options=list(job_options.keys()),
            )

            selected_resume_label = st.selectbox(
                "Select Resume Version Used",
                options=list(resume_options.keys()),
            )

            application_status = st.selectbox(
                "Application Status",
                options=[
                    "Applied",
                    "Assessment",
                    "Interview",
                    "Selected",
                    "Rejected",
                    "Withdrawn",
                ],
            )

            application_notes = st.text_area(
                "Application Notes",
                placeholder=(
                    "Add referral details, preparation notes, "
                    "HR details, etc."
                ),
            )

            submit_application = st.form_submit_button(
                "Save Application"
            )

            if submit_application:

                selected_job = job_options[
                    selected_job_label
                ]

                selected_resume = resume_options[
                    selected_resume_label
                ]

                save_application(
                    company_name=selected_job.company_name,
                    job_title=selected_job.job_title,
                    job_id=selected_job.id,
                    resume_version_id=selected_resume.id,
                    resume_version_name=selected_resume.version_name,
                    resume_file_path=selected_resume.stored_file_path,
                    status=application_status,
                    job_url=selected_job.job_url or "",
                    notes=application_notes,
                )

                st.success(
                    "Application saved successfully!"
                )

                st.rerun()

    st.divider()

    st.subheader("📋 Application Tracker")

    if not applications:

        st.info(
            "No applications added yet."
        )

    else:

        for application in applications:

            with st.expander(
                f"{application.company_name} - "
                f"{application.job_title} "
                f"[{application.status}]"
            ):

                st.write(
                    f"**Company:** {application.company_name}"
                )

                st.write(
                    f"**Job Title:** {application.job_title}"
                )

                st.write(
                    f"**Applied On:** "
                    f"{application.application_date.strftime('%d %b %Y')}"
                )

                st.write(
                    f"**Resume Used:** "
                    f"{application.resume_version_name}"
                )

                st.write(
                    f"**Resume File:** "
                    f"{application.resume_file_path}"
                )

                if application.job_url:

                    st.markdown(
                        f"[Open Job Posting]({application.job_url})"
                    )

                st.write("**Update Status**")

                status_options = [
                    "Applied",
                    "Assessment",
                    "Interview",
                    "Selected",
                    "Rejected",
                    "Withdrawn",
                ]

                current_status_index = status_options.index(
                    application.status
                )

                new_status = st.selectbox(
                    "Application Status",
                    options=status_options,
                    index=current_status_index,
                    key=f"status_{application.id}",
                )

                if st.button(
                    "Update Status",
                    key=f"update_status_{application.id}",
                ):

                    update_application_status(
                        application_id=application.id,
                        new_status=new_status,
                    )

                    st.success(
                        "Application status updated."
                    )

                    st.rerun()

                if application.notes:

                    st.write("**Notes:**")
                    st.write(application.notes)

                if st.button(
                    "Delete Application",
                    key=f"delete_application_{application.id}",
                ):

                    delete_application(
                        application_id=application.id
                    )

                    st.success(
                        "Application deleted."
                    )

                    st.rerun()


elif page == "Interview Preparation":

    st.title("🎯 Interview Preparation")

    st.write(
        "Prepare for interviews using the exact resume "
        "and job description connected to your application."
    )

    applications = get_all_applications()

    if not applications:

        st.warning(
            "Please create an application first."
        )

    else:

        application_options = {
            f"{application.company_name} - "
            f"{application.job_title} - "
            f"{application.status}": application
            for application in applications
        }

        selected_application_label = st.selectbox(
            "Select Application",
            options=list(application_options.keys()),
            key="interview_application_selector",
        )

        selected_application = application_options[
            selected_application_label
        ]

        st.divider()

        st.subheader("📌 Application Details")

        st.write(
            f"**Company:** "
            f"{selected_application.company_name}"
        )

        st.write(
            f"**Job Title:** "
            f"{selected_application.job_title}"
        )

        st.write(
            f"**Application Status:** "
            f"{selected_application.status}"
        )

        st.write(
            f"**Resume Version Used:** "
            f"{selected_application.resume_version_name}"
        )

        st.write(
            f"**Exact Resume File:** "
            f"{selected_application.resume_file_path}"
        )

        st.divider()

        st.subheader("📄 Job Description")

        selected_job = None

        jobs = get_all_jobs()

        for job in jobs:

            if job.id == selected_application.job_id:

                selected_job = job
                break

        if selected_job:

            st.text_area(
                "Job Description",
                value=selected_job.job_description,
                height=250,
                disabled=True,
                key=f"interview_job_description_{selected_application.id}",
            )

        else:

            st.error(
                "Linked job could not be found."
            )

        st.divider()

        st.subheader("🧠 Resume Skill Analysis")

        selected_resume = None

        resumes = get_all_resume_versions()

        for resume in resumes:

            if resume.id == selected_application.resume_version_id:

                selected_resume = resume
                break

        if selected_resume and selected_job:

            skill_result = analyze_skill_gap(
                resume_text=selected_resume.resume_text or "",
                job_description=selected_job.job_description,
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Skill Coverage",
                    f"{skill_result['coverage_score']}%",
                )

            with col2:

                st.metric(
                    "Matched Skills",
                    len(skill_result["matched_skills"]),
                )

            with col3:

                st.metric(
                    "Missing Skills",
                    len(skill_result["missing_skills"]),
                )

            col1, col2 = st.columns(2)

            with col1:

                st.write("**Matched Skills**")

                if skill_result["matched_skills"]:

                    for skill in skill_result["matched_skills"]:

                        st.success(skill)

                else:

                    st.info(
                        "No matched skills found."
                    )

            with col2:

                st.write("**Missing Skills**")

                if skill_result["missing_skills"]:

                    for skill in skill_result["missing_skills"]:

                        st.warning(skill)

                else:

                    st.success(
                        "No missing skills found."
                    )

        st.divider()

        st.subheader("❓ Interview Question Generator")

        interview_type = st.selectbox(
            "Select Interview Type",
            options=[
                "HR Interview",
                "Resume-Based Interview",
                "Technical Interview",
                "Project-Based Interview",
                "Job Description-Based Interview",
            ],
            key=f"interview_type_{selected_application.id}",
        )

        if st.button(
            "Generate Interview Questions",
            key=f"generate_interview_questions_{selected_application.id}",
        ):

            if not selected_resume:

                st.error(
                    "Resume version could not be found."
                )

            elif not selected_job:

                st.error(
                    "Job description could not be found."
                )

            else:

                with st.spinner(
                    "AI is generating interview questions..."
                ):

                    ai_response = generate_ai_interview_questions(
                        resume_text=selected_resume.resume_text or "",
                        job_description=selected_job.job_description,
                        interview_type=interview_type,
                    )

                st.write("AI response received.")

                st.code(ai_response)

                questions = [
                    line.strip()
                    for line in ai_response.splitlines()
                    if line.strip()
                ]

                if questions:

                    st.session_state[
                        f"generated_questions_{selected_application.id}"
                    ] = questions

                    st.success(
                        f"{len(questions)} questions generated successfully."
                    )

                else:

                    st.error(
                        "No questions were returned by AI."
                    )

            if not selected_resume:

                st.error(
                    "Resume version could not be found."
                )

            elif not selected_job:

                st.error(
                    "Job description could not be found."
                )

            else:

                ai_response = generate_ai_interview_questions(
                resume_text=selected_resume.resume_text or "",
                job_description=selected_job.job_description,
                interview_type=interview_type,
                )

                questions = [
                    line.strip()
                    for line in ai_response.splitlines()
                    if line.strip()
                ]

                # Remove unwanted headings and empty lines
                questions = [
                    question
                    for question in questions
                    if question.lower() not in [
                        "here are the interview questions:",
                        "interview questions:",
                        "questions:",
                    ]
                ]

                if not questions:

                    st.error(
                        "AI did not return any interview questions."
                    )

                    st.write("Raw AI Response:")
                    st.code(ai_response)

                else:

                    st.session_state[
                        f"generated_questions_{selected_application.id}"
                    ] = questions

                    st.success(
                        f"{len(questions)} interview questions generated."
                    )

                    st.subheader("📝 Generated Interview Questions")

                    for index, question in enumerate(
                        questions,
                        start=1,
                    ):

                        st.write(
                            f"**Q{index}. {question}**"
                        )

                st.session_state[
                    f"generated_questions_{selected_application.id}"
                ] = questions

                existing_questions = get_interview_questions(
                    application_id=selected_application.id
                )

                saved_question_texts = {
                    (
                        saved_question.question,
                        saved_question.interview_type,
                    )
                    for saved_question in existing_questions
                }

                saved_count = 0

                for question in questions:

                    question_key = (
                        question,
                        interview_type,
                    )

                    if question_key not in saved_question_texts:

                        save_interview_question(
                            application_id=selected_application.id,
                            company_name=selected_application.company_name,
                            job_title=selected_application.job_title,
                            resume_version_id=(
                                selected_application.resume_version_id
                            ),
                            resume_version_name=(
                                selected_application.resume_version_name
                            ),
                            resume_file_path=(
                                selected_application.resume_file_path
                            ),
                            job_description=(
                                selected_job.job_description
                            ),
                            interview_type=interview_type,
                            question=question,
                        )

                        saved_count += 1

                st.success(
                    f"Interview questions generated successfully! "
                    f"{saved_count} new question(s) saved."
                )

        generated_questions_key = (
            f"generated_questions_{selected_application.id}"
        )

        if generated_questions_key in st.session_state:

            st.divider()

            st.subheader(
                "📝 Generated Interview Questions"
            )

            generated_questions = st.session_state[
                generated_questions_key
            ]

            for index, question in enumerate(
                generated_questions,
                start=1,
            ):

                st.write(
                    f"**Q{index}. {question}**"
                )

                st.text_area(
                    f"Your Answer - Q{index}",
                    height=100,
                    key=(
                        f"generated_answer_"
                        f"{selected_application.id}_"
                        f"{interview_type}_"
                        f"{index}"
                    ),
                )

            st.info(
                "Practice answering each question using "
                "the exact resume version submitted for this application."
            )

        st.divider()

        st.subheader("💾 Saved Interview Questions")

        saved_questions = get_interview_questions(
            application_id=selected_application.id
        )

        if not saved_questions:

            st.info(
                "No saved interview questions yet."
            )

        else:

            for index, saved_question in enumerate(
                saved_questions,
                start=1,
            ):

                with st.expander(
                    f"Q{index}. "
                    f"{saved_question.question}"
                ):

                    st.write(
                        f"**Interview Type:** "
                        f"{saved_question.interview_type}"
                    )

                    st.write(
                        f"**Resume Version:** "
                        f"{saved_question.resume_version_name}"
                    )

                    current_answer = st.text_area(
                        "Your Answer",
                        value=saved_question.answer or "",
                        height=150,
                        key=f"saved_answer_{saved_question.id}",
                    )
                    
                    if st.button(
                        "🤖 Generate Model Answer",
                        key=f"generate_model_answer_{saved_question.id}",
                    ):

                        if not selected_resume:

                            st.error(
                                "Resume version could not be found."
                            )

                        elif not selected_job:

                            st.error(
                                "Job description could not be found."
                            )

                        else:

                            with st.spinner(
                                "AI is preparing a model answer..."
                            ):

                                model_answer = generate_model_answer(
                                    question=saved_question.question,
                                    resume_text=selected_resume.resume_text or "",
                                    job_description=selected_job.job_description,
                                )

                            st.subheader("🤖 AI Model Answer")

                            st.write(model_answer)

                            st.info(
                                "Use this answer as a reference and customize it "
                                "with your real experience."
                            )
                    
                    

                    status_options = [
                        "Not Started",
                        "In Progress",
                        "Completed",
                    ]

                    current_status = st.selectbox(
                        "Preparation Status",
                        options=status_options,
                        index=status_options.index(
                            saved_question.preparation_status
                            if saved_question.preparation_status
                            in status_options
                            else "Not Started"
                        ),
                        key=f"saved_status_{saved_question.id}",
                    )

                    if st.button(
                        "Save Answer",
                        key=f"save_answer_{saved_question.id}",
                    ):

                        update_interview_answer(
                            question_id=saved_question.id,
                            answer=current_answer,
                            preparation_status=current_status,
                        )

                        st.success(
                            "Answer saved successfully!"
                        )

                        st.rerun()

                    if st.button(
                        "Delete Question",
                        key=f"delete_question_{saved_question.id}",
                    ):

                        delete_interview_question(
                            question_id=saved_question.id
                        )

                        st.success(
                            "Question deleted successfully!"
                        )

                        st.rerun()
                        
elif page == "Resume Improvement":
    
    st.title("✨ AI Resume Improvement")

    st.write(
        "Improve your resume according to a selected job description "
        "using local AI."
    )

    resumes = get_all_resume_versions()
    jobs = get_all_jobs()

    if not resumes:

        st.warning(
            "Please upload at least one resume in Resume Library."
        )

    elif not jobs:

        st.warning(
            "Please save at least one job in Find Jobs."
        )

    else:

        st.subheader("📄 Select Resume")

        resume_options = {
            f"Version {resume.id}: {resume.version_name}": resume
            for resume in resumes
        }

        selected_resume_label = st.selectbox(
            "Choose Resume Version",
            options=list(resume_options.keys()),
            key="improvement_resume_selector",
        )

        selected_resume = resume_options[
            selected_resume_label
        ]

        st.divider()

        st.subheader("💼 Select Job")

        job_options = {
            f"{job.company_name} - {job.job_title}": job
            for job in jobs
        }

        selected_job_label = st.selectbox(
            "Choose Job",
            options=list(job_options.keys()),
            key="improvement_job_selector",
        )

        selected_job = job_options[
            selected_job_label
        ]

        st.divider()

        st.subheader("📊 Selected Details")

        st.write(
            f"**Resume:** {selected_resume.version_name}"
        )

        st.write(
            f"**Company:** {selected_job.company_name}"
        )

        st.write(
            f"**Job Title:** {selected_job.job_title}"
        )

        if not selected_resume.resume_text:

            st.error(
                "Selected resume has no extracted text."
            )

        elif not selected_job.job_description:

            st.error(
                "Selected job has no job description."
            )

        else:

            if st.button(
                "✨ Improve Resume Using AI",
                key="improve_resume_button",
            ):

                with st.spinner(
                    "AI is analyzing your resume..."
                ):

                    improvement_result = improve_resume_for_job(
                        resume_text=selected_resume.resume_text,
                        job_description=selected_job.job_description,
                    )

                st.session_state[
                    "resume_improvement_result"
                ] = improvement_result

                st.success(
                    "Resume improvement analysis completed!"
                )

            if "resume_improvement_result" in st.session_state:

                st.divider()

                st.subheader(
                    "🤖 AI Resume Improvement Report"
                )

                st.markdown(
                    st.session_state[
                        "resume_improvement_result"
                    ]
                )

                st.download_button(
                    label="Download Improvement Report",
                    data=st.session_state["resume_improvement_result"],
                    file_name="resume_improvement_report.md",
                    mime="text/markdown",
                )
    
    
elif page == "Job Application":
    
    st.title("Job Application Assistant")

    st.write(
        "Analyze a job, tailor your resume, and prepare your application."
    )

    resume_text = st.text_area(
        "Paste Your Current Resume",
        height=300,
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=300,
    )

    st.markdown("---")

    if st.button("Generate Resume Recommendations"):

        if not resume_text.strip():
            st.warning("Please enter your resume.")

        elif not job_description.strip():
            st.warning("Please enter the job description.")

        else:
            with st.spinner("Analyzing resume against job description..."):

                recommendation = generate_resume_recommendations(
                    resume_text,
                    job_description,
                )

                st.session_state[
                    "resume_recommendation"
                ] = recommendation

    if "resume_recommendation" in st.session_state:

        st.markdown("## Resume Recommendations")

        st.markdown(
            st.session_state["resume_recommendation"]
        )

        st.download_button(
            "Download Resume Recommendations",
            data=st.session_state["resume_recommendation"],
            file_name="resume_recommendations.md",
            mime="text/markdown",
        )

    st.markdown("---")

    if st.button("Create JD-Tailored Resume"):

        if not resume_text.strip():
            st.warning("Please enter your resume.")

        elif not job_description.strip():
            st.warning("Please enter the job description.")

        else:
            with st.spinner("Creating tailored resume..."):

                tailored_resume = generate_tailored_resume(
                    resume_text,
                    job_description,
                )

                st.session_state[
                    "tailored_resume"
                ] = tailored_resume

    if "tailored_resume" in st.session_state:

        st.markdown("## Tailored Resume")

        st.markdown(
            st.session_state["tailored_resume"]
        )
        
        resume_file_path = "tailored_resume.docx"

    resume_file_path = "tailored_resume.docx"

    create_docx_file(
        st.session_state["tailored_resume"],
        resume_file_path,
    )

    with open(resume_file_path, "rb") as file:

        st.download_button(
            label="Download Tailored Resume DOCX",
            data=file,
            file_name="tailored_resume.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
        )

        st.download_button(
            "Download Tailored Resume",
            data=st.session_state["tailored_resume"],
            file_name="tailored_resume.md",
            mime="text/markdown",
        )

    st.markdown("---")

    if st.button("Generate Cover Letter"):

        if not resume_text.strip():
            st.warning("Please enter your resume.")

        elif not job_description.strip():
            st.warning("Please enter the job description.")

        else:
            with st.spinner("Writing cover letter..."):

                cover_letter = generate_cover_letter(
                    resume_text,
                    job_description,
                )

                st.session_state[
                    "cover_letter"
                ] = cover_letter

    if "cover_letter" in st.session_state:

        st.markdown("## Cover Letter")

        st.markdown(
            st.session_state["cover_letter"]
        )

        st.download_button(
            "Download Cover Letter",
            data=st.session_state["cover_letter"],
            file_name="cover_letter.md",
            mime="text/markdown",
        )                      
