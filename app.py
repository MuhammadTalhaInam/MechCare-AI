import streamlit as st
import asyncio
import re

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


/* =========================================================
   HERO
   ========================================================= */

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


/* =========================================================
   SECTION
   ========================================================= */

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


/* =========================================================
   INPUTS
   ========================================================= */

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


/* =========================================================
   SELECT
   ========================================================= */

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}


/* =========================================================
   BUTTON
   ========================================================= */

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


/* =========================================================
   REPORT
   ========================================================= */

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


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1E293B;
}


/* =========================================================
   WORKFLOW
   ========================================================= */

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


/* =========================================================
   OUTPUT DASHBOARD
   ========================================================= */

.dashboard-card {
    background: linear-gradient(135deg, #111827, #16263A);
    border: 1px solid #1E5B83;
    border-radius: 16px;
    padding: 20px;
    min-height: 125px;
    margin-bottom: 15px;
}

.dashboard-icon {
    font-size: 30px;
}

.dashboard-label {
    color: #94A3B8;
    font-size: 13px;
    margin-top: 5px;
}

.dashboard-value {
    color: #F8FAFC;
    font-size: 18px;
    font-weight: 700;
    margin-top: 5px;
}


/* =========================================================
   PRIORITY
   ========================================================= */

.priority-high {
    background: linear-gradient(135deg, #3B1118, #58151C);
    border: 1px solid #991B1B;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 25px;
}

.priority-medium {
    background: linear-gradient(135deg, #3B2A0B, #4A3410);
    border: 1px solid #A16207;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 25px;
}

.priority-low {
    background: linear-gradient(135deg, #0B3024, #0F3D2E);
    border: 1px solid #15803D;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 25px;
}

.priority-title {
    color: #F8FAFC;
    font-size: 23px;
    font-weight: 800;
}

.priority-description {
    color: #CBD5E1;
    font-size: 14px;
    margin-top: 5px;
}


/* =========================================================
   INDICATOR CARDS
   ========================================================= */

.indicator-alert {
    background-color: #3B1118;
    border: 1px solid #991B1B;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.indicator-warning {
    background-color: #3B2A0B;
    border: 1px solid #A16207;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.indicator-normal {
    background-color: #0B3024;
    border: 1px solid #15803D;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.indicator-unknown {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.indicator-icon {
    font-size: 28px;
}

.indicator-name {
    color: #F8FAFC;
    font-weight: 700;
    margin-top: 5px;
}

.indicator-status {
    color: #CBD5E1;
    font-size: 12px;
    margin-top: 3px;
}


/* =========================================================
   SAFETY NOTICE
   ========================================================= */

.safety-notice {
    background-color: #172033;
    border-left: 5px solid #38BDF8;
    border-radius: 10px;
    padding: 18px;
    margin-top: 25px;
    color: #CBD5E1;
}

</style>
""", unsafe_allow_html=True)


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


        # =================================================
        # OUTPUT DASHBOARD
        # =================================================

        st.markdown(
            "## 📊 Machine Health Overview"
        )

        st.caption(
            "Visual indicators are based on the information provided "
            "by the user and the AI-generated maintenance report."
        )


        # =================================================
        # PRIORITY DETECTION
        # =================================================

        result_text = str(final_result)

        priority_match = re.search(
            r"priority\s*[:\-]\s*(high|medium|low)",
            result_text,
            re.IGNORECASE
        )

        if priority_match:
            priority = priority_match.group(1).upper()
        else:
            priority = "REVIEW"


        if priority == "HIGH":

            st.markdown(
                """
                <div class="priority-high">
                    <div class="priority-title">
                        🔴 HIGH PRIORITY
                    </div>
                    <div class="priority-description">
                        Immediate inspection and appropriate maintenance
                        attention are recommended.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        elif priority == "MEDIUM":

            st.markdown(
                """
                <div class="priority-medium">
                    <div class="priority-title">
                        🟡 MEDIUM PRIORITY
                    </div>
                    <div class="priority-description">
                        The machine should be inspected and monitored
                        according to the maintenance recommendations.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        elif priority == "LOW":

            st.markdown(
                """
                <div class="priority-low">
                    <div class="priority-title">
                        🟢 LOW PRIORITY
                    </div>
                    <div class="priority-description">
                        Continue monitoring the machine and follow
                        the recommended preventive maintenance.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="priority-medium">
                    <div class="priority-title">
                        🟡 PRIORITY: REVIEW
                    </div>
                    <div class="priority-description">
                        Review the AI-generated report and confirm the
                        machine condition through appropriate inspection.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # DETECTED PROBLEM INDICATORS
        # =================================================

        st.markdown(
            "### 🔍 Detected Problem Indicators"
        )

        combined_input = (
            problem_description
            + " "
            + operating_condition
            + " "
            + additional_observations
        ).lower()


        def indicator_status(keywords):

            for word in keywords:
                if word in combined_input:
                    return True

            return False


        vibration_detected = indicator_status(
            [
                "vibration",
                "vibrating",
                "shaking",
                "oscillation"
            ]
        )

        noise_detected = indicator_status(
            [
                "noise",
                "noisy",
                "grinding",
                "rattling",
                "humming",
                "sound"
            ]
        )

        temperature_detected = indicator_status(
            [
                "hot",
                "heating",
                "heated",
                "temperature",
                "overheating",
                "hotter"
            ]
        )

        performance_detected = indicator_status(
            [
                "reduced",
                "reduction",
                "slow",
                "low output",
                "low flow",
                "decreased",
                "decrease",
                "performance",
                "pressure"
            ]
        )


        indicators = st.columns(4)


        with indicators[0]:

            if vibration_detected:

                st.markdown(
                    """
                    <div class="indicator-warning">
                        <div class="indicator-icon">📳</div>
                        <div class="indicator-name">
                            Vibration
                        </div>
                        <div class="indicator-status">
                            Detected in input
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="indicator-unknown">
                        <div class="indicator-icon">📳</div>
                        <div class="indicator-name">
                            Vibration
                        </div>
                        <div class="indicator-status">
                            Not reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with indicators[1]:

            if noise_detected:

                st.markdown(
                    """
                    <div class="indicator-alert">
                        <div class="indicator-icon">🔊</div>
                        <div class="indicator-name">
                            Noise
                        </div>
                        <div class="indicator-status">
                            Abnormal noise reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="indicator-unknown">
                        <div class="indicator-icon">🔊</div>
                        <div class="indicator-name">
                            Noise
                        </div>
                        <div class="indicator-status">
                            Not reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with indicators[2]:

            if temperature_detected:

                st.markdown(
                    """
                    <div class="indicator-alert">
                        <div class="indicator-icon">🌡️</div>
                        <div class="indicator-name">
                            Temperature
                        </div>
                        <div class="indicator-status">
                            Heating reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="indicator-unknown">
                        <div class="indicator-icon">🌡️</div>
                        <div class="indicator-name">
                            Temperature
                        </div>
                        <div class="indicator-status">
                            Not reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with indicators[3]:

            if performance_detected:

                st.markdown(
                    """
                    <div class="indicator-warning">
                        <div class="indicator-icon">📉</div>
                        <div class="indicator-name">
                            Performance
                        </div>
                        <div class="indicator-status">
                            Reduced performance
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="indicator-normal">
                        <div class="indicator-icon">⚙️</div>
                        <div class="indicator-name">
                            Performance
                        </div>
                        <div class="indicator-status">
                            No reduction reported
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # =================================================
        # MACHINE SUMMARY
        # =================================================

        st.write("")

        st.markdown(
            "### ⚙️ Machine Summary"
        )

        summary = st.columns(3)


        with summary[0]:

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-icon">⚙️</div>
                    <div class="dashboard-label">
                        Machine Type
                    </div>
                    <div class="dashboard-value">
                        {machine_type}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        with summary[1]:

            age_value = (
                machine_age
                if machine_age.strip()
                else "Not provided"
            )

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-icon">📅</div>
                    <div class="dashboard-label">
                        Machine Age
                    </div>
                    <div class="dashboard-value">
                        {age_value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        with summary[2]:

            maintenance_value = (
                last_maintenance
                if last_maintenance.strip()
                else "Not provided"
            )

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-icon">🛠️</div>
                    <div class="dashboard-label">
                        Last Maintenance
                    </div>
                    <div class="dashboard-value">
                        {maintenance_value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # FINAL AI REPORT
        # =================================================

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


        # =================================================
        # SAFETY NOTICE
        # =================================================

        st.markdown(
            """
            <div class="safety-notice">
                <strong>🛡️ Safety Notice</strong><br>
                This AI-generated report is intended as engineering
                decision-support information. Equipment should be isolated
                and appropriate safety procedures should be followed before
                inspection or maintenance. Final decisions should be verified
                by a qualified engineer or technician.
            </div>
            """,
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
