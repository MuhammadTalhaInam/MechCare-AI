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
# MACHINE DATA
# =========================================================

MACHINE_MODELS = {
    "Centrifugal Pump": [
        "General Purpose Pump",
        "End-Suction Pump",
        "Horizontal Split-Case Pump",
        "Multistage Pump",
        "Other"
    ],

    "Electric Motor": [
        "Induction Motor",
        "Synchronous Motor",
        "Three-Phase Motor",
        "Single-Phase Motor",
        "Other"
    ],

    "Gearbox": [
        "Helical Gearbox",
        "Worm Gearbox",
        "Planetary Gearbox",
        "Bevel Gearbox",
        "Other"
    ],

    "Compressor": [
        "Reciprocating Compressor",
        "Screw Compressor",
        "Centrifugal Compressor",
        "Scroll Compressor",
        "Other"
    ],

    "Fan": [
        "Axial Fan",
        "Centrifugal Fan",
        "Radial Fan",
        "Industrial Exhaust Fan",
        "Other"
    ],

    "Bearing System": [
        "Ball Bearing",
        "Roller Bearing",
        "Tapered Roller Bearing",
        "Thrust Bearing",
        "Other"
    ],

    "Turbine": [
        "Francis Turbine",
        "Pelton Turbine",
        "Kaplan Turbine",
        "Steam Turbine",
        "Other"
    ],

    "Other": [
        "Other Machine / Equipment"
    ]
}


# =========================================================
# PAGE STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0B1220;
    color: #F8FAFC;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* HERO */

.hero-box {
    background: linear-gradient(135deg, #111827, #0F2A43);
    border: 1px solid #164E63;
    border-radius: 22px;
    padding: 35px;
    margin-bottom: 30px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
}

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


/* SECTION */

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


/* INPUTS */

label {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}

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


/* SELECT */

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}


/* BUTTON */

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


/* REPORT */

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


/* FOOTER */

.footer {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1E293B;
}


/* WORKFLOW */

.workflow-card {
    background-color: #111827;
    border: 1px solid #1E5B83;
    border-radius: 16px;
    padding: 18px 10px;
    text-align: center;
    min-height: 135px;
}

.workflow-icon {
    font-size: 32px;
}

.workflow-name {
    color: #F8FAFC;
    font-weight: 700;
    font-size: 14px;
}

.workflow-description {
    color: #94A3B8;
    font-size: 12px;
}

.workflow-arrow {
    color: #38BDF8;
    font-size: 25px;
    text-align: center;
    padding-top: 45px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HERO
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

st.markdown("## 🤖 How MechCare AI Works")

st.caption(
    "Your machine problem passes through multiple specialized AI agents."
)

workflow = st.columns(
    [1, 0.15, 1, 0.15, 1, 0.15, 1, 0.15, 1]
)


with workflow[0]:

    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-icon">👤</div>
            <br>
            <div class="workflow-name">User Problem</div>
            <div class="workflow-description">
                Machine symptoms
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with workflow[1]:

    st.markdown(
        '<div class="workflow-arrow">→</div>',
        unsafe_allow_html=True
    )


with workflow[2]:

    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-icon">🔍</div>
            <br>
            <div class="workflow-name">Problem Analysis</div>
            <div class="workflow-description">
                Understand symptoms
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with workflow[3]:

    st.markdown(
        '<div class="workflow-arrow">→</div>',
        unsafe_allow_html=True
    )


with workflow[4]:

    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-icon">🧠</div>
            <br>
            <div class="workflow-name">Fault Diagnosis</div>
            <div class="workflow-description">
                Find possible causes
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with workflow[5]:

    st.markdown(
        '<div class="workflow-arrow">→</div>',
        unsafe_allow_html=True
    )


with workflow[6]:

    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-icon">🛠️</div>
            <br>
            <div class="workflow-name">Maintenance Planning</div>
            <div class="workflow-description">
                Plan corrective actions
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with workflow[7]:

    st.markdown(
        '<div class="workflow-arrow">→</div>',
        unsafe_allow_html=True
    )


with workflow[8]:

    st.markdown(
        """
        <div class="workflow-card">
            <div class="workflow-icon">🛡️</div>
            <br>
            <div class="workflow-name">Safety & Final Report</div>
            <div class="workflow-description">
                Generate final report
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")
st.write("")


# =========================================================
# MACHINE PROFILE
# =========================================================

st.markdown(
    '<div class="section-box">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🏭 Machine Profile</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Select the machine information below. The model options '
    'change automatically based on the selected machine type.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# MACHINE TYPE
# =========================================================

machine_types = list(MACHINE_MODELS.keys())

machine_type = st.selectbox(
    "⚙️ Machine Type",
    machine_types
)


# =========================================================
# MACHINE ID / MANUFACTURER / MODEL
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    machine_id = st.selectbox(
        "🆔 Machine ID / Name",
        [
            "MCH-001",
            "MCH-002",
            "MCH-003",
            "MCH-004",
            "MCH-005",
            "MCH-006",
            "MCH-007",
            "MCH-008",
            "Other"
        ]
    )


with col2:

    manufacturer = st.selectbox(
        "🏢 Manufacturer",
        [
            "ABB",
            "Siemens",
            "WEG",
            "KSB",
            "Sulzer",
            "Grundfos",
            "Caterpillar",
            "General Electric",
            "Other / Unknown"
        ]
    )


with col3:

    model = st.selectbox(
        "📦 Model",
        MACHINE_MODELS[machine_type]
    )


# =========================================================
# MACHINE AGE / OPERATING HOURS
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    machine_age = st.selectbox(
        "📅 Machine Age",
        [
            "Less than 1 year",
            "1–2 years",
            "3–5 years",
            "6–10 years",
            "More than 10 years",
            "Unknown"
        ]
    )


with col2:

    operating_hours = st.selectbox(
        "⏱️ Operating Hours",
        [
            "Less than 2 hours/day",
            "2–4 hours/day",
            "4–8 hours/day",
            "8–12 hours/day",
            "More than 12 hours/day",
            "Continuous operation",
            "Unknown"
        ]
    )


with col3:

    operating_speed = st.selectbox(
        "⚙️ Operating Speed",
        [
            "Below 500 RPM",
            "500–1000 RPM",
            "1000–1500 RPM",
            "1500–3000 RPM",
            "Above 3000 RPM",
            "Variable Speed",
            "Unknown"
        ]
    )


# =========================================================
# LOAD CONDITION / LAST MAINTENANCE
# =========================================================

col1, col2 = st.columns(2)


with col1:

    load_condition = st.selectbox(
        "🔩 Load Condition",
        [
            "Unknown",
            "No Load",
            "Light Load",
            "Moderate Load",
            "Heavy Load",
            "Variable Load"
        ]
    )


with col2:

    last_maintenance = st.selectbox(
        "🛠️ Last Maintenance",
        [
            "Less than 1 month ago",
            "1–3 months ago",
            "3–6 months ago",
            "6–12 months ago",
            "More than 1 year ago",
            "Unknown"
        ]
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
# OPERATING CONDITION
# =========================================================

operating_condition = st.text_area(
    "🔄 Operating Condition",
    placeholder=(
        "Example: Running continuously at normal operating "
        "speed under moderate load."
    ),
    height=110
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
MACHINE PROFILE

Machine ID / Name:
{machine_id}

Manufacturer:
{manufacturer}

Model:
{model}

Machine Type:
{machine_type}

Machine Age:
{machine_age}

Operating Hours:
{operating_hours}

Operating Speed:
{operating_speed}

Load Condition:
{load_condition}


PROBLEM INFORMATION

Problem Description:
{problem_description}

Operating Condition:
{operating_condition}

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
