
from crewai import Task

def create_maintenance_planning_task(agent):
    return Task(
        description=(
            "Create a short maintenance plan using the machine problem "
            "and possible causes from the previous agent."
        ),

        expected_output=(
            "Give only:\n"
            "Immediate checks: maximum 3 short points\n"
            "Maintenance actions: maximum 3 short points\n"
            "Preventive maintenance: maximum 2 short points\n"
            "Safety precautions: maximum 3 short points\n"
            "Maximum 200 words."
        ),

        agent=agent
    )
