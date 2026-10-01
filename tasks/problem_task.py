
from crewai import Task

def create_problem_analysis_task(agent):
    return Task(
        description=(
            "Analyze the user's machine problem. "
            "Give only the main symptoms and important observations. "
            "Do not give a diagnosis."
        ),

        expected_output=(
            "Give only:\n"
            "Machine: one line\n"
            "Symptoms: maximum 3 short points\n"
            "Important observation: maximum 2 short points\n"
            "Missing information: maximum 2 short points\n"
            "Maximum 150 words."
        ),

        agent=agent
    )
