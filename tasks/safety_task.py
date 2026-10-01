
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
    "## Final Summary\n\n"
    "Under each heading, provide the relevant information.\n"
    "Use short, clear sentences.\n"
    "Maximum 300 words."
),

        agent=agent
    )
