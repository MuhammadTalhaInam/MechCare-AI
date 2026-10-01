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
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main application */

    .stApp {
        background-color: #0B1220;
        color: #F8FAFC;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* Main title */

    .main-title {
        font-size: 44px;
        font-weight: 800;
        color: #38BDF8;
    }

    .main-subtitle {
        font-size: 20px;
        font-weight: 600;
        color: #7DD3FC;
    }

    .main-description {
        font-size: 16px;
        color: #CBD5E1;
    }


    /* Hero box */

    .hero-box {
        background: linear-gradient(135deg, #111827, #0F2A43);
        border: 1px solid #164E63;
        border-radius: 22px;
        padding: 35px;
        margin-bottom: 30px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    }


    /* Section */

    .section-box {
        background-color: #111827;
        border: 1px solid #1E3A5F;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #E0F2FE;
    }

    .section-description {
        font-size: 14px;
        color: #94A3B8;
    }


    /* Input labels */

    label {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }


    /* Input fields */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #111827 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    input,
    textarea {
        color: #F8FAFC !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #64748B !important;
    }


    /* Select box */

    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }


    /* Analyze button */

    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #0284C7, #06B6D4);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 18px;
        font-weight: 700;
    }

    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(6,182,212,0.30);
        transform: translateY(-2px);
    }


    /* Report */

    .report-box {
        background-color: #111827;
        border: 1px solid #1E5B83;
        border-radius: 18px;
        padding: 30px;
        margin-top: 25px;
    }

    .report-box h2 {
        color: #38BDF8 !important;
    }

    .report-box h3 {
        color: #7DD3FC !important;
    }


    /* Footer */

    .footer {
        text-align: center;
        color: #64748B;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #1E293B;
    }


    /* Workflow */

    .workflow-container {
        background: linear-gradient(135deg, #111827, #0F2A43);
        border: 1px solid #1E5B83;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.20);
    }

    .workflow-title {
        color: #E0F2FE;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
    }

    .workflow-step {
        background-color: #0B1220;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 10px;
        text-align: center;
        min-height: 125px;
    }

    .workflow-icon {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .workflow-name {
        color: #F8FAFC;
        font-size: 14px;
        font-weight: 700;
    }

    .workflow-description {
        color: #94A3B8;
        font-size: 11px;
        margin-top: 5px;
    }

    .workflow-arrow {
        color: #38BDF8;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        padding-top: 38px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    '<div class="hero-box">',
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 8])

with col1:
    st.markdown(
        "<div style='font-size:55px;'>⚙️</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<div class="main-title">MechCare AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Multi-Agent Machine Maintenance & Troubleshooting Assistant'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-description">'
        'Analyze machine problems, identify possible causes, '
        'and generate clear maintenance guidance using AI.'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# AI WORKFLOW
# =========================================================

st.markdown(
    """
    <div class="workflow-container">

        <div class="workflow-title">
            🤖 How MechCare AI Works
        </div>

        <div style="
            display: flex;
            align-items: stretch;
            justify-content: center;
            gap: 8px;
        ">

            <!-- USER PROBLEM -->

            <div style="flex: 1;">
                <div class="workflow-step">
                    <div class="workflow-icon">👤</div>

                    <div class="workflow-name">
                        User Problem
                    </div>

                    <div class="workflow-description">
                        Machine symptoms
                    </div>
                </div>
            </div>


            <div class="workflow-arrow">
                →
            </div>


            <!-- PROBLEM ANALYSIS -->

            <div style="flex: 1;">
                <div class="workflow-step">
                    <div class="workflow-icon">🔍</div>

                    <div class="workflow-name">
                        Problem Analysis
                    </div>

                    <div class="workflow-description">
                        Understand symptoms
                    </div>
                </div>
            </div>


            <div class="workflow-arrow">
                →
            </div>


            <!-- FAULT DIAGNOSIS -->

            <div style="flex: 1;">
                <div class="workflow-step">
                    <div class="workflow-icon">🧠</div>

                    <div class="workflow-name">
                        Fault Diagnosis
                    </div>

                    <div class="workflow-description">
                        Find possible causes
                    </div>
                </div>
            </div>


            <div class="workflow-arrow">
                →
            </div>


            <!-- MAINTENANCE -->

            <div style="flex: 1;">
                <div class="workflow-step">
                    <div class="workflow-icon">🛠️</div>

                    <div class="workflow-name">
                        Maintenance Planning
                    </div>

                    <div class="workflow-description">
                        Plan corrective actions
                    </div>
                </div>
            </div>


            <div class="workflow-arrow">
                →
            </div>


            <!-- SAFETY AND REPORT -->

            <div style="flex: 1;">
                <div class="workflow-step">
                    <div class="workflow-icon">🛡️</div>

                    <div class="workflow-name">
                        Safety & Final Report
                    </div>

                    <div class="workflow-description">
                        Generate final report
                    </div>
                </div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MACHINE INFORMATION
# =========================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🔧 Machine Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Enter the available machine information and describe the problem. '
    'MechCare AI will analyze the information using multiple AI agents.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# MACHINE TYPE AND AGE
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
# OPERATING CONDITION AND MAINTENANCE
# =========================================================

col1, col2 = st.columns(2)

with col1:
    operating_condition = st.text_area(
        "🔄 Operating Condition",
        placeholder=(
            "Example: Running continuously at normal "
            "operating speed."
        ),
        height=110
    )

with col2:
    last_maintenance = st.text_input(
        "🛠️ Last Maintenance",
        placeholder="Example: 6 months ago"
    )


# =========================================================
# ADDITIONAL OBSERVATIONS
# =========================================================

additional_observations = st.text_area(
    "🔍 Additional Observations",
    placeholder="Add any other observations or unusual behavior.",
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
# AI ANALYSIS
# =========================================================

if analyze_button:

    if not problem_description.strip():

        st.warning(
            "⚠️ Please enter the problem description before analyzing."
        )

    else:

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

        with st.spinner(
            "🤖 MechCare AI is analyzing the machine..."
        ):

            final_result = asyncio.run(
                run_mechcare(machine_problem)
            )

        st.success(
            "✅ Analysis completed successfully!"
        )

        st.markdown(
            '<div class="report-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            "## 📋 Final Maintenance Report"
        )

        st.markdown(
            final_result
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    '⚙️ MechCare AI | Multi-Agent Machine Maintenance Assistant'
    '<br>'
    'AI-generated guidance should be verified by a qualified '
    'engineer or technician before performing maintenance.'
    '</div>',
    unsafe_allow_html=True
)
