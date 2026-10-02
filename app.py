import streamlit as st
import asyncio

from crew import run_mechcare


# =================================================
# PAGE CONFIGURATION
# =================================================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide"
)


# =================================================
# TITLE
# =================================================

st.title("⚙️ MechCare AI")

st.write(
    "AI-based machine maintenance and troubleshooting assistant "
    "for mechanical equipment."
)

st.divider()


# =================================================
# MACHINE PROFILE
# =================================================

st.header("🏭 Machine Profile")

col1, col2 = st.columns(2)

with col1:

    machine_type = st.selectbox(
        "Machine Type",
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

    machine_id = st.selectbox(
        "Machine ID / Name",
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

    manufacturer = st.selectbox(
        "Manufacturer",
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

    model_options = {

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

    model = st.selectbox(
        "Model",
        model_options[machine_type]
    )


with col2:

    machine_age = st.selectbox(
        "Machine Age",
        [
            "Less than 1 year",
            "1–2 years",
            "3–5 years",
            "6–10 years",
            "More than 10 years",
            "Unknown"
        ]
    )

    operating_hours = st.selectbox(
        "Operating Hours",
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

    operating_speed = st.selectbox(
        "Operating Speed",
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

    load_condition = st.selectbox(
        "Load Condition",
        [
            "Unknown",
            "No Load",
            "Light Load",
            "Moderate Load",
            "Heavy Load",
            "Variable Load"
        ]
    )

    last_maintenance = st.selectbox(
        "Last Maintenance",
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


# =================================================
# MACHINE SYMPTOMS
# =================================================

st.header("📋 Machine Symptoms")

symptoms = st.multiselect(
    "Select the symptoms you are observing:",
    [
        "Unusual Noise",
        "Excessive Vibration",
        "Overheating",
        "Reduced Performance",
        "Leakage",
        "Increased Power Consumption",
        "Slow / Irregular Operation",
        "Pressure / Flow Problem",
        "Loose Components",
        "Lubrication Problem",
        "Burning Smell",
        "Other"
    ]
)


# =================================================
# PROBLEM DESCRIPTION
# =================================================

st.header("📝 Problem Description")

problem_description = st.text_area(
    "Describe the machine problem:",
    placeholder=(
        "Example: The pump is producing unusual noise and vibration "
        "during operation. Flow rate has decreased."
    ),
    height=120
)


# =================================================
# OPERATING CONDITION
# =================================================

operating_condition = st.text_area(
    "Operating Condition:",
    placeholder=(
        "Example: Machine is operating continuously at normal load."
    ),
    height=100
)


# =================================================
# ADDITIONAL OBSERVATIONS
# =================================================

additional_observations = st.text_area(
    "Additional Observations:",
    placeholder=(
        "Example: Temperature is slightly higher than normal."
    ),
    height=100
)


st.divider()


# =================================================
# AI AGENT WORKFLOW
# =================================================

st.header("🤖 AI Agent Workflow")

workflow = [
    (
        "1",
        "Problem Analysis",
        "Understands the machine problem and symptoms."
    ),
    (
        "2",
        "Fault Diagnosis",
        "Identifies possible mechanical causes."
    ),
    (
        "3",
        "Maintenance Planning",
        "Creates practical maintenance actions."
    ),
    (
        "4",
        "Safety & Final Report",
        "Reviews the information and creates the final report."
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


# =================================================
# ANALYZE BUTTON
# =================================================

if st.button(
    "🔍 Analyze Machine",
    type="primary",
    use_container_width=True
):

    if not problem_description.strip():

        st.warning(
            "Please describe the machine problem before starting the analysis."
        )

        st.stop()


    # =================================================
    # PREPARE MACHINE INFORMATION
    # =================================================

    selected_symptoms = ", ".join(symptoms)

    if not selected_symptoms:

        selected_symptoms = "No specific symptoms selected."


    machine_problem = f"""
MACHINE INFORMATION

Machine Type: {machine_type}
Machine ID / Name: {machine_id}
Manufacturer: {manufacturer}
Model: {model}
Machine Age: {machine_age}
Operating Hours: {operating_hours}
Operating Speed: {operating_speed}
Load Condition: {load_condition}
Last Maintenance: {last_maintenance}

SELECTED SYMPTOMS

{selected_symptoms}

PROBLEM DESCRIPTION

{problem_description}

OPERATING CONDITION

{operating_condition}

ADDITIONAL OBSERVATIONS

{additional_observations}
"""


    # =================================================
    # RUN MECHCARE AI
    # =================================================

    with st.spinner(
        "🤖 MechCare AI is analyzing the machine..."
    ):

        try:

            result = asyncio.run(
                run_mechcare(machine_problem)
            )

            diagnosis_result = result["diagnosis"]

            final_report = result["final_report"]


        except Exception as e:

            st.error(
                "An error occurred while analyzing the machine."
            )

            st.exception(e)

            st.stop()


    st.success(
        "✅ Machine analysis completed successfully!"
    )

    st.divider()


    # =================================================
    # MACHINE HEALTH DASHBOARD
    # =================================================

    st.subheader("📊 Machine Health Dashboard")

    report_text = final_report

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


    st.divider()


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


    st.divider()


    # =================================================
    # MAINTENANCE CHECKLIST
    # =================================================

    st.subheader(
        "🔧 Maintenance Checklist"
    )

    st.caption(
        "Use these checks as a practical guide during inspection."
    )

    check1, check2 = st.columns(2)


    with check1:

        st.checkbox(
            "☐ Check machine for unusual noise"
        )

        st.checkbox(
            "☐ Check for excessive vibration"
        )

        st.checkbox(
            "☐ Check temperature"
        )

        st.checkbox(
            "☐ Check for leakage"
        )


    with check2:

        st.checkbox(
            "☐ Check lubrication condition"
        )

        st.checkbox(
            "☐ Check loose components"
        )

        st.checkbox(
            "☐ Check alignment"
        )

        st.checkbox(
            "☐ Check operating conditions"
        )


    st.divider()


    # =================================================
    # FINAL ENGINEERING REPORT
    # =================================================

    st.subheader(
        "📋 Engineering Analysis Report"
    )

    st.markdown(
        final_report
    )


    st.divider()


    # =================================================
    # DISCLAIMER
    # =================================================

    st.caption(
        "⚠️ MechCare AI provides an initial engineering "
        "decision-support analysis. Always follow manufacturer "
        "procedures and consult a qualified engineer or technician "
        "before performing maintenance or repairs."
    )
