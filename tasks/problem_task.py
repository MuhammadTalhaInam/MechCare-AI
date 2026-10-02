from crewai import Task


def create_problem_analysis_task(agent):
    return Task(
        description=(
            "Analyze the user's machine problem. "
            "Identify the main symptoms, important observations, "
            "missing information, and additional measurements or data "
            "that would help confirm the problem. "
            "Do not give a diagnosis."
        ),

        expected_output=(
            "Give the result in this format using Markdown:\n\n"

            "## Symptoms\n"
            "- Maximum 3 short points\n\n"

            "## Important Observations\n"
            "- Maximum 2 short points\n\n"

            "## Missing Information\n"
            "- Maximum 2 short points\n\n"

            "## Additional Data Recommended\n"
            "- Maximum 5 measurements or pieces of information\n"
            "- Only recommend data relevant to this machine and problem\n\n"

            "Maximum 200 words."
        ),

        agent=agent
    )
