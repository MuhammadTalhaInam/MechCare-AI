import streamlit as st
import asyncio

from crew import run_mechcare


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CHECKLIST STATE
# =========================================================

checklist_items = [
    "Check machine for unusual noise",
    "Check for excessive vibration",
    "Check temperature",
    "Check for leakage",
    "Check lubrication condition",
    "Check loose components",
    "Check alignment",
    "Check operating conditions"
]

for item in checklist_items:
    if item not in st.session_state:
        st.session_state[item] = False


# =========================================================
# AI ANALYSIS STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #07111f 0%,
            #0b1728 50%,
            #101c2f 100%
        );
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #0d2238, #102d49);
        border: 1px solid #1e4d73;
        border-radius: 22px;
        padding: 35px;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: 46px;
        margin-bottom: 5px;
    }

    .hero h3 {
        color: #38bdf8;
        margin-top: 0;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.7;
    }

    /* Selected symptom */
    .symptom-box {
        background: #123653;
        border: 1px solid #1d668f;
        border-radius: 12px;
        padding: 12px 15px;
        color: #7dd3fc;
        margin-top: 10px;
    }

    /* Report */
    .report-box {
        background: #0b1928;
        border: 1px solid #245276;
        border-radius: 18px;
        padding: 25px;
        color: #dbeafe;
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
    <div class="hero">
        <h1>⚙️ MechCare AI</h1>
        <h3>AI-Powered Machine Maintenance & Troubleshooting Assistant</h3>
        <p>
            Describe your machine, operating conditions, and observed
            symptoms. MechCare AI uses a multi-agent engineering workflow
            to analyze the problem, identify possible causes, suggest
            maintenance actions, and generate a structured safety-focused
            report.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WORKFLOW
# =========================================================

st.subheader("🤖 How MechCare AI Works")

st.caption(
    "Your machine problem passes through four specialized AI agents. "
    "Each agent performs a different engineering task before the final report is generated."
)


workflow = [
    (
        "AGENT 01",
        "🔍 Problem Analysis Agent",
        "Analyzes machine information, symptoms, observations, and missing information."
    ),
    (
        "AGENT 02",
        "🧠 Fault Diagnosis Agent",
        "Examines symptoms and identifies possible mechanical and operational causes."
    ),
    (
        "AGENT 03",
        "🛠️ Maintenance Planning Agent",
        "Converts possible causes into practical inspection and maintenance actions."
    ),
    (
        "AGENT 04",
        "🛡️ Safety & Final Report Agent",
        "Reviews the previous results and creates the final safety-focused engineering report."
    )
]


workflow_columns = st.columns(4)

for column, agent in zip(workflow_columns, workflow):

    number, title, description = agent

    with column:

        st.info(
            f"**{number}**\n\n"
            f"### {title}\n\n"
            f"{description}"
        )


st.divider()


# =========================================================
# MACHINE PROFILE
# =========================================================

st.subheader("🏭 Machine Profile")

st.caption(
    "Provide basic information about the machine so the AI can understand its operating context."
)


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
# MACHINE INFORMATION
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


st.divider()


# =========================================================
# SYMPTOMS
# =========================================================

st.subheader("🔍 Observed Symptoms")

st.caption(
    "Select all symptoms currently observed in the machine. "
    "You can select multiple symptoms."
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

    st.info(
        "Selected symptoms: " + "  •  ".join(selected_symptoms)
    )


st.divider()


# =========================================================
# PROBLEM INFORMATION
# =========================================================

st.subheader("🚨 Problem Information")

st.caption(
    "Describe what is happening with the machine. "
    "More useful information helps the AI produce a more relevant engineering analysis."
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

st.write("")


analyze_button = st.button(
    "🔍 Analyze Machine Problem",
    use_container_width=True
)


# =========================================================
# RUN AI ANALYSIS
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


        # -----------------------------------------------------
        # CREATE MACHINE INFORMATION FOR THE AI
        # -----------------------------------------------------

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


        # -----------------------------------------------------
        # RUN FOUR AGENTS
        # -----------------------------------------------------

        with st.spinner(
            "🤖 MechCare AI is analyzing the machine through 4 AI agents..."
        ):

            try:

                result = asyncio.run(
                    run_mechcare(machine_problem)
                )

                # SAVE THE AI RESULT
                st.session_state.analysis_result = result

                st.success(
                    "✅ Machine analysis completed successfully."
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
# DISPLAY AI ANALYSIS
# =========================================================

if st.session_state.analysis_result is not None:

    result = st.session_state.analysis_result

    # -------------------------------------------------
    # GET DIAGNOSIS AND FINAL REPORT
    # -------------------------------------------------

    diagnosis_result = result["diagnosis"]
    final_report = result["final_report"]


    # =================================================
    # ENHANCED HEALTH DASHBOARD
    # =================================================

    st.subheader("📊 Machine Health Dashboard")

    report_text = final_report

    # -------------------------------------------------
    # EXTRACT PRIORITY FROM AI REPORT
    # -------------------------------------------------

    priority = "Not specified"

    if "## Priority" in report_text:

        priority_section = report_text.split(
            "## Priority",
            1
        )[1]

        if "##" in priority_section:

            priority = priority_section.split(
                "##",
                1
            )[0].strip()

        else:

            priority = priority_section.strip()


    # -------------------------------------------------
    # DETERMINE HEALTH STATUS
    # -------------------------------------------------

    priority_lower = priority.lower()

    if (
        "critical" in priority_lower
        or "urgent" in priority_lower
    ):

        health_status = "🔴 Critical"
        maintenance_status = "Immediate Inspection"

    elif "high" in priority_lower:

        health_status = "🟠 Attention Required"
        maintenance_status = "Inspection Recommended"

    elif (
        "medium" in priority_lower
        or "moderate" in priority_lower
    ):

        health_status = "🟡 Monitor"
        maintenance_status = "Further Inspection"

    else:

        health_status = "🟢 Review Required"
        maintenance_status = "Follow Recommended Checks"


    # -------------------------------------------------
    # DASHBOARD CARDS
    # -------------------------------------------------

    dash1, dash2, dash3, dash4 = st.columns(4)

    with dash1:

        st.markdown("### 🏭 Machine")
        st.write(machine_type)

    with dash2:

        st.markdown("### ❤️ Health Status")
        st.write(health_status)

    with dash3:

        st.markdown("### ⚠️ Priority")
        st.write(priority)

    with dash4:

        st.markdown("### 🔧 Maintenance")
        st.write(maintenance_status)


    st.info(
        f"**Machine:** {machine_type}  |  "
        f"**ID:** {machine_id}  |  "
        f"**Manufacturer:** {manufacturer}"
    )


    # =================================================
    # SMART DIAGNOSIS
    # =================================================

    st.subheader(
        "🧠 Possible Faults & Diagnostic Checks"
    )

    st.caption(
        "The AI identifies possible causes, explains why they "
        "may be related to the symptoms, and suggests simple "
        "checks for confirmation."
    )

    st.markdown(
        diagnosis_result
    )


    # =================================================
    # MAINTENANCE CHECKLIST
    # =================================================

    st.subheader(
        "🔧 Maintenance Checklist"
    )

    st.caption(
        "Tick each check when you have completed it."
    )

    check1, check2 = st.columns(2)

    with check1:

        st.checkbox(
            "Check machine for unusual noise",
            key="Check machine for unusual noise"
        )

        st.checkbox(
            "Check for excessive vibration",
            key="Check for excessive vibration"
        )

        st.checkbox(
            "Check temperature",
            key="Check temperature"
        )

        st.checkbox(
            "Check for leakage",
            key="Check for leakage"
        )

    with check2:

        st.checkbox(
            "Check lubrication condition",
            key="Check lubrication condition"
        )

        st.checkbox(
            "Check loose components",
            key="Check loose components"
        )

        st.checkbox(
            "Check alignment",
            key="Check alignment"
        )

        st.checkbox(
            "Check operating conditions",
            key="Check operating conditions"
        )


    # =================================================
    # FINAL REPORT
    # =================================================

    st.subheader(
        "📋 Engineering Analysis Report"
    )

    st.caption(
        "Generated by the MechCare AI multi-agent engineering workflow."
    )


    st.markdown(
        final_report
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚙️ MechCare AI | AI-Based Mechanical Maintenance & Troubleshooting Assistant"
)

st.caption(
    "Designed for engineering decision support and educational use."
)
