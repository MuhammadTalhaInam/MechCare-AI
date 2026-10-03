from crewai import Task


def create_condition_monitoring_task(agent):
    return Task(
        description=(
            "Monitor and assess the current health condition of the user's "
            "machine using the available machine information. "
            "Identify abnormal behavior, early warning signs, possible "
            "degradation patterns, and the overall health condition. "
            "If enough information is available, estimate the remaining "
            "useful life. Do not give a final fault diagnosis."
        ),

        expected_output=(
            "Give the result in EXACTLY this format using Markdown:\n\n"

            "## Asset Health\n"
            "Health Status: [brief description of the current machine condition]\n"
            "Health Score: [number from 0-100 or Not Available]\n\n"

            "## Active Anomalies\n"
            "- [maximum 3 short points]\n\n"

            "## Early Warning Signs\n"
            "- [maximum 3 short points]\n\n"

            "## RUL Estimate\n"
            "RUL: [estimated remaining useful life if enough historical data "
            "exists, otherwise Not Available]\n\n"

            "## Alert Severity Level\n"
            "Severity: [Low, Medium, High, or Critical]\n\n"

            "## Recommended Next Action\n"
            "- [maximum 3 short points]\n\n"

            "IMPORTANT:\n"
            "Keep Health Status, Health Score, Severity, and Recommended Next "
            "Action as separate fields. Do not put Recommended Next Action "
            "inside Asset Health or Alert Severity.\n\n"

            "Maximum 250 words."
        ),

        agent=agent
    )
