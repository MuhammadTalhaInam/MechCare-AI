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
            "Give the result in this format using Markdown:\n\n"

            "## Asset Health\n"
            "- Current health condition of the machine\n"
            "- Health score from 0-100 if enough information is available\n\n"

            "## Active Anomalies\n"
            "- Maximum 3 short points\n\n"

            "## Early Warning Signs\n"
            "- Maximum 3 short points\n\n"

            "## RUL Estimate\n"
            "- Estimated remaining useful life if enough information is available\n"
            "- Clearly state when there is not enough data for an estimate\n\n"

            "## Alert Severity Level\n"
            "- Low, Medium, High, or Critical\n\n"

            "## Recommended Next Action\n"
            "- Maximum 3 short points for the next engineering agent\n\n"

            "Maximum 250 words."
        ),

        agent=agent
    )
