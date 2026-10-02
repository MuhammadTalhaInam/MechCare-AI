from crewai import Task

def create_safety_final_report_task(agent):
    return Task(
        description=(
            "Create a short final machine maintenance report using the "
            "maintenance plan provided by the previous agent."
        ),

        expected_output=(
            "Create the report using exactly these Markdown headings:\n\n"
            "## Machine\n"
            "## Problem\n"
            "## Possible Causes\n"
            "## Recommended Checks\n"
            "## Maintenance Actions\n"
            "## Safety\n"
            "## Priority\n"
            "## Engineering Explanation\n"
            "## Final Summary\n\n"
            "Under each heading, provide the relevant information.\n"
            "For Engineering Explanation, briefly explain the mechanical or "
            "engineering reason behind the possible problem in simple language.\n"
            "Use short, clear sentences that an engineering student can understand.\n"
            "Do not introduce new faults that were not identified by the previous agents.\n"
            "Use short, clear sentences.\n"
            "Maximum 350 words."
        ),

        agent=agent
    )
