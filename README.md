# ⚙️ MechCare AI

### Multi-Agent Machine Maintenance & Troubleshooting Assistant

MechCare AI is a multi-agent AI application designed to help users analyze common machine problems, identify possible causes, and generate practical maintenance guidance.

The system uses multiple specialized AI agents to analyze a machine problem step by step and produce a structured maintenance report.

> **Note:** MechCare AI provides AI-generated decision-support guidance. It does not replace a qualified engineer, technician, manufacturer instructions, or proper maintenance procedures.

---

## 🚀 Features

- Analyze machine problems using natural language
- Identify possible mechanical causes
- Recommend inspection and maintenance actions
- Provide safety considerations
- Assign a maintenance priority
- Generate a structured final maintenance report
- Simple and user-friendly Streamlit interface
- Multi-agent workflow using CrewAI
- Powered by Groq LLM

---

## 🤖 Multi-Agent Workflow

MechCare AI uses four specialized AI agents:

**1. Problem Analysis Agent**

Analyzes the machine information, identifies symptoms, and organizes the available information.

**2. Fault Diagnosis Agent**

Analyzes the symptoms and identifies possible mechanical or operational causes.

**3. Maintenance Planning Agent**

Converts the possible causes into practical inspection and maintenance actions.

**4. Safety & Final Report Agent**

Reviews the previous outputs and generates the final report with safety considerations and priority.

### Workflow

```text
User
  ↓
Problem Analysis Agent
  ↓
Fault Diagnosis Agent
  ↓
Maintenance Planning Agent
  ↓
Safety & Final Report Agent
  ↓
Final Maintenance Report
```

---

## 🔧 Supported Machine Types

The application can analyze problems related to:

- Centrifugal Pump
- Electric Motor
- Gearbox
- Compressor
- Fan
- Bearing System
- Turbine
- Other machines

---

## 🛠️ Technologies Used

- Python
- CrewAI
- Groq
- Streamlit
- Large Language Models (LLMs)
- Google Colab
- GitHub

---

## 📂 Project Structure

```text
MechCare-AI/
│
├── app.py
├── crew.py
├── llm_config.py
├── requirements.txt
│
├── agents/
│   ├── problem_agent.py
│   ├── diagnosis_agent.py
│   ├── maintenance_agent.py
│   └── safety_agent.py
│
└── tasks/
    ├── problem_task.py
    ├── diagnosis_task.py
    ├── maintenance_task.py
    └── safety_task.py
```

---

## ⚙️ How It Works

The user enters information such as:

- Machine type
- Problem description
- Operating condition
- Machine age
- Last maintenance
- Additional observations

The information is then passed through the four specialized AI agents.

Each agent performs a specific task and passes its result to the next agent.

Finally, the Safety & Final Report Agent combines the information into a structured maintenance report.

---

## 🖥️ Application Output

The final report contains:

- Machine
- Problem
- Possible Causes
- Recommended Checks
- Maintenance Actions
- Safety
- Priority
- Final Summary

---

## 🔐 Environment Variable

The application requires a Groq API key.

Set the following environment variable:

```text
GROQ_API_KEY
```

For Streamlit Cloud, add the key through the application's **Secrets** settings.

**Never commit your API key to GitHub.**

---

## 🌐 Deployment

The application is designed to run using **Streamlit** and can be deployed through Streamlit Community Cloud.

---

## 🎯 Project Objective

The main objective of MechCare AI is to demonstrate how multi-agent AI can be applied to mechanical engineering and machine maintenance.

The project combines mechanical engineering knowledge with Generative AI and agent-based workflows to provide an easy-to-use maintenance assistance system.

---

## 👨‍💻 Project

**MechCare AI**

Developed as a Generative & Agentic AI project with a focus on applying AI to mechanical engineering and machine maintenance.
