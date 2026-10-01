
from crewai import Task

def create_safety_final_report_task(agent):
    return Task(
        description=(
            "Create a short final machine maintenance report using the "
            "maintenance plan provided by the previous agent."
        ),

        expected_output=(
            "Give only:\n"
            "Machine: one line\n"
            "Problem: one line\n"
            "Possible causes: maximum 3 short points\n"
            "Recommended checks: maximum 3 short points\n"
            "Maintenance actions: maximum 3 short points\n"
            "Safety: maximum 3 short points\n"
            "Priority: Low, Medium, or High\n"
            "Final summary: maximum 2 sentences\n"
            "Maximum 300 words."
        ),

        agent=agent
    )
