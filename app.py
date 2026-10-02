import streamlit as st
import asyncio
import html

from crew import run_mechcare


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================================
       MAIN APP
    ================================= */

    .stApp {
        background: linear-gradient(
            135deg,
            #07111f 0%,
            #0b1728 50%,
            #101c2f 100%
        );
        color: #f1f5f9;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }


    /* ================================
       HERO
    ================================= */

    .hero-box {
        background: linear-gradient(
            135deg,
            #0d2238,
            #102d49
        );
        border: 1px solid #1e4d73;
        border-radius: 22px;
        padding: 38px 40px;
        margin-bottom: 28px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.25);
    }

    .main-title {
        font-size: 46px;
        font-weight: 800;
        margin-bottom: 8px;
        color: #f8fafc;
    }

    .main-subtitle {
        font-size: 21px;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 15px;
    }

    .main-description {
        font-size: 16px;
        line-height: 1.7;
        color: #cbd5e1;
        max-width: 950px;
    }


    /* ================================
       SECTIONS
    ================================= */

    .section-box {
        background: #0d1b2a;
        border: 1px solid #20384f;
        border-radius: 18px;
        padding: 25px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 5px;
    }

    .section-description {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.6;
    }


    /* ================================
       WORKFLOW CARDS
    ================================= */

    .workflow-card {
        background: linear-gradient(
            145deg,
            #0c1a29,
            #102338
        );
        border: 1px solid #29445d;
        border-radius: 16px;
        padding: 20px;
        min-height: 190px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
        transition: all 0.2s ease;
    }

    .workflow-card:hover {
        border-color: #38bdf8;
        transform: translateY(-3px);
    }

    .workflow-number {
        display: inline-block;
        font-size: 12px;
        font-weight: 800;
        color: #38bdf8;
        background: #102f49;
        border: 1px solid #245b7d;
        border-radius: 20px;
        padding: 5px 10px;
        margin-bottom: 12px;
    }

    .workflow-title {
        font-size: 17px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.4;
        margin-bottom: 10px;
    }

    .workflow-text {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.6;
    }


    /* ================================
       SYMPTOM TAGS
    ================================= */

    .symptom-container {
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .symptom-tag {
        display: inline-block;
        background: #123653;
        border: 1px solid #1d668f;
        color: #7dd3fc;
        border-radius: 20px;
        padding: 7px 13px;
        margin: 4px;
        font-size: 13px;
        font-weight: 600;
    }


    /* ================================
       INPUTS
    ================================= */

    label {
        color: #dbeafe !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #101f31 !important;
        border-color: #29445d !important;
    }

    textarea {
        background-color: #101f31 !important;
        color: #f8fafc !important;
    }

    input {
        background-color: #101f31 !important;
        color: #f8fafc !important;
    }


    /* ================================
       BUTTON
    ================================= */

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 14px;
        font-size: 17px;
        font-weight: 700;
        border: none;
        background: linear-gradient(
            90deg,
            #0284c7,
            #06b6d4
        );
        color: white;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.25);
    }


    /* ================================
       REPORT
    ================================= */

    .report-box {
        background: #0b1928;
        border: 1px solid #245276;
        border-radius: 18px;
        padding: 30px;
        margin-top: 20px;
        line-height: 1.7;
        color: #dbeafe;
    }

    .report-box h1,
    .report-box h2 {
        color: #38bdf8;
        border-bottom: 1px solid #29445d;
        padding-bottom: 8px;
    }

    .report-box h3 {
        color: #67e8f9;
    }

    .report-box p,
    .report-box li {
        color: #dbeafe;
    }


    /* ================================
       FOOTER
    ================================= */

    .footer {
        text-align: center;
        color: #64748b;
        margin-top: 45px;
        font-size: 13px;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero-box">

        <div class="main-title">
            ⚙️ MechCare AI
        </div>

        <div class="main-subtitle">
            AI-Powered Machine Maintenance & Troubleshooting Assistant
        </div>

        <div class="main-description">
            Describe your machine, operating conditions, and observed
            symptoms. MechCare AI uses a multi-agent engineering workflow
            to analyze the problem, identify possible causes, suggest
            maintenance actions, and generate a structured safety-focused
            report.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# AI WORKFLOW
# =========================================================

st.markdown(
    """
    <div class="section-box">

        <div class="section-title">
            🤖 How MechCare AI Works
        </div>

        <div class="section-description">
            Your machine problem passes through four specialized AI agents.
            Each agent performs a different engineering task before the
            final report is generated.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


workflow_cols = st.columns(4)

workflow_data = [
    (
        "01",
        "🔍 Problem Analysis Agent",
        "Analyzes machine information, symptoms, observations, and missing information."
    ),
    (
        "02",
        "🧠 Fault Diagnosis Agent",
        "Examines symptoms and identifies possible mechanical and operational causes."
    ),
    (
        "03",
        "🛠️ Maintenance Planning Agent",
        "Converts possible causes into practical inspection and maintenance actions."
    ),
    (
        "04",
        "🛡️ Safety & Final Report Agent",
        "Reviews the previous results and creates the final safety-focused engineering report."
    )
]


for col, data in zip(workflow_cols, workflow_data):

    number, title, description = data

    with col:

        st.markdown(
            f"""
            <div class="workflow-card">

                <div class="workflow-number">
                    AGENT {number}
                </div>

                <div class="workflow-title">
                    {title}
                </div>

                <div class="workflow-text">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# MACHINE PROFILE
# =========================================================

st.markdown(
    """
    <div class="section-box">

        <div class="section-title">
            🏭 Machine Profile
        </div>

        <div class="section-description">
            Provide basic information about the machine so the AI can
            understand its operating context.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MACHINE MODELS
# =========================================================

MACHINE_MODELS = {

    "Centrifugal Pump": [
        "KSB Etanorm",
        "Grundfos CR",
        "Sulzer AHLSTAR",
        "Generic / Unknown"
    ],

    "Electric Motor": [
        "ABB M3BP",
        "Siemens SIMOTICS",
        "WEG W22",
        "Generic / Unknown"
    ],

    "Gearbox": [
        "SEW-Eurodrive",
        "Flender",
        "Bonfiglioli",
        "Generic / Unknown"
    ],

    "Compressor": [
        "Atlas Copco GA",
        "Ingersoll Rand",
        "Kaeser",
        "Generic / Unknown"
    ],

    "Fan": [
        "ABB Fan",
        "Siemens Fan",
        "Generic Industrial Fan",
        "Generic / Unknown"
    ],

    "Bearing System": [
        "SKF Bearing",
        "FAG Bearing",
        "NTN Bearing",
        "Generic / Unknown"
    ],

    "Turbine": [
        "Francis Turbine",
        "Pelton Turbine",
        "Kaplan Turbine",
        "Generic / Unknown"
    ],

    "Other": [
        "Generic Machine",
        "Custom Equipment",
        "Unknown"
    ]
}


# =========================================================
# MACHINE PROFILE INPUTS
# =========================================================

col1, col2, col3 = st.columns(3)


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


with col3:

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


col4, col5, col6 = st.columns(3)


with col4:

    model = st.selectbox(
        "🔧 Model",
        MACHINE_MODELS[machine_type]
    )


with col5:

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


with col6:

    operating_hours = st.selectbox(
        "⏱️ Operating Hours",
        [
            "Less than 2 hours/day",
            "2–4 hours/day",
            "4–8 hours/day",
            "8–12 hours/day",
            "More than 12 hours/day",
            "Continuous",
            "Unknown"
        ]
    )


col7, col8, col9 = st.columns(3)


with col7:

    operating_speed = st.selectbox(
        "🔄 Operating Speed",
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


with col8:

    load_condition = st.selectbox(
        "⚡ Load Condition",
        [
            "Unknown",
            "No Load",
            "Light Load",
            "Moderate Load",
            "Heavy Load",
            "Variable Load"
        ]
    )


with col9:

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
# SMART SYMPTOM SELECTION
# =========================================================

st.markdown(
    """
    <div class="section-box">

        <div class="section-title">
            🔍 Observed Symptoms
        </div>

        <div class="section-description">
            Select all symptoms currently observed in the machine.
            You can select multiple symptoms.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


symptom_options = [
    "🔊 Unusual Noise",
    "📳 Excessive Vibration",
    "🌡️ Overheating",
    "📉 Reduced Performance",
    "💧 Leakage",
    "⚡ Increased Power Consumption",
    "🔄 Slow / Irregular Operation",
    "💨 Pressure / Flow Problem",
    "🔩 Loose Components",
    "🛢️ Lubrication Problem",
    "🔥 Burning Smell",
    "⚠️ Other"
]


selected_symptoms = st.multiselect(
    "Select observed symptoms",
    symptom_options,
    placeholder="Choose one or more symptoms..."
)


if selected_symptoms:

    st.markdown(
        "### Selected Symptoms"
    )

    symptom_html = '<div class="symptom-container">'

    for symptom in selected_symptoms:

        safe_symptom = html.escape(symptom)

        symptom_html += (
            f'<span class="symptom-tag">'
            f'{safe_symptom}'
            f'</span>'
        )

    symptom_html += "</div>"

    st.markdown(
        symptom_html,
        unsafe_allow_html=True
    )


# =========================================================
# PROBLEM INFORMATION
# =========================================================

st.markdown(
    """
    <div class="section-box">

        <div class="section-title">
            🚨 Problem Information
        </div>

        <div class="section-description">
            Describe what is happening with the machine. More useful
            information helps the AI produce a more relevant engineering
            analysis.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


problem_description = st.text_area(
    "Problem Description",
    placeholder=(
        "Example: The pump produces unusual noise and vibration "
        "during operation. Flow rate has decreased."
    ),
    height=130
)


operating_condition = st.text_area(
    "Operating Condition",
    placeholder=(
        "Example: Machine operates continuously at approximately "
        "1450 RPM under moderate load."
    ),
    height=110
)


additional_observations = st.text_area(
    "Additional Observations",
    placeholder=(
        "Example: Vibration becomes higher after several hours "
        "of continuous operation."
    ),
    height=110
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)


analyze_button = st.button(
    "🔍 Analyze Machine Problem"
)


# =========================================================
# RUN AI WORKFLOW
# =========================================================

if analyze_button:

    if not problem_description.strip() and not selected_symptoms:

        st.warning(
            "Please provide a problem description or select at least one symptom."
        )

    else:

        selected_symptoms_text = (
            ", ".join(selected_symptoms)
            if selected_symptoms
            else "No specific symptoms selected"
        )


        # =====================================================
        # MACHINE INFORMATION SENT TO CREW
        # =====================================================

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

Last Maintenance:
{last_maintenance}


PROBLEM INFORMATION

Observed Symptoms:
{selected_symptoms_text}

Problem Description:
{problem_description}

Operating Condition:
{operating_condition}

Additional Observations:
{additional_observations}

"""


        # =====================================================
        # AI PROCESSING
        # =====================================================

        with st.spinner(
            "🤖 MechCare AI is analyzing the machine through 4 AI agents..."
        ):

            try:

                result = asyncio.run(
                    run_mechcare(machine_problem)
                )


                st.success(
                    "✅ Machine analysis completed successfully."
                )


                # =================================================
                # FINAL REPORT
                # =================================================

                st.markdown(
                    """
                    <div class="section-box">

                        <div class="section-title">
                            📋 Engineering Analysis Report
                        </div>

                        <div class="section-description">
                            Generated by the MechCare AI multi-agent
                            engineering workflow.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                # Convert result safely to string
                result_text = str(result)


                st.markdown(
                    f"""
                    <div class="report-box">

                    {result_text}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            except Exception as e:

                st.error(
                    "❌ An error occurred while analyzing the machine."
                )

                st.warning(
                    "Please check your Groq API key and Streamlit deployment logs."
                )

                st.code(
                    str(e)
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        ⚙️ <b>MechCare AI</b>
        <br>

        AI-Based Mechanical Maintenance & Troubleshooting Assistant

        <br><br>

        Designed for engineering decision support and educational use.

    </div>
    """,
    unsafe_allow_html=True
)
