from crewai import Task


def create_fault_diagnosis_task(agent):
    return Task(
        description=(
            "Analyze the machine problem and the problem analysis from Agent 1. "
            "Identify the most likely possible mechanical or operational causes. "
            "For each possible cause, explain why it may be related to the symptoms "
            "and provide a simple confirmation check. "
            "Do not confirm any fault because this is only an initial diagnosis."
        ),

        expected_output=(
    "Give the result in this format using Markdown:\n\n"

    "## **Possible Cause 1: [cause]**\n"
    "**Why:** [short reason]\n"
    "**How to Confirm:** [simple inspection or measurement]\n\n"

    "## **Possible Cause 2: [cause]**\n"
    "**Why:** [short reason]\n"
    "**How to Confirm:** [simple inspection or measurement]\n\n"

    "## **Possible Cause 3: [cause]**\n"
    "**Why:** [short reason]\n"
    "**How to Confirm:** [simple inspection or measurement]\n\n"

    "## **Possible Cause 4: [cause]**\n"
    "**Why:** [short reason]\n"
    "**How to Confirm:** [simple inspection or measurement]\n\n"

    "Use only the causes that are relevant to the machine problem. "
    "Maximum 4 possible causes. "
    "Keep the language simple and practical. "
    "Maximum 250 words."
),

        agent=agent
    )
