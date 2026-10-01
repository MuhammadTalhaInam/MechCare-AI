
from crewai import Task

def create_fault_diagnosis_task(agent):
    return Task(
        description=(
            "Analyze the machine problem and identify the most likely "
            "possible causes. Give a short reason and a simple check "
            "for each cause. Do not confirm any fault."
        ),

        expected_output=(
            "Give only:\n"
            "Possible causes: maximum 4\n"
            "Reason: one short sentence for each cause\n"
            "Confirmation check: one short sentence for each cause\n"
            "Maximum 200 words."
        ),

        agent=agent
    )
