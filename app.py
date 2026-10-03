import streamlit as st
import asyncio
import json
import streamlit.components.v1 as components

from crew import run_mechcare
from pdf_report import create_pdf_report


# =========================================================
# VOICE READER
# =========================================================

def speak_text(text):

    # Convert the report into safe JavaScript text
    report_json = json.dumps(str(text))

    components.html(
        f"""
        <div style="
            background:#0b1928;
            border:1px solid #245276;
            border-radius:18px;
            padding:20px;
            color:#dbeafe;
            font-family:Arial, sans-serif;
        ">

            <h3 style="
                margin-top:0;
                color:#f8fafc;
            ">
                🔊 Listen to MechCare AI Results
            </h3>

            <p style="
                color:#94a3b8;
                margin-bottom:15px;
            ">
                Listen to the complete AI analysis and change the
                speaking speed according to your preference.
            </p>

            <div style="
                display:flex;
                flex-wrap:wrap;
                gap:10px;
                align-items:center;
            ">

                <button
                    onclick="playSpeech()"
                    style="
                        padding:9px 18px;
                        border:none;
                        border-radius:8px;
                        cursor:pointer;
                        font-size:14px;
                    "
                >
                    ▶️ Play
                </button>

                <button
                    onclick="pauseSpeech()"
                    style="
                        padding:9px 18px;
                        border:none;
                        border-radius:8px;
                        cursor:pointer;
                        font-size:14px;
                    "
                >
                    ⏸️ Pause
                </button>

                <button
                    onclick="stopSpeech()"
                    style="
                        padding:9px 18px;
                        border:none;
                        border-radius:8px;
                        cursor:pointer;
                        font-size:14px;
                    "
                >
                    ⏹️ Stop
                </button>

                <label style="
                    color:#cbd5e1;
                    font-size:14px;
                ">
                    Speed:
                </label>

                <select
                    id="speed"
                    onchange="changeSpeed()"
                    style="
                        padding:8px 12px;
                        border-radius:7px;
                        border:1px solid #475569;
                        background:#172b40;
                        color:#f8fafc;
                        font-size:14px;
                    "
                >
                    <option value="0.25">0.25×</option>
                    <option value="0.5">0.5×</option>
                    <option value="0.75">0.75×</option>
                    <option value="1" selected>1×</option>
                    <option value="1.25">1.25×</option>
                    <option value="1.5">1.5×</option>
                    <option value="1.75">1.75×</option>
                    <option value="2">2×</option>
                </select>

            </div>

            <div
                id="voiceStatus"
                style="
                    margin-top:15px;
                    color:#7dd3fc;
                    font-size:14px;
                "
            >
                Ready to play
            </div>

        </div>


        <script>

        const rawReportText = {report_json};


        // -------------------------------------------------
        // CLEAN TEXT FOR VOICE
        // -------------------------------------------------
        // This cleaning is ONLY for the voice.
        // The original report displayed in Streamlit
        // remains completely unchanged.

        const reportText = rawReportText

            // Remove Markdown heading symbols
            .replace(/^#+\\s*/gm, "")

            // Remove bold Markdown
            .replace(/\\*\\*(.*?)\\*\\*/g, "$1")

            // Remove italic Markdown
            .replace(/\\*(.*?)\\*/g, "$1")

            // Remove inline code formatting
            .replace(/`(.*?)`/g, "$1")

            // Remove Markdown horizontal lines
            .replace(/^(---+|___+|\\*\\*\\*+)\\s*$/gm, "")

            // Remove bullet symbols
            .replace(/^\\s*[-*+]\\s+/gm, "")

            // Remove numbered-list Markdown formatting
            .replace(/^\\s*\\d+[.)]\\s+/gm, "")

            // Remove remaining Markdown characters
            .replace(/^\\s*[#*_]+\\s*/gm, "")

            // Clean extra spaces
            .replace(/[ \\t]+/g, " ")

            // Clean excessive blank lines
            .replace(/\\n\\n+/g, "\\n\\n")

            .trim();


        // =================================================
        // MOBILE-FRIENDLY SPEECH SYSTEM
        // =================================================

        let speech = null;

        let currentSpeed = 1;

        let isPaused = false;

        let isStopped = true;

        let speechSession = 0;

        let currentChunkIndex = 0;

        let currentChunkPosition = 0;

        let speechStartPosition = 0;

        let isChangingSpeed = false;

        let availableVoice = null;

        let pendingAction = null;


        // =================================================
        // SPLIT REPORT INTO SMALLER SPEECH CHUNKS
        // =================================================

        function createSpeechChunks(text) {{

            const normalizedText =
                text.replace(/\\s+/g, " ").trim();


            if (!normalizedText) {{
                return [];
            }}


            const sentences =
                normalizedText.match(
                    /[^.!?]+[.!?]+|[^.!?]+$/g
                ) || [normalizedText];


            const chunks = [];

            let currentChunk = "";


            sentences.forEach(function(sentence) {{

                const cleanSentence =
                    sentence.trim();


                if (!cleanSentence) {{
                    return;
                }}


                if (
                    (currentChunk + " " + cleanSentence).length
                    <= 450
                ) {{

                    currentChunk =
                        currentChunk
                            ? currentChunk + " " + cleanSentence
                            : cleanSentence;

                }} else {{

                    if (currentChunk) {{
                        chunks.push(currentChunk);
                    }}

                    currentChunk = cleanSentence;
                }}

            }});


            if (currentChunk) {{
                chunks.push(currentChunk);
            }}


            return chunks;
        }}


        const speechChunks =
            createSpeechChunks(reportText);


        // =================================================
        // FIND MOBILE-COMPATIBLE VOICE
        // =================================================

        function loadAvailableVoice() {{

            if (!("speechSynthesis" in window)) {{
                return;
            }}


            const voices =
                window.speechSynthesis.getVoices();


            if (!voices || voices.length === 0) {{
                return;
            }}


            availableVoice =
                voices.find(function(voice) {{

                    return voice.lang === "en-US";

                }});


            if (!availableVoice) {{

                availableVoice =
                    voices.find(function(voice) {{

                        return voice.lang === "en-GB";

                    }});

            }}


            if (!availableVoice) {{

                availableVoice =
                    voices.find(function(voice) {{

                        return voice.lang &&
                            voice.lang.toLowerCase().startsWith("en");

                    }});

            }}


            if (!availableVoice && voices.length > 0) {{

                availableVoice = voices[0];

            }}

        }}


        if ("speechSynthesis" in window) {{

            loadAvailableVoice();

            window.speechSynthesis.onvoiceschanged =
                function() {{

                    loadAvailableVoice();

                }};

        }}


        // =================================================
        // UPDATE STATUS
        // =================================================

        function updateStatus(message) {{

            const status =
                document.getElementById("voiceStatus");


            if (status) {{

                status.innerText = message;

            }}

        }}


        // =================================================
        // CREATE AND START CURRENT CHUNK
        // =================================================

        function speakCurrentChunk(startPosition) {{

            if (!("speechSynthesis" in window)) {{

                updateStatus(
                    "❌ Text-to-speech is not supported by this browser."
                );

                return;
            }}


            if (currentChunkIndex >= speechChunks.length) {{

                currentChunkIndex = 0;

                currentChunkPosition = 0;

                speechStartPosition = 0;

                speech = null;

                isPaused = false;

                isStopped = false;

                isChangingSpeed = false;

                pendingAction = null;

                updateStatus("✅ Finished");

                return;
            }}


            const chunk =
                speechChunks[currentChunkIndex];


            if (!chunk) {{

                currentChunkIndex++;

                currentChunkPosition = 0;

                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;

            }}


            let position =
                typeof startPosition === "number"
                    ? startPosition
                    : currentChunkPosition;


            if (position < 0) {{
                position = 0;
            }}


            if (position >= chunk.length) {{

                currentChunkIndex++;

                currentChunkPosition = 0;

                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;

            }}


            const remainingText =
                chunk.substring(position);


            if (!remainingText.trim()) {{

                currentChunkIndex++;

                currentChunkPosition = 0;

                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;

            }}


            currentChunkPosition = position;

            speechStartPosition = position;


            speechSession++;

            const thisSession =
                speechSession;


            speech =
                new SpeechSynthesisUtterance(
                    remainingText
                );


            speech.rate =
                currentSpeed;

            speech.pitch =
                1;

            speech.volume =
                1;


            if (availableVoice) {{

                speech.voice =
                    availableVoice;

            }}


            if (
                availableVoice &&
                availableVoice.lang
            ) {{

                speech.lang =
                    availableVoice.lang;

            }} else {{

                speech.lang =
                    "en-US";

            }}


            isStopped = false;


            // -------------------------------------------------
            // START
            // -------------------------------------------------

            speech.onstart = function() {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                isPaused = false;


                updateStatus(
                    "🔊 Speaking at " +
                    currentSpeed +
                    "×..."
                );

            }};


            // -------------------------------------------------
            // TRACK CURRENT POSITION
            // -------------------------------------------------

            speech.onboundary = function(event) {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                if (
                    typeof event.charIndex === "number"
                ) {{

                    currentChunkPosition =
                        speechStartPosition +
                        event.charIndex;

                }}

            }};


            // -------------------------------------------------
            // PAUSE EVENT
            // -------------------------------------------------
            // IMPORTANT:
            // The pause event itself gives us charIndex.
            // This is more accurate than relying only
            // on the previous boundary event.

            speech.onpause = function(event) {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                if (
                    event &&
                    typeof event.charIndex === "number"
                ) {{

                    currentChunkPosition =
                        speechStartPosition +
                        event.charIndex;

                }}


                isPaused = true;


                if (pendingAction === "speed") {{

                    updateStatus(
                        "🔄 Changing speed..."
                    );

                }} else {{

                    updateStatus(
                        "⏸️ Paused — press Play to continue"
                    );

                }}

            }};


            // -------------------------------------------------
            // RESUME EVENT
            // -------------------------------------------------

            speech.onresume = function() {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                isPaused = false;


                updateStatus(
                    "🔊 Speaking at " +
                    currentSpeed +
                    "×..."
                );

            }};


            // -------------------------------------------------
            // FINISHED CURRENT CHUNK
            // -------------------------------------------------

            speech.onend = function() {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                speech = null;


                // If the speech was manually paused,
                // DO NOT move to the next chunk.

                if (isPaused) {{
                    return;
                }}


                // If the user is changing speed,
                // DO NOT move to the next chunk.

                if (isChangingSpeed) {{
                    return;
                }}


                // Normal completion of this chunk.

                currentChunkIndex++;

                currentChunkPosition = 0;

                speechStartPosition = 0;


                if (isStopped) {{
                    return;
                }}


                setTimeout(function() {{

                    if (
                        thisSession !== speechSession ||
                        isStopped ||
                        isPaused ||
                        isChangingSpeed
                    ) {{
                        return;
                    }}


                    speakCurrentChunk(0);

                }}, 40);

            }};


            // -------------------------------------------------
            // ERROR
            // -------------------------------------------------

            speech.onerror = function(event) {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                if (
                    event.error === "canceled" ||
                    event.error === "interrupted"
                ) {{
                    return;
                }}


                speech = null;


                updateStatus(
                    "❌ Voice playback error. Please press Play again."
                );

            }};


            // -------------------------------------------------
            // START SPEECH
            // -------------------------------------------------

            window.speechSynthesis.speak(
                speech
            );

        }}


        // =================================================
        // PLAY / RESUME
        // =================================================

        function playSpeech() {{

            if (!("speechSynthesis" in window)) {{

                updateStatus(
                    "❌ Text-to-speech is not supported by this browser."
                );

                return;
            }}


            loadAvailableVoice();


            // -------------------------------------------------
            // RESUME AFTER PAUSE
            // -------------------------------------------------

            if (isPaused) {{

                const savedChunk =
                    currentChunkIndex;


                const savedPosition =
                    currentChunkPosition;


                isChangingSpeed = false;

                pendingAction = null;

                isStopped = false;


                // Invalidate the old utterance first.

                speechSession++;


                window.speechSynthesis.cancel();

                speech = null;


                // Restore exactly the saved location.

                currentChunkIndex =
                    savedChunk;

                currentChunkPosition =
                    savedPosition;

                speechStartPosition =
                    savedPosition;

                isPaused = false;


                updateStatus(
                    "▶️ Continuing from saved position at " +
                    currentSpeed +
                    "×..."
                );


                setTimeout(function() {{

                    if (!isStopped) {{

                        speakCurrentChunk(
                            savedPosition
                        );

                    }}

                }}, 120);


                return;

            }}


            // -------------------------------------------------
            // IF ALREADY SPEAKING
            // -------------------------------------------------

            if (
                speech &&
                window.speechSynthesis.speaking
            ) {{

                return;

            }}


            // -------------------------------------------------
            // IF REPORT FINISHED
            // -------------------------------------------------

            if (
                currentChunkIndex >=
                speechChunks.length
            ) {{

                currentChunkIndex = 0;

                currentChunkPosition = 0;

                speechStartPosition = 0;

            }}


            isStopped = false;

            isPaused = false;

            isChangingSpeed = false;

            pendingAction = null;


            window.speechSynthesis.cancel();


            setTimeout(function() {{

                if (!isStopped) {{

                    speakCurrentChunk(
                        currentChunkPosition
                    );

                }}

            }}, 100);

        }}


        // =================================================
        // PAUSE
        // =================================================

        function pauseSpeech() {{

            if (
                !("speechSynthesis" in window)
            ) {{
                return;
            }}


            if (
                !speech ||
                !window.speechSynthesis.speaking ||
                isPaused
            ) {{
                return;
            }}


            // IMPORTANT:
            // Do NOT cancel here.
            //
            // We first use the browser's pause event.
            // That event provides charIndex, which lets
            // us save the current position accurately.

            pendingAction = "pause";


            window.speechSynthesis.pause();


            updateStatus(
                "⏸️ Pausing..."
            );

        }}


        // =================================================
        // STOP
        // =================================================

        function stopSpeech() {{

            if ("speechSynthesis" in window) {{

                speechSession++;

                isChangingSpeed = false;

                pendingAction = null;

                window.speechSynthesis.cancel();

                speech = null;

                currentChunkIndex = 0;

                currentChunkPosition = 0;

                speechStartPosition = 0;

                isPaused = false;

                isStopped = true;


                updateStatus(
                    "⏹️ Stopped — press Play to start again"
                );

            }}

        }}


        // =================================================
        // CHANGE SPEED
        // =================================================

        function changeSpeed() {{

            const selectedSpeed =
                parseFloat(
                    document.getElementById("speed").value
                );


            if (isNaN(selectedSpeed)) {{
                return;
            }}


            currentSpeed =
                selectedSpeed;


            if (!("speechSynthesis" in window)) {{
                return;
            }}


            // -------------------------------------------------
            // CURRENTLY SPEAKING
            // -------------------------------------------------

            if (
                speech &&
                window.speechSynthesis.speaking &&
                !isPaused
            ) {{

                isChangingSpeed = true;

                pendingAction = "speed";


                updateStatus(
                    "🔄 Changing speed to " +
                    currentSpeed +
                    "×..."
                );


                // IMPORTANT:
                // Pause FIRST.
                //
                // The onpause event will capture the
                // actual current charIndex.
                //
                // We do NOT immediately cancel because
                // that could lose the latest position.

                window.speechSynthesis.pause();


                // Wait for the browser to process
                // the pause event.

                setTimeout(function() {{

                    if (!isChangingSpeed) {{
                        return;
                    }}


                    const savedChunk =
                        currentChunkIndex;


                    const savedPosition =
                        currentChunkPosition;


                    // Invalidate the old utterance.

                    speechSession++;


                    window.speechSynthesis.cancel();

                    speech = null;


                    currentChunkIndex =
                        savedChunk;

                    currentChunkPosition =
                        savedPosition;

                    speechStartPosition =
                        savedPosition;

                    isPaused = false;


                    updateStatus(
                        "🔊 Speaking at " +
                        currentSpeed +
                        "×..."
                    );


                    setTimeout(function() {{

                        if (!isStopped) {{

                            isChangingSpeed = false;

                            pendingAction = null;


                            speakCurrentChunk(
                                savedPosition
                            );

                        }}

                    }}, 100);


                }}, 150);


                return;

            }}


            // -------------------------------------------------
            // CURRENTLY PAUSED
            // -------------------------------------------------

            if (
                isPaused
            ) {{

                // Do not restart.
                //
                // The selected speed will be used
                // when Play is pressed.

                updateStatus(
                    "⏸️ Paused — " +
                    currentSpeed +
                    "× selected. Press Play to continue."
                );

                return;

            }}

        }}

        </script>
        """,
        height=210
    )


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MechCare AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CHECKLIST STATE
# =========================================================

checklist_items = [
    "Check machine for unusual noise",
    "Check for excessive vibration",
    "Check temperature",
    "Check for leakage",
    "Check lubrication condition",
    "Check loose components",
    "Check alignment",
    "Check operating conditions"
]

for item in checklist_items:
    if item not in st.session_state:
        st.session_state[item] = False


# =========================================================
# AI ANALYSIS STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# =========================================================
# AGENT WORKFLOW STATE
# =========================================================

if "agents_completed" not in st.session_state:
    st.session_state.agents_completed = False


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #07111f 0%,
            #0b1728 50%,
            #101c2f 100%
        );
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #0d2238, #102d49);
        border: 1px solid #1e4d73;
        border-radius: 22px;
        padding: 35px;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: 46px;
        margin-bottom: 5px;
    }

    .hero h3 {
        color: #38bdf8;
        margin-top: 0;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.7;
    }

    /* Selected symptom */
    .symptom-box {
        background: #123653;
        border: 1px solid #1d668f;
        border-radius: 12px;
        padding: 12px 15px;
        color: #7dd3fc;
        margin-top: 10px;
    }

    /* Report */
    .report-box {
        background: #0b1928;
        border: 1px solid #245276;
        border-radius: 18px;
        padding: 25px;
        color: #dbeafe;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⚙️ MechCare AI</h1>
        <h3>AI-Powered Machine Maintenance & Troubleshooting Assistant</h3>
        <p>
            Describe your machine, operating conditions, and observed
            symptoms. MechCare AI uses a multi-agent engineering workflow
            to analyze the problem, identify possible causes, suggest
            maintenance actions, and generate a structured safety-focused
            report.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WORKFLOW
# =========================================================

st.subheader("🤖 How MechCare AI Works")

st.caption(
    "Your machine problem passes through four specialized AI agents. "
    "Each agent performs a different engineering task before the final report is generated."
)


workflow = [
    (
        "AGENT 01",
        "🔍 Problem Analysis Agent",
        "Analyzes machine information, symptoms, observations, and missing information."
    ),
    (
        "AGENT 02",
        "🧠 Fault Diagnosis Agent",
        "Examines symptoms and identifies possible mechanical and operational causes."
    ),
    (
        "AGENT 03",
        "🛠️ Maintenance Planning Agent",
        "Converts possible causes into practical inspection and maintenance actions."
    ),
    (
        "AGENT 04",
        "🛡️ Safety & Final Report Agent",
        "Reviews the previous results and creates the final safety-focused engineering report."
    )
]


workflow_columns = st.columns(4)

for column, agent in zip(workflow_columns, workflow):

    number, title, description = agent

    with column:

        st.info(
            f"**{number}**\n\n"
            f"### {title}\n\n"
            f"{description}"
        )


st.divider()


# =========================================================
# MACHINE PROFILE
# =========================================================

st.subheader("🏭 Machine Profile")

st.caption(
    "Provide basic information about the machine so the AI can understand its operating context."
)


MACHINE_MODELS = {

    "Centrifugal Pump": [
        "KSB Etanorm",
        "Grundfos CR",
        "Sulzer AHLSTAR",
        "Generic / Unknown"
    ],

    "Electric Motor": [
        "ABB M3BP",
        "Siemens SIMOTICS",
        "WEG W22",
        "Generic / Unknown"
    ],

    "Gearbox": [
        "SEW-Eurodrive",
        "Flender",
        "Bonfiglioli",
        "Generic / Unknown"
    ],

    "Compressor": [
        "Atlas Copco GA",
        "Ingersoll Rand",
        "Kaeser",
        "Generic / Unknown"
    ],

    "Fan": [
        "ABB Fan",
        "Siemens Fan",
        "Generic Industrial Fan",
        "Generic / Unknown"
    ],

    "Bearing System": [
        "SKF Bearing",
        "FAG Bearing",
        "NTN Bearing",
        "Generic / Unknown"
    ],

    "Turbine": [
        "Francis Turbine",
        "Pelton Turbine",
        "Kaplan Turbine",
        "Generic / Unknown"
    ],

    "Other": [
        "Generic Machine",
        "Custom Equipment",
        "Unknown"
    ]
}


# =========================================================
# MACHINE INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    machine_type = st.selectbox(
        "⚙️ Machine Type",
        [
            "Centrifugal Pump",
            "Electric Motor",
            "Gearbox",
            "Compressor",
            "Fan",
            "Bearing System",
            "Turbine",
            "Other"
        ]
    )


with col2:

    machine_id = st.selectbox(
        "🆔 Machine ID / Name",
        [
            "MCH-001",
            "MCH-002",
            "MCH-003",
            "MCH-004",
            "MCH-005",
            "MCH-006",
            "MCH-007",
            "MCH-008",
            "Other"
        ]
    )


with col3:

    manufacturer = st.selectbox(
        "🏢 Manufacturer",
        [
            "ABB",
            "Siemens",
            "WEG",
            "KSB",
            "Sulzer",
            "Grundfos",
            "Caterpillar",
            "General Electric",
            "Other / Unknown"
        ]
    )


col4, col5, col6 = st.columns(3)


with col4:

    model = st.selectbox(
        "🔧 Model",
        MACHINE_MODELS[machine_type]
    )


with col5:

    machine_age = st.selectbox(
        "📅 Machine Age",
        [
            "Less than 1 year",
            "1–2 years",
            "3–5 years",
            "6–10 years",
            "More than 10 years",
            "Unknown"
        ]
    )


with col6:

    operating_hours = st.selectbox(
        "⏱️ Operating Hours",
        [
            "Less than 2 hours/day",
            "2–4 hours/day",
            "4–8 hours/day",
            "8–12 hours/day",
            "More than 12 hours/day",
            "Continuous",
            "Unknown"
        ]
    )


col7, col8, col9 = st.columns(3)


with col7:

    operating_speed = st.selectbox(
        "🔄 Operating Speed",
        [
            "Below 500 RPM",
            "500–1000 RPM",
            "1000–1500 RPM",
            "1500–3000 RPM",
            "Above 3000 RPM",
            "Variable Speed",
            "Unknown"
        ]
    )


with col8:

    load_condition = st.selectbox(
        "⚡ Load Condition",
        [
            "Unknown",
            "No Load",
            "Light Load",
            "Moderate Load",
            "Heavy Load",
            "Variable Load"
        ]
    )


with col9:

    last_maintenance = st.selectbox(
        "🛠️ Last Maintenance",
        [
            "Less than 1 month ago",
            "1–3 months ago",
            "3–6 months ago",
            "6–12 months ago",
            "More than 1 year ago",
            "Unknown"
        ]
    )


st.divider()


# =========================================================
# SYMPTOMS
# =========================================================

st.subheader("🔍 Observed Symptoms")

st.caption(
    "Select all symptoms currently observed in the machine. "
    "You can select multiple symptoms."
)


symptom_options = [
    "🔊 Unusual Noise",
    "📳 Excessive Vibration",
    "🌡️ Overheating",
    "📉 Reduced Performance",
    "💧 Leakage",
    "⚡ Increased Power Consumption",
    "🔄 Slow / Irregular Operation",
    "💨 Pressure / Flow Problem",
    "🔩 Loose Components",
    "🛢️ Lubrication Problem",
    "🔥 Burning Smell",
    "⚠️ Other"
]


selected_symptoms = st.multiselect(
    "Select observed symptoms",
    symptom_options,
    placeholder="Choose one or more symptoms..."
)


if selected_symptoms:

    st.info(
        "Selected symptoms: " + "  •  ".join(selected_symptoms)
    )


st.divider()


# =========================================================
# PROBLEM INFORMATION
# =========================================================

st.subheader("🚨 Problem Information")

st.caption(
    "Describe what is happening with the machine. "
    "More useful information helps the AI produce a more relevant engineering analysis."
)


problem_description = st.text_area(
    "Problem Description",
    placeholder=(
        "Example: The pump produces unusual noise and vibration "
        "during operation. Flow rate has decreased."
    ),
    height=130
)


operating_condition = st.text_area(
    "Operating Condition",
    placeholder=(
        "Example: Machine operates continuously at approximately "
        "1450 RPM under moderate load."
    ),
    height=110
)


additional_observations = st.text_area(
    "Additional Observations",
    placeholder=(
        "Example: Vibration becomes higher after several hours "
        "of continuous operation."
    ),
    height=110
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.write("")


analyze_button = st.button(
    "🔍 Analyze Machine Problem",
    use_container_width=True
)


# =========================================================
# RUN AI ANALYSIS
# =========================================================

if analyze_button:

    if not problem_description.strip() and not selected_symptoms:

        st.warning(
            "Please provide a problem description or select at least one symptom."
        )

    else:

        selected_symptoms_text = (
            ", ".join(selected_symptoms)
            if selected_symptoms
            else "No specific symptoms selected"
        )


        # -----------------------------------------------------
        # CREATE MACHINE INFORMATION FOR THE AI
        # -----------------------------------------------------

        machine_problem = f"""

MACHINE PROFILE

Machine ID / Name:
{machine_id}

Manufacturer:
{manufacturer}

Model:
{model}

Machine Type:
{machine_type}

Machine Age:
{machine_age}

Operating Hours:
{operating_hours}

Operating Speed:
{operating_speed}

Load Condition:
{load_condition}

Last Maintenance:
{last_maintenance}


PROBLEM INFORMATION

Observed Symptoms:
{selected_symptoms_text}

Problem Description:
{problem_description}

Operating Condition:
{operating_condition}

Additional Observations:
{additional_observations}

"""


        # -----------------------------------------------------
        # RUN FOUR AGENTS
        # -----------------------------------------------------

        with st.status(
            "⚙️ MechCare AI is analyzing your machine...",
            expanded=True
        ) as analysis_status:

            try:

                st.write(
                    "🔍 Problem Analysis Agent — analyzing symptoms..."
                )

                st.write(
                    "🧠 Fault Diagnosis Agent — identifying possible causes..."
                )

                st.write(
                    "🛠️ Maintenance Planning Agent — preparing maintenance actions..."
                )

                st.write(
                    "🛡️ Safety & Final Report Agent — preparing final report..."
                )

                result = asyncio.run(
                    run_mechcare(machine_problem)
                )

                analysis_status.update(
                    label="✅ Analysis Complete",
                    state="complete",
                    expanded=False
                )

                # SAVE THE AI RESULT
                st.session_state.analysis_result = result

                # MARK ALL AGENTS AS COMPLETED
                st.session_state.agents_completed = True

                st.success(
                    "✅ Machine analysis completed successfully."
                )

            except Exception as e:

                analysis_status.update(
                    label="❌ Analysis Failed",
                    state="error",
                    expanded=True
                )

                st.error(
                    "❌ An error occurred while analyzing the machine."
                )

                st.warning(
                    "Please check your Groq API key and Streamlit deployment logs."
                )

                st.code(
                    str(e)
                )


# =========================================================
# DISPLAY AI ANALYSIS
# =========================================================

if st.session_state.analysis_result is not None:

    result = st.session_state.analysis_result

    # -------------------------------------------------
    # GET PROBLEM ANALYSIS, DIAGNOSIS AND FINAL REPORT
    # -------------------------------------------------

    problem_analysis = result["problem_analysis"]
    diagnosis_result = result["diagnosis"]
    final_report = result["final_report"]


    # =================================================
    # ENHANCED HEALTH DASHBOARD
    # =================================================

    st.subheader("📊 Machine Health Dashboard")

    report_text = final_report

    # -------------------------------------------------
    # EXTRACT PRIORITY FROM AI REPORT
    # -------------------------------------------------

    priority = "Not specified"

    if "## Priority" in report_text:

        priority_section = report_text.split(
            "## Priority",
            1
        )[1]

        if "##" in priority_section:

            priority = priority_section.split(
                "##",
                1
            )[0].strip()

        else:

            priority = priority_section.strip()


    # -------------------------------------------------
    # DETERMINE HEALTH STATUS
    # -------------------------------------------------

    priority_lower = priority.lower()

    if (
        "critical" in priority_lower
        or "urgent" in priority_lower
    ):

        health_status = "🔴 Critical"
        maintenance_status = "Immediate Inspection"

    elif "high" in priority_lower:

        health_status = "🟠 Attention Required"
        maintenance_status = "Inspection Recommended"

    elif (
        "medium" in priority_lower
        or "moderate" in priority_lower
    ):

        health_status = "🟡 Monitor"
        maintenance_status = "Further Inspection"

    else:

        health_status = "🟢 Review Required"
        maintenance_status = "Follow Recommended Checks"


    # -------------------------------------------------
    # DASHBOARD CARDS
    # -------------------------------------------------

    dash1, dash2, dash3, dash4 = st.columns(4)

    with dash1:

        st.markdown("### 🏭 Machine")
        st.write(machine_type)

    with dash2:

        st.markdown("### ❤️ Health Status")
        st.write(health_status)

    with dash3:

        st.markdown("### ⚠️ Priority")
        st.write(priority)

    with dash4:

        st.markdown("### 🔧 Maintenance")
        st.write(maintenance_status)


    st.info(
        f"**Machine:** {machine_type}  |  "
        f"**ID:** {machine_id}  |  "
        f"**Manufacturer:** {manufacturer}"
    )


    # =================================================
    # ADDITIONAL DATA RECOMMENDED
    # =================================================

    st.subheader(
        "📈 Additional Data Recommended"
    )

    st.caption(
        "Collecting the following measurements or information "
        "can help confirm the possible machine fault."
    )

    st.markdown(
        problem_analysis
    )


    # =================================================
    # SMART DIAGNOSIS
    # =================================================

    st.subheader(
        "🧠 Possible Faults & Diagnostic Checks"
    )

    st.caption(
        "The AI identifies possible causes, explains why they "
        "may be related to the symptoms, and suggests simple "
        "checks for confirmation."
    )

    st.markdown(
        diagnosis_result
    )


    # =================================================
    # MAINTENANCE CHECKLIST
    # =================================================

    st.subheader(
        "🔧 Maintenance Checklist"
    )

    st.caption(
        "Tick each check when you have completed it."
    )

    check1, check2 = st.columns(2)

    with check1:

        st.checkbox(
            "Check machine for unusual noise",
            key="Check machine for unusual noise"
        )

        st.checkbox(
            "Check for excessive vibration",
            key="Check for excessive vibration"
        )

        st.checkbox(
            "Check temperature",
            key="Check temperature"
        )

        st.checkbox(
            "Check for leakage",
            key="Check for leakage"
        )

    with check2:

        st.checkbox(
            "Check lubrication condition",
            key="Check lubrication condition"
        )

        st.checkbox(
            "Check loose components",
            key="Check loose components"
        )

        st.checkbox(
            "Check alignment",
            key="Check alignment"
        )

        st.checkbox(
            "Check operating conditions",
            key="Check operating conditions"
        )


    # =================================================
    # FINAL REPORT
    # =================================================

    st.subheader(
        "📋 Engineering Analysis Report"
    )

    st.caption(
        "Generated by the MechCare AI multi-agent engineering workflow."
    )

    st.markdown(
        final_report
    )


    # =================================================
    # VOICE READER
    # =================================================

    st.subheader(
        "🔊 Listen to AI Results"
    )

    st.caption(
        "Listen to the complete AI analysis, diagnosis, and final engineering report."
    )


    # Combine all AI-generated results
    # so the voice reads the complete output.

    complete_voice_text = f"""
MechCare AI Engineering Analysis.

Additional Data Recommended.

{problem_analysis}

Possible Faults and Diagnostic Checks.

{diagnosis_result}

Final Engineering Analysis Report.

{final_report}
"""


    speak_text(
        complete_voice_text
    )


    # =================================================
    # PDF REPORT DOWNLOAD
    # =================================================

    pdf_filename = "MechCare_AI_Report.pdf"

    create_pdf_report(
        pdf_filename,
        machine_type,
        machine_id,
        manufacturer,
        final_report
    )

    with open(pdf_filename, "rb") as pdf_file:

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_file,
            file_name="MechCare_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚙️ MechCare AI | AI-Based Mechanical Maintenance & Troubleshooting Assistant"
)

st.caption(
    "Designed for engineering decision support and educational use."
)
