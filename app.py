
import streamlit as st
import asyncio

from crew import run_mechcare


# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide"
)


# =========================
# TITLE
# =========================

st.title("⚙️ MechCare AI")

st.subheader("Multi-Agent Machine Maintenance & Troubleshooting Assistant")

st.write(
    "Enter the machine information below and MechCare AI will analyze "
    "the problem and generate a maintenance report."
)


# =========================
# MACHINE INFORMATION
# =========================

st.header("Machine Information")

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

problem_description = st.text_area(
    "Problem Description",
    placeholder="Describe the problem, symptoms, noise, vibration, leakage, etc."
)

operating_condition = st.text_area(
    "Operating Condition",
    placeholder="Example: Running continuously at normal operating speed."
)

machine_age = st.text_input(
    "Machine Age",
    placeholder="Example: 3 years"
)

last_maintenance = st.text_input(
    "Last Maintenance",
    placeholder="Example: 6 months ago"
)

additional_observations = st.text_area(
    "Additional Observations",
    placeholder="Add any other observations or unusual behavior."
)


# =========================
# ANALYZE BUTTON
# =========================

if st.button("🔍 Analyze Machine", type="primary"):

    if not problem_description.strip():

        st.warning("Please enter the problem description.")

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
            "MechCare AI is analyzing the machine..."
        ):

            final_result = asyncio.run(
                run_mechcare(machine_problem)
            )

        st.success("Analysis completed!")

st.header("📋 Final Maintenance Report")

st.markdown(
    """
    <style>
    .stMarkdown {
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(final_result)
