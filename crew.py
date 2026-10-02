from llm_config import create_llm

from agents.problem_agent import create_problem_analysis_agent
from agents.diagnosis_agent import create_fault_diagnosis_agent
from agents.maintenance_agent import create_maintenance_planning_agent
from agents.safety_agent import create_safety_final_report_agent

from tasks.problem_task import create_problem_analysis_task
from tasks.diagnosis_task import create_fault_diagnosis_task
from tasks.maintenance_task import create_maintenance_planning_task
from tasks.safety_task import create_safety_final_report_task


async def run_mechcare(machine_problem):

    # Create LLM
    llm = create_llm()


    # =========================
    # AGENT 1 — PROBLEM ANALYSIS
    # =========================

    problem_agent = create_problem_analysis_agent(llm)
    problem_task = create_problem_analysis_task(problem_agent)

    problem_task.description += f"""

USER MACHINE INFORMATION:

{machine_problem}
"""

    problem_result = await problem_agent.aexecute_task(problem_task)


    # =========================
    # AGENT 2 — FAULT DIAGNOSIS
    # =========================

    diagnosis_agent = create_fault_diagnosis_agent(llm)
    diagnosis_task = create_fault_diagnosis_task(diagnosis_agent)

    diagnosis_task.description += f"""

MACHINE PROBLEM:

{machine_problem}

PROBLEM ANALYSIS FROM AGENT 1:

{problem_result}
"""

    diagnosis_result = await diagnosis_agent.aexecute_task(diagnosis_task)


    # =========================
    # AGENT 3 — MAINTENANCE
    # =========================

    maintenance_agent = create_maintenance_planning_agent(llm)
    maintenance_task = create_maintenance_planning_task(maintenance_agent)

    maintenance_task.description += f"""

MACHINE PROBLEM:

{machine_problem}

FAULT DIAGNOSIS FROM AGENT 2:

{diagnosis_result}
"""

    maintenance_result = await maintenance_agent.aexecute_task(maintenance_task)


    # =========================
    # AGENT 4 — SAFETY & REPORT
    # =========================

    safety_agent = create_safety_final_report_agent(llm)
    safety_task = create_safety_final_report_task(safety_agent)

    safety_task.description += f"""

MACHINE INFORMATION:

{machine_problem}

FAULT DIAGNOSIS FROM AGENT 2:

{diagnosis_result}

MAINTENANCE PLAN FROM AGENT 3:

{maintenance_result}
"""

    safety_result = await safety_agent.aexecute_task(safety_task)


    # =========================
    # FINAL RESULT
    # =========================

    return {
        "diagnosis": str(diagnosis_result),
        "final_report": str(safety_result)
    }
