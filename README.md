# ⚙️ MechCare AI

### AI-Based Machine Maintenance & Troubleshooting Assistant

MechCare AI is an **AI-powered machine maintenance and troubleshooting assistant** designed to help engineers, technicians, students, and machine operators understand machine problems and perform structured initial analysis.

The application collects **machine information, condition monitoring data, observed symptoms, and problem descriptions**, then processes the information through a **five-agent AI engineering workflow** to generate possible faults, diagnostic checks, maintenance recommendations, safety considerations, and a final engineering report.

---

## 🚀 Features

### 🤖 Multi-Agent Engineering Workflow

MechCare AI uses five specialized AI agents to analyze a machine problem step by step:

| Agent | Responsibility |
|---|---|
| 📈 **Condition Monitoring** | Evaluates machine condition, abnormal behavior, early warning signs, and predictive condition |
| 🔍 **Problem Analysis** | Analyzes the reported problem, symptoms, and missing information |
| 🧠 **Fault Diagnosis** | Identifies possible faults and suggests diagnostic checks |
| 🛠️ **Maintenance Planning** | Provides inspection and maintenance recommendations |
| 🛡️ **Safety & Final Report** | Reviews the analysis, considers safety, and generates the final engineering report |

---

## 📊 Condition Monitoring & Predictive Intelligence

The application analyzes available machine monitoring information and provides an AI-based assessment of:

- Machine condition
- Abnormal behavior
- Early warning signs
- Possible predictive condition
- Recommended next action

The application also recommends **additional data or measurements** that may help confirm a suspected machine fault.

---

## 🏭 Machine Profile

Users can enter important machine information, including:

- Machine Type
- Machine ID
- Manufacturer
- Machine Model
- Machine Age
- Operating Hours
- Operating Speed
- Load Condition
- Last Maintenance

### Supported Machine Types

- Centrifugal Pump
- Electric Motor
- Gearbox
- Compressor
- Fan
- Bearing System
- Turbine
- Other

---

## 📈 Condition Monitoring Inputs

Users can provide important machine operating measurements such as:

- 🌡️ Temperature (°C)
- 📳 Vibration (mm/s)
- 🔄 RPM
- 💨 Pressure (bar)
- 💧 Flow Rate (L/min)
- ⚡ Current (A)

These measurements are analyzed together with the machine information and observed symptoms.

---

## ⚠️ Observed Symptoms

Users can select one or multiple symptoms observed during machine operation.

Examples include:

- Unusual noise
- Excessive vibration
- Overheating
- Reduced performance
- Leakage
- Increased power consumption
- Slow or irregular operation
- Pressure or flow problems
- Loose components
- Lubrication problems
- Burning smell
- Other

---

## 🔍 Possible Faults & Diagnostic Checks

Based on the available information, MechCare AI identifies possible causes of the machine problem.

The system connects:

**Symptoms → Possible Causes → Diagnostic Checks**

This helps users understand what could be causing the problem and what checks may be useful for further investigation.

---

## 🛠️ Maintenance Checklist

MechCare AI provides a practical maintenance checklist containing checks such as:

- Check for unusual noise
- Check for excessive vibration
- Check temperature
- Check for leakage
- Check lubrication condition
- Check loose components
- Check alignment
- Check operating conditions

Users can mark individual checks as completed.

---

## 📋 Final Engineering Report

After the analysis, MechCare AI generates a consolidated engineering report containing relevant findings from the AI workflow.

The report can include:

- Problem summary
- Condition assessment
- Possible faults
- Diagnostic checks
- Maintenance recommendations
- Safety considerations
- Recommended next actions

---

## 🔊 AI Voice Reader

MechCare AI includes a browser-based voice reader that can read the generated engineering analysis aloud.

### Voice Controls

- ▶️ Play
- ⏸️ Pause
- ⏹️ Stop

### Adjustable Speed

The voice speed can be adjusted from:

**0.25× → 2×**

Available speeds:

`0.25×` `0.5×` `0.75×` `1×` `1.25×` `1.5×` `1.75×` `2×`

The voice reader can read the main AI analysis sections, including the condition monitoring results, recommended additional data, possible faults, and final engineering report.

---

## 📄 PDF Report

The final engineering analysis can be exported as a **PDF report**.

This makes it easier to save, share, and document the results of a machine troubleshooting case.

---

# 🧠 How MechCare AI Works

The overall workflow is:

```text
Machine Information
        ↓
Condition Monitoring Data
        ↓
Observed Symptoms
        ↓
Problem Description
        ↓
        AI Analysis
        ↓
┌───────────────────────────────┐
│  01 Condition Monitoring      │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  02 Problem Analysis          │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  03 Fault Diagnosis           │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  04 Maintenance Planning      │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  05 Safety & Final Report     │
└───────────────────────────────┘
        ↓
Engineering Analysis
        ↓
Voice Reader / PDF Report
```

---

# 🏗️ Project Architecture

MechCare AI is built around a modular multi-agent architecture.

### Main Components

```text
MechCare AI
│
├── app.py
│   └── Streamlit User Interface
│
├── crew.py
│   └── Multi-Agent Engineering Workflow
│
├── pdf_report.py
│   └── PDF Report Generation
│
└── requirements.txt
    └── Required Python Packages
```

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| 🐍 **Python** | Main programming language |
| 🎈 **Streamlit** | Web application interface |
| 🤖 **Groq API** | AI model integration |
| 🔄 **Multi-Agent Architecture** | Specialized engineering analysis |
| 🌐 **JavaScript Speech Synthesis** | Browser-based voice reader |
| 📄 **PDF Generation** | Engineering report export |

---

# 💻 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/mechcare-ai.git
```

Move into the project folder:

```bash
cd mechcare-ai
```

---

## 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 3. Configure Groq API Key

MechCare AI requires a **Groq API key** for AI analysis.

For local development, configure your Streamlit secrets with your API key.

Example:

```toml
GROQ_API_KEY = "your_api_key_here"
```

**Never commit your actual API key to GitHub.**

---

## 4. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 📁 Project Structure

```text
mechcare-ai/
│
├── app.py
├── crew.py
├── pdf_report.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🔐 Security

API credentials should always be stored securely.

Do not place your actual Groq API key directly inside:

```text
app.py
crew.py
```

or any other source file that will be uploaded to GitHub.

Use Streamlit secrets or environment variables instead.

---

# 🎯 Project Objectives

MechCare AI was developed with the following objectives:

- Combine **Mechanical Engineering + Artificial Intelligence**
- Simplify machine troubleshooting
- Structure engineering analysis using specialized AI agents
- Support condition monitoring
- Identify possible machine faults
- Recommend maintenance actions
- Provide safety-focused information
- Generate engineering reports
- Make AI-based engineering assistance easier to access

---

# 🔮 Future Improvements

Possible future enhancements include:

- 📊 Historical machine data
- 📈 Condition monitoring trend graphs
- 🚨 Automated anomaly detection
- 🔮 Advanced predictive maintenance
- 🗂️ Analysis history
- 🏭 More machine types and models
- 📅 Maintenance scheduling
- 📑 More detailed PDF reports
- 📱 Improved mobile interface
- 📊 Machine performance dashboards

---

# ⚠️ Disclaimer

MechCare AI is an **engineering decision-support and educational tool**.

The AI-generated results should be treated as preliminary guidance and should be verified using appropriate engineering measurements, inspections, manufacturer documentation, safety procedures, and qualified professional judgment before making maintenance or operational decisions.

---

# 👨‍💻 Project

**MechCare AI**

An AI-powered approach to **machine maintenance, condition monitoring, troubleshooting, and engineering decision support.**

---

## ⭐ If You Find This Project Useful

Consider giving the repository a ⭐ on GitHub and sharing your feedback or ideas for future improvements.

**Your ideas and suggestions are always welcome.**
