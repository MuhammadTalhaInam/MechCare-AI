import streamlit as st
import asyncio

from crew import run_mechcare


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide"
)


# =========================================================
# CUSTOM UI STYLING
# =========================================================

st.markdown("""
<style>

/* =====================================================
   MAIN APP
   ===================================================== */

.stApp {
    background-color: #0B1220;
    color: #F8FAFC;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* =====================================================
   TEXT
   ===================================================== */

h1 {
    color: #38BDF8 !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

h2 {
    color: #E0F2FE !important;
    font-weight: 700 !important;
}

h3 {
    color: #7DD3FC !important;
}

p {
    color: #CBD5E1 !important;
}

label {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}


/* =====================================================
   HERO SECTION
   ===================================================== */

.hero-section {
    display: flex;
    align-items: center;
    gap: 25px;
    padding: 35px;
    margin-bottom: 35px;
    border-radius: 22px;

    background: linear-gradient(
        135deg,
        #111827,
        #0F2A43
    );

    border: 1px solid #164E63;

    box-shadow:
        0 10px 35px rgba(0, 0, 0, 0.25);
}

.hero-icon {
    width: 85px;
    height: 85px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 20px;

    background: linear-gradient(
        135deg,
        #0284C7,
        #06B6D4
    );

    font-size: 45px;

    box-shadow:
        0 8px 25px rgba(6, 182, 212, 0.25);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 20px;
    font-weight: 600;
    color: #38BDF8;
    margin-bottom: 10px;
}

.hero-description {
    font-size: 16px;
    color: #CBD5E1;
    line-height: 1.6;
}


/* =====================================================
   SECTION CARDS
   ===================================================== */

.section-card {
    background: #111827;
    border: 1px solid #1E3A5F;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 25px;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.18);
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #E0F2FE;
    margin-bottom: 5px;
}

.section-description {
    font-size: 14px;
    color: #94A3B8;
    margin-bottom: 15px;
}


/* =====================================================
   INPUT BOXES
   ===================================================== */

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {

    background-color: #111827 !important;

    border: 1px solid #334155 !important;

    border-radius: 10px !important;
}

input,
textarea {

    color: #F8FAFC !important;

    caret-color: #38BDF8 !important;
}

textarea::placeholder,
input::placeholder {
    color: #64748B !important;
}


/* =====================================================
   SELECT BOX
   ===================================================== */

div[data-baseweb="select"] > div {

    background-color: #111827 !important;

    border: 1px solid #334155 !important;

    border-radius: 10px !important;

    color: #F8FAFC !important;
}


/* =====================================================
   ANALYZE BUTTON
   ===================================================== */

.stButton > button {

    width: 100%;

    background: linear-gradient(
        90deg,
        #0284C7,
        #06B6D4
    );

    color: white !important;

    border: none;

    border-radius: 10px;

    padding: 0.7rem 1rem;

    font-size: 18px;

    font-weight: 700;

    transition: 0.2s;
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px rgba(6, 182, 212, 0.25);
}


/* =====================================================
   REPORT CARD
   ===================================================== */

.report-card {

    background: #111827;

    border: 1px solid #1E5B83;

    border-radius: 18px;

    padding: 30px;

    margin-top: 20px;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.22);
}


/* =====================================================
   REPORT HEADINGS
   ===================================================== */

.report-card h2 {

    color: #38BDF8 !important;

    border-bottom: 1px solid #334155;

    padding-bottom: 8px;

    margin-top: 25px;
}

.report-card h3 {

    color: #7DD3FC !important;
}


/* =====================================================
   SUCCESS / WARNING
   ===================================================== */

div[data-testid="stAlert"] {

    border-radius: 10px;
}


/* =====================================================
   DIVIDER
   ===================================================== */

hr {

    border-color: #1E3A5F !important;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {

    text-align: center;

    color: #64748B;

    font-size: 13px;

    margin-top: 40px;

    padding-top: 20px;

    border-top: 1px solid #1E293B;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero-section">

    <div class="hero-icon">
        ⚙️
    </div>

    <div>

        <div class="hero-title">
            MechCare AI
        </div>

        <div class="hero-subtitle">
            Multi-Agent Machine Maintenance & Troubleshooting Assistant
        </div>

        <div class="hero-description">
            Analyze machine problems, identify possible causes,
            and generate clear maintenance guidance using AI.
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# MACHINE INFORMATION SECTION
# =========================================================

st.markdown("""
<div class="section-card">

    <div class="section-title">
        🔧 Machine Information
    </div>

    <div class="section-description">
        Enter the available machine information and describe the problem.
        MechCare AI will analyze the information using multiple AI agents.
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# MACHINE TYPE + MACHINE AGE
# =========================================================

col1, col2 = st.columns(2)


with col1:

    machine_type = st.selectbox(
        "⚙️ Machine Type",
        [
            "Centrifugal Pump",
            "Electric Motor",
            "Gearbox",
            "Compressor",
            "Fan",
            "Bearing System",
            "Turbine",
            "Other"
        ]
    )


with col2:

    machine_age = st.text_input(
        "📅 Machine Age",
        placeholder="Example: 3 years"
    )


# =========================================================
# PROBLEM DESCRIPTION
# =========================================================

problem_description = st.text_area(
    "⚠️ Problem Description",
    placeholder=(
        "Describe the problem, symptoms, unusual noise, "
        "vibration, leakage, heating, reduced performance, etc."
    ),
    height=130
)


# =========================================================
# OPERATING CONDITION + LAST MAINTENANCE
# =========================================================

col3, col4 = st.columns(2)


with col3:

    operating_condition = st.text_area(
        "🔄 Operating Condition",
        placeholder=(
            "Example: Running continuously at normal "
            "operating speed."
        ),
        height=110
    )


with col4:

    last_maintenance = st.text_input(
        "🛠️ Last Maintenance",
        placeholder="Example: 6 months ago"
    )


# =========================================================
# ADDITIONAL OBSERVATIONS
# =========================================================

additional_observations = st.text_area(
    "🔍 Additional Observations",
    placeholder=(
        "Add any other observations or unusual behavior."
    ),
    height=110
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.write("")

analyze_button = st.button(
    "🔍 Analyze Machine",
    type="primary"
)


# =========================================================
# RUN MECHCARE AI
# =========================================================

if analyze_button:

    if not problem_description.strip():

        st.warning(
            "⚠️ Please enter the problem description before analyzing."
        )

    else:

        # ---------------------------------------------
        # Prepare machine information
        # ---------------------------------------------

        machine_problem = f"""
Machine Type: {machine_type}

Problem Description:
{problem_description}

Operating Condition:
{operating_condition}

Machine Age:
{machine_age}

Last Maintenance:
{last_maintenance}

Additional Observations:
{additional_observations}
"""


        # ---------------------------------------------
        # Run Multi-Agent System
        # ---------------------------------------------

        with st.spinner(
            "🤖 MechCare AI is analyzing the machine..."
        ):

            final_result = asyncio.run(
                run_mechcare(machine_problem)
            )


        # ---------------------------------------------
        # Success message
        # ---------------------------------------------

        st.success(
            "✅ Analysis completed successfully!"
        )


        # ---------------------------------------------
        # Final Report
        # ---------------------------------------------

        st.markdown("""
        <div class="report-card">
        """, unsafe_allow_html=True)

        st.markdown(
            "## 📋 Final Maintenance Report"
        )

        st.markdown(
            final_result
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

    ⚙️ MechCare AI &nbsp;|&nbsp;
    Multi-Agent Machine Maintenance Assistant

    <br>

    AI-generated guidance should be verified by a qualified
    engineer or technician before performing maintenance.

</div>
""", unsafe_allow_html=True)
