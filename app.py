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
            background:#0d1021;
            border:1px solid #34345f;
            border-radius:18px;
            padding:20px;
            color:#e5e7eb;
            font-family:Arial, sans-serif;
            box-shadow:0 0 25px rgba(124,58,237,0.10);
        ">

            <h3 style="
                margin-top:0;
                color:#f8fafc;
            ">
                🔊 Listen to MechCare AI Results
            </h3>

            <p style="
                color:#9ca3af;
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
                        background:#17172f;
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
                    color:#67e8f9;
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

        const reportText = rawReportText

            .replace(/^#+\\s*/gm, "")

            .replace(/\\*\\*(.*?)\\*\\*/g, "$1")

            .replace(/\\*(.*?)\\*/g, "$1")

            .replace(/`(.*?)`/g, "$1")

            .replace(/^(---+|___+|\\*\\*\\*+)\\s*$/gm, "")

            .replace(/^\\s*[-*+]\\s+/gm, "")

            .replace(/^\\s*\\d+[.)]\\s+/gm, "")

            .replace(/^\\s*[#*_]+\\s*/gm, "")

            .replace(/[ \\t]+/g, " ")

            .replace(/\\n\\n+/g, "\\n\\n")

            .trim();


        // =================================================
        // SPEECH SYSTEM
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


            speech.onstart = function(){{

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


                if (isChangingSpeed) {{

                    updateStatus(
                        "🔄 Changing speed..."
                    );

                }} else {{

                    updateStatus(
                        "⏸️ Paused — press Play to continue"
                    );

                }}

            }};


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


            speech.onend = function() {{

                if (thisSession !== speechSession) {{
                    return;
                }}


                speech = null;


                if (isPaused) {{
                    return;
                }}


                if (isChangingSpeed) {{
                    return;
                }}


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


            if (isPaused) {{

                const savedChunk =
                    currentChunkIndex;


                const savedPosition =
                    currentChunkPosition;


                isChangingSpeed = false;

                isStopped = false;


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
                    "▶️ Continuing from saved position at " +
                    currentSpeed +
                    "×..."
                );


                setTimeout(function() {{

                    if (
                        !isStopped &&
                        !isPaused
                    ) {{

                        speakCurrentChunk(
                            savedPosition
                        );

                    }}

                }}, 200);


                return;

            }}


            if (
                speech &&
                window.speechSynthesis.speaking
            ) {{

                return;

            }}


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


            window.speechSynthesis.cancel();


            setTimeout(function() {{

                if (!isStopped) {{

                    speakCurrentChunk(
                        currentChunkPosition
                    );

                }}

            }}, 150);

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
                isPaused ||
                isStopped
            ) {{
                return;
            }}


            const savedPosition =
                currentChunkPosition;


            isPaused = true;

            isChangingSpeed = false;


            currentChunkPosition =
                savedPosition;


            updateStatus(
                "⏸️ Pausing..."
            );


            window.speechSynthesis.pause();


            setTimeout(function() {{

                if (isPaused) {{

                    updateStatus(
                        "⏸️ Paused — press Play to continue"
                    );

                }}

            }}, 250);

        }}


        // =================================================
        // STOP
        // =================================================

        function stopSpeech() {{

            if ("speechSynthesis" in window) {{

                speechSession++;

                isChangingSpeed = false;

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


            if (
                speech &&
                window.speechSynthesis.speaking &&
                !isPaused
            ){{

                const savedChunk =
                    currentChunkIndex;


                const savedPosition =
                    currentChunkPosition;


                isChangingSpeed = true;

                isPaused = true;


                updateStatus(
                    "🔄 Changing speed to " +
                    currentSpeed +
                    "×..."
                );


                window.speechSynthesis.pause();


                setTimeout(function() {{

                    if (!isChangingSpeed) {{
                        return;
                    }}


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


                            speakCurrentChunk(
                                savedPosition
                            );

                        }}

                    }}, 200);


                }}, 250);


                return;

            }}


            if (isPaused) {{

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
    initial_sidebar_state="expanded"
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

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(124, 58, 237, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 12%,
                rgba(34, 211, 238, 0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 50% 80%,
                rgba(168, 85, 247, 0.07),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #070817 0%,
                #0b0d1c 45%,
                #0d1024 100%
            );
    }

    .block-container {
        max-width: 1550px;
        padding-top: 1.3rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    ::selection {
        background: rgba(34,211,238,0.30);
        color: white;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #08091a 0%,
                #0b0d20 50%,
                #070817 100%
            );

        border-right: 1px solid rgba(124,58,237,0.28);

        box-shadow:
            10px 0 45px rgba(0,0,0,0.25);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1;
    }


    /* SIDEBAR BRAND */

    .sidebar-brand {
        padding: 19px;
        border: 1px solid rgba(124,58,237,0.42);
        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(42,27,76,0.95),
                rgba(13,17,38,0.96)
            );

        margin-bottom: 20px;

        box-shadow:
            0 0 25px rgba(124,58,237,0.12),
            0 15px 35px rgba(0,0,0,0.25);

        position: relative;
        overflow: hidden;
    }

    .sidebar-brand:after {
        content: "";
        position: absolute;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        right: -50px;
        top: -50px;
        background: rgba(34,211,238,0.10);
    }

    .sidebar-brand-title {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .sidebar-brand-subtitle {
        color: #67e8f9;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .sidebar-section {
        color: #7176a0;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        margin-top: 22px;
        margin-bottom: 8px;
    }

    .sidebar-machine {
        background:
            linear-gradient(
                135deg,
                #11132b,
                #0b0d1e
            );

        border: 1px solid rgba(34,211,238,0.18);
        border-radius: 15px;

        padding: 14px;
        margin-top: 15px;

        box-shadow:
            0 0 22px rgba(34,211,238,0.06);
    }

    .sidebar-machine-label {
        color: #7176a0;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sidebar-machine-name {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 700;
        margin-top: 4px;
    }

    .sidebar-status {
        display: inline-block;
        margin-top: 9px;
        padding: 5px 9px;
        border-radius: 999px;

        background: rgba(52,211,153,0.09);
        color: #6ee7b7;

        border: 1px solid rgba(52,211,153,0.25);

        font-size: 10px;
        font-weight: 700;
    }


    /* =====================================================
       HEADERS
       ===================================================== */

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    .section-title {
        color: #f8fafc;
        font-size: 21px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .section-description {
        color: #9298b5;
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 14px;
    }


    /* =====================================================
       TOP HEADER
       ===================================================== */

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;

        padding: 20px 23px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(27,21,55,0.96),
                rgba(11,14,31,0.96)
            );

        border: 1px solid rgba(124,58,237,0.34);
        border-radius: 20px;

        box-shadow:
            0 0 35px rgba(124,58,237,0.08),
            0 18px 45px rgba(0,0,0,0.25);

        position: relative;
        overflow: hidden;
    }

    .top-header:before {
        content: "";
        position: absolute;
        width: 320px;
        height: 2px;
        left: 0;
        bottom: 0;

        background:
            linear-gradient(
                90deg,
                transparent,
                #7c3aed,
                #22d3ee,
                transparent
            );

        opacity: 0.9;
    }

    .top-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 850;
        margin: 0;
    }

    .top-subtitle {
        color: #9298b5;
        font-size: 13px;
        margin-top: 4px;
    }

    .online-badge {
        background: rgba(34,211,238,0.08);
        color: #67e8f9;
        border: 1px solid rgba(34,211,238,0.28);
        border-radius: 999px;

        padding: 8px 13px;

        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;

        box-shadow:
            0 0 18px rgba(34,211,238,0.08);
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        position: relative;
        overflow: hidden;

        background:
            linear-gradient(
                135deg,
                #171538 0%,
                #11142c 48%,
                #10182c 100%
            );

        border: 1px solid rgba(124,58,237,0.40);
        border-radius: 22px;

        padding: 30px;

        margin-bottom: 22px;

        box-shadow:
            0 0 45px rgba(124,58,237,0.10),
            0 22px 55px rgba(0,0,0,0.28);
    }

    .hero:before {
        content: "";
        position: absolute;
        width: 350px;
        height: 350px;
        border-radius: 50%;

        right: -140px;
        top: -160px;

        background:
            radial-gradient(
                circle,
                rgba(34,211,238,0.15),
                transparent 65%
            );
    }

    .hero:after {
        content: "";
        position: absolute;

        width: 170px;
        height: 170px;

        border-radius: 50%;

        right: 80px;
        bottom: -120px;

        background:
            radial-gradient(
                circle,
                rgba(168,85,247,0.13),
                transparent 70%
            );
    }

    .hero h1 {
        color: #ffffff;
        font-size: 40px;
        margin: 0;
        letter-spacing: -1px;
    }

    .hero h3 {
        color: #67e8f9 !important;
        font-size: 16px;
        margin-top: 6px;
    }

    .hero p {
        color: #b7bdd2;
        font-size: 14px;
        line-height: 1.75;
        max-width: 850px;
        margin-bottom: 0;
    }


    /* =====================================================
       CARDS
       ===================================================== */

    .ui-card {
        background:
            linear-gradient(
                145deg,
                rgba(17,20,43,0.96),
                rgba(10,12,27,0.98)
            );

        border: 1px solid rgba(92,96,143,0.28);
        border-radius: 17px;

        padding: 18px;
        margin-bottom: 15px;

        box-shadow:
            0 12px 30px rgba(0,0,0,0.18),
            inset 0 1px 0 rgba(255,255,255,0.025);

        transition:
            border-color 0.2s ease,
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .ui-card:hover {
        border-color: rgba(34,211,238,0.35);

        box-shadow:
            0 0 25px rgba(34,211,238,0.07),
            0 15px 35px rgba(0,0,0,0.22);

        transform: translateY(-1px);
    }

    .card-label {
        color: #6f759c;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-bottom: 6px;
    }

    .card-value {
        color: #f8fafc;
        font-size: 19px;
        font-weight: 750;
    }

    .card-small {
        color: #9298b5;
        font-size: 12px;
        margin-top: 5px;
    }


    /* =====================================================
       STATUS CARDS
       ===================================================== */

    .status-card {
        background:
            linear-gradient(
                145deg,
                rgba(17,20,43,0.98),
                rgba(10,12,27,0.98)
            );

        border: 1px solid rgba(92,96,143,0.30);
        border-radius: 17px;

        padding: 17px;

        min-height: 112px;

        box-shadow:
            0 12px 30px rgba(0,0,0,0.18);

        position: relative;
        overflow: hidden;
    }

    .status-card:after {
        content: "";
        position: absolute;

        width: 90px;
        height: 90px;

        right: -45px;
        bottom: -45px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(124,58,237,0.13),
                transparent 70%
            );
    }

    .status-title {
        color: #6f759c;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .status-main {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 750;
        margin-top: 9px;
        line-height: 1.3;
    }

    .status-sub {
        color: #858ba8;
        font-size: 11px;
        margin-top: 5px;
    }


    /* =====================================================
       WORKFLOW
       ===================================================== */

    .workflow-card {
        background:
            linear-gradient(
                145deg,
                #11142b,
                #0b0d1e
            );

        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 17px;

        padding: 18px;

        height: 100%;
        min-height: 155px;

        box-shadow:
            0 10px 28px rgba(0,0,0,0.18);

        position: relative;
        overflow: hidden;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }

    .workflow-card:before {
        content: "";
        position: absolute;

        left: 0;
        top: 0;

        width: 3px;
        height: 100%;

        background:
            linear-gradient(
                180deg,
                #22d3ee,
                #7c3aed
            );
    }

    .workflow-card:hover {
        transform: translateY(-3px);

        border-color: rgba(34,211,238,0.45);

        box-shadow:
            0 0 30px rgba(124,58,237,0.10),
            0 15px 32px rgba(0,0,0,0.25);
    }

    .workflow-number {
        color: #67e8f9;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 1.3px;
    }

    .workflow-title {
        color: #f8fafc;
        font-size: 14px;
        font-weight: 750;
        margin-top: 8px;
    }

    .workflow-description {
        color: #858ba8;
        font-size: 12px;
        line-height: 1.6;
        margin-top: 7px;
    }


    /* =====================================================
       SYMPTOM BOX
       ===================================================== */

    .symptom-box {
        background:
            linear-gradient(
                135deg,
                rgba(34,211,238,0.08),
                rgba(124,58,237,0.08)
            );

        border: 1px solid rgba(34,211,238,0.25);

        border-radius: 13px;

        padding: 13px 15px;

        color: #a5f3fc;

        margin-top: 10px;

        line-height: 1.6;

        font-size: 13px;

        box-shadow:
            0 0 20px rgba(34,211,238,0.05);
    }


    /* =====================================================
       QUESTIONS
       ===================================================== */

    .question-card {
        background:
            linear-gradient(
                145deg,
                rgba(20,18,45,0.96),
                rgba(10,12,27,0.98)
            );

        border: 1px solid rgba(124,58,237,0.24);

        border-radius: 15px;

        padding: 14px 15px;

        margin-bottom: 11px;

        box-shadow:
            0 8px 22px rgba(0,0,0,0.16);

        transition:
            border-color 0.2s ease,
            transform 0.2s ease;
    }

    .question-card:hover {
        border-color: rgba(34,211,238,0.38);
        transform: translateX(2px);
    }

    .question-number {
        color: #67e8f9;
        font-size: 9px;
        font-weight: 900;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .question-text {
        color: #dfe3f2;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 5px;
    }


    /* =====================================================
       REPORT
       ===================================================== */

    .report-box {
        background:
            linear-gradient(
                145deg,
                #0e1022,
                #090b18
            );

        border: 1px solid rgba(124,58,237,0.24);

        border-radius: 17px;

        padding: 24px;

        color: #dbe4f5;

        line-height: 1.75;

        box-shadow:
            0 15px 35px rgba(0,0,0,0.20),
            0 0 25px rgba(124,58,237,0.04);
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 10px !important;

        border: 1px solid rgba(124,58,237,0.40) !important;

        background:
            linear-gradient(
                135deg,
                #33206b,
                #182b58
            ) !important;

        color: #f8fafc !important;

        font-weight: 750 !important;

        min-height: 44px;

        transition:
            transform 0.15s ease,
            border-color 0.15s ease,
            box-shadow 0.15s ease,
            background 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #22d3ee !important;

        background:
            linear-gradient(
                135deg,
                #45268c,
                #173d68
            ) !important;

        box-shadow:
            0 0 22px rgba(34,211,238,0.14),
            0 0 35px rgba(124,58,237,0.10);

        transform: translateY(-1px);
    }


    /* =====================================================
       INPUTS
       ===================================================== */

    div[data-baseweb="select"] > div {
        background-color: #0d1021 !important;

        border-color: #303454 !important;

        border-radius: 10px !important;

        transition:
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #7c3aed !important;

        box-shadow:
            0 0 14px rgba(124,58,237,0.10);
    }

    textarea {
        background-color: #0d1021 !important;

        border: 1px solid #303454 !important;

        color: #f8fafc !important;

        border-radius: 10px !important;
    }

    textarea:focus {
        border-color: #22d3ee !important;

        box-shadow:
            0 0 0 1px rgba(34,211,238,0.25),
            0 0 18px rgba(34,211,238,0.07) !important;
    }

    label {
        color: #cdd3e4 !important;
        font-weight: 600 !important;
    }


    /* =====================================================
       MULTISELECT
       ===================================================== */

    [data-baseweb="tag"] {
        background:
            linear-gradient(
                135deg,
                #35206f,
                #173b61
            ) !important;

        color: #e0f2fe !important;

        border: 1px solid rgba(34,211,238,0.20);
    }


    /* =====================================================
       CHECKBOX
       ===================================================== */

    [data-testid="stCheckbox"] label {
        color: #cbd5e1 !important;
        font-size: 13px !important;
    }


    /* =====================================================
       EXPANDERS
       ===================================================== */

    [data-testid="stExpander"] {
        background: #0d1021;

        border: 1px solid #303454;

        border-radius: 12px;
    }


    /* =====================================================
       STATUS
       ===================================================== */

    [data-testid="stStatusWidget"] {
        border-radius: 14px;
        background: #0d1021;
        border-color: #34345f;
    }


    /* =====================================================
       PROGRESS BAR
       ===================================================== */

    [data-testid="stProgressBar"] > div > div {
        background:
            linear-gradient(
                90deg,
                #7c3aed,
                #22d3ee
            ) !important;

        box-shadow:
            0 0 14px rgba(34,211,238,0.18);
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border-color: rgba(91,96,142,0.28) !important;

        margin-top: 25px !important;
        margin-bottom: 25px !important;
    }


    /* =====================================================
       DOWNLOAD BUTTON
       ===================================================== */

    [data-testid="stDownloadButton"] button {
        border-radius: 11px !important;

        background:
            linear-gradient(
                135deg,
                #372078,
                #174667
            ) !important;

        border: 1px solid rgba(34,211,238,0.30) !important;

        color: white !important;

        font-weight: 750 !important;

        box-shadow:
            0 0 22px rgba(34,211,238,0.07);
    }


    /* =====================================================
       RESPONSIVE
       ===================================================== */

    @media (max-width: 1100px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .top-title {
            font-size: 23px;
        }

        .hero h1 {
            font-size: 32px;
        }

    }

    @media (max-width: 700px) {

        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            padding-top: 0.8rem;
        }

        .hero {
            padding: 21px;
        }

        .hero h1 {
            font-size: 28px;
        }

        .hero h3 {
            font-size: 14px;
        }

        .top-header {
            padding: 16px;
        }

        .top-title {
            font-size: 20px;
        }

        .online-badge {
            display: none;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                ⚙️ MechCare AI
            </div>

            <div class="sidebar-brand-subtitle">
                Engineering Intelligence
            </div>
        </div>
        """
    )

    st.html(
        '<div class="sidebar-section">Navigation</div>'
    )

    navigation = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Machine Diagnostics",
            "Maintenance",
            "Reports"
        ],
        label_visibility="collapsed"
    )

    st.html(
        '<div class="sidebar-section">Machine Category</div>'
    )

    machine_category_filter = st.selectbox(
        "Machine Category",
        [
            "All Machines",
            "Centrifugal Pump",
            "Electric Motor",
            "Gearbox",
            "Compressor",
            "Fan",
            "Bearing System",
            "Turbine",
            "Other"
        ],
        label_visibility="collapsed"
    )

    st.html(
        '<div class="sidebar-section">Quick System Links</div>'
    )

    st.button(
        "📋 Active Machine Profiles",
        use_container_width=True
    )

    st.button(
        "🛠️ Maintenance Logs",
        use_container_width=True
    )

    st.button(
        "📄 Generated Reports",
        use_container_width=True
    )

    st.html(
        '<div class="sidebar-section">Current Machine</div>'
    )

    st.html(
        """
        <div class="sidebar-machine">

            <div class="sidebar-machine-label">
                System
            </div>

            <div class="sidebar-machine-name">
                Active Diagnostic Session
            </div>

            <span class="sidebar-status">
                ● SYSTEM READY
            </span>

        </div>
        """
    )

    st.markdown("")

    st.caption("MechCare AI v1.0")
    st.caption("Engineering decision support system")


# =========================================================
# TOP HEADER
# =========================================================

st.html(
    """
    <div class="top-header">

        <div>
            <div class="top-title">
                Engineering Command Center
            </div>

            <div class="top-subtitle">
                AI-powered machine diagnostics, maintenance planning
                and engineering reporting.
            </div>
        </div>

        <div class="online-badge">
            ● AI SYSTEM READY
        </div>

    </div>
    """
)


# =========================================================
# HERO
# =========================================================

st.html(
    """
    <div class="hero">

        <h1>⚙️ MechCare AI</h1>

        <h3>
            AI-Powered Machine Maintenance & Troubleshooting Assistant
        </h3>

        <p>
            Describe your machine, operating conditions, and observed
            symptoms. MechCare AI uses a multi-agent engineering workflow
            to analyze the problem, identify possible causes, suggest
            maintenance actions, and generate a structured safety-focused
            report.
        </p>

    </div>
    """
)


# =========================================================
# MAIN ASYMMETRIC LAYOUT
# =========================================================

main_column, right_column = st.columns(
    [3.45, 1.15],
    gap="large"
)


# =========================================================
# RIGHT INTELLIGENCE PANEL
# =========================================================

with right_column:

    st.html(
        '<div class="section-title">⚡ Quick Intelligence</div>'
    )

    st.html(
        '<div class="section-description">System information and quick diagnostic context.</div>'
    )

    st.html(
        """
        <div class="ui-card">

            <div class="card-label">
                SYSTEM STATUS
            </div>

            <div class="card-value">
                🟢 Online
            </div>

            <div class="card-small">
                AI diagnostic engine ready
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="ui-card">

            <div class="card-label">
                WORKFLOW
            </div>

            <div class="card-value">
                4 AI Agents
            </div>

            <div class="card-small">
                Analysis → Diagnosis → Maintenance → Safety
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="ui-card">

            <div class="card-label">
                INPUT QUALITY
            </div>

            <div class="card-value">
                Detailed Data
            </div>

            <div class="card-small">
                More machine information can improve diagnostic context.
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="ui-card">

            <div class="card-label">
                QUICK CHECKS
            </div>

            <div class="card-small" style="line-height:1.9;">

                🔊 Listen for unusual noise<br>
                📳 Observe vibration<br>
                🌡️ Check temperature<br>
                💧 Inspect for leakage<br>
                🛢️ Check lubrication<br>
                🔩 Inspect loose components

            </div>

        </div>
        """
    )


    # =====================================================
    # ENGINEERING QUESTIONS
    # =====================================================

    st.html(
        '<div class="section-title" style="margin-top:22px;">💡 Engineering Questions</div>'
    )

    st.html(
        '<div class="section-description">Useful questions to consider during machine inspection.</div>'
    )

    engineering_questions = [
        (
            "01",
            "What changed before the problem started?"
        ),
        (
            "02",
            "Does the symptom increase with machine speed?"
        ),
        (
            "03",
            "Does the problem appear under heavy load?"
        ),
        (
            "04",
            "Is the machine temperature higher than normal?"
        ),
        (
            "05",
            "Has the machine recently been repaired or adjusted?"
        ),
        (
            "06",
            "Is the vibration coming from a specific component?"
        ),
        (
            "07",
            "When was the machine last lubricated?"
        ),
        (
            "08",
            "Are there any unusual sounds, smells or leaks?"
        ),
        (
            "09",
            "Has machine performance gradually decreased?"
        ),
        (
            "10",
            "Could operating conditions have changed?"
        )
    ]

    for number, question in engineering_questions:

        st.html(
            f"""
            <div class="question-card">

                <div class="question-number">
                    ENGINEERING CHECK {number}
                </div>

                <div class="question-text">
                    {question}
                </div>

            </div>
            """
        )


# =========================================================
# CENTER WORKSPACE
# =========================================================

with main_column:

    # =====================================================
    # WORKFLOW
    # =====================================================

    st.html(
        '<div class="section-title">🤖 Multi-Agent Engineering Workflow</div>'
    )

    st.html(
        '<div class="section-description">Your machine problem is processed through four specialized engineering agents.</div>'
    )


    workflow = [
        (
            "01",
            "🔍 Problem Analysis",
            "Analyzes machine information, symptoms, observations and missing information."
        ),
        (
            "02",
            "🧠 Fault Diagnosis",
            "Examines symptoms and identifies possible mechanical and operational causes."
        ),
        (
            "03",
            "🛠️ Maintenance Planning",
            "Converts possible causes into practical inspection and maintenance actions."
        ),
        (
            "04",
            "🛡️ Safety & Report",
            "Reviews previous results and creates the final safety-focused engineering report."
        )
    ]


    workflow_columns = st.columns(4, gap="small")


    for column, agent in zip(workflow_columns, workflow):

        number, title, description = agent

        with column:

            st.html(
                f"""
                <div class="workflow-card">

                    <div class="workflow-number">
                        AGENT {number}
                    </div>

                    <div class="workflow-title">
                        {title}
                    </div>

                    <div class="workflow-description">
                        {description}
                    </div>

                </div>
                """
            )


    st.divider()


    # =====================================================
    # MACHINE PROFILE
    # =====================================================

    st.html(
        '<div class="section-title">🏭 Machine Profile</div>'
    )

    st.html(
        '<div class="section-description">Provide the machine context used by the AI diagnostic workflow.</div>'
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


    # =====================================================
    # MACHINE INFORMATION
    # =====================================================

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


    # =====================================================
    # SYMPTOMS
    # =====================================================

    st.html(
        '<div class="section-title">🔍 Observed Symptoms</div>'
    )

    st.html(
        '<div class="section-description">Select all symptoms currently observed in the machine.</div>'
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

        st.html(
            '<div class="symptom-box"><b>Selected Symptoms:</b> '
            + "  •  ".join(selected_symptoms)
            + "</div>"
        )


    st.divider()


    # =====================================================
    # PROBLEM INFORMATION
    # =====================================================

    st.html(
        '<div class="section-title">🚨 Problem Information</div>'
    )

    st.html(
        '<div class="section-description">Describe what is happening. More useful information gives the AI better engineering context.</div>'
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


    # =====================================================
    # ANALYZE BUTTON
    # =====================================================

    st.write("")


    analyze_button = st.button(
        "🔍 Analyze Machine Problem",
        use_container_width=True
    )


    # =====================================================
    # RUN AI ANALYSIS
    # =====================================================

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


            # -------------------------------------------------
            # CREATE MACHINE INFORMATION FOR THE AI
            # -------------------------------------------------

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


            # -------------------------------------------------
            # RUN FOUR AGENTS
            # -------------------------------------------------

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

                    st.session_state.analysis_result = result

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


    # =====================================================
    # DISPLAY AI ANALYSIS
    # =====================================================

    if st.session_state.analysis_result is not None:

        result = st.session_state.analysis_result


        # -------------------------------------------------
        # GET RESULTS
        # -------------------------------------------------

        problem_analysis = result["problem_analysis"]
        diagnosis_result = result["diagnosis"]
        final_report = result["final_report"]


        # =================================================
        # HEALTH DASHBOARD
        # =================================================

        st.divider()

        st.html(
            '<div class="section-title">📊 Machine Health Dashboard</div>'
        )

        st.html(
            '<div class="section-description">AI-generated health and maintenance overview based on the current engineering analysis.</div>'
        )


        report_text = final_report


        # -------------------------------------------------
        # EXTRACT PRIORITY
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

        dash1, dash2, dash3, dash4 = st.columns(4, gap="small")


        with dash1:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-title">
                        MACHINE
                    </div>

                    <div class="status-main">
                        🏭 {machine_type}
                    </div>

                    <div class="status-sub">
                        {machine_id}
                    </div>

                </div>
                """
            )


        with dash2:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-title">
                        HEALTH STATUS
                    </div>

                    <div class="status-main">
                        {health_status}
                    </div>

                    <div class="status-sub">
                        AI assessment
                    </div>

                </div>
                """
            )


        with dash3:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-title">
                        PRIORITY
                    </div>

                    <div class="status-main">
                        ⚠️ {priority}
                    </div>

                    <div class="status-sub">
                        Extracted from final report
                    </div>

                </div>
                """
            )


        with dash4:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-title">
                        MAINTENANCE
                    </div>

                    <div class="status-main">
                        🔧 {maintenance_status}
                    </div>

                    <div class="status-sub">
                        Recommended action
                    </div>

                </div>
                """
            )


        st.markdown("")


        # =================================================
        # ACTIVE MACHINE CARD
        # =================================================

        st.html(
            f"""
            <div class="ui-card">

                <div class="card-label">
                    ACTIVE MACHINE PROFILE
                </div>

                <div class="card-value">
                    {machine_type} · {machine_id}
                </div>

                <div class="card-small">
                    Manufacturer: {manufacturer}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Model: {model}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Speed: {operating_speed}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    Load: {load_condition}
                </div>

            </div>
            """
        )


        # =================================================
        # ADDITIONAL DATA RECOMMENDED
        # =================================================

        st.html(
            '<div class="section-title">📈 Additional Data Recommended</div>'
        )

        st.html(
            '<div class="section-description">Collecting these measurements or observations can help confirm the possible machine fault.</div>'
        )

        st.markdown(
            problem_analysis
        )


        # =================================================
        # SMART DIAGNOSIS
        # =================================================

        st.html(
            '<div class="section-title" style="margin-top:25px;">🧠 Possible Faults & Diagnostic Checks</div>'
        )

        st.html(
            '<div class="section-description">Possible causes, their relationship with the symptoms, and suggested confirmation checks.</div>'
        )

        st.markdown(
            diagnosis_result
        )


        # =================================================
        # MAINTENANCE CHECKLIST
        # =================================================

        st.html(
            '<div class="section-title" style="margin-top:25px;">🔧 Maintenance Checklist</div>'
        )

        st.html(
            '<div class="section-description">Tick each inspection when it has been completed.</div>'
        )


        completed_count = sum(
            1
            for item in checklist_items
            if st.session_state[item]
        )


        progress_value = (
            completed_count / len(checklist_items)
        )


        st.progress(
            progress_value,
            text=f"{completed_count} of {len(checklist_items)} checks completed"
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

        st.html(
            '<div class="section-title" style="margin-top:25px;">📋 Engineering Analysis Report</div>'
        )

        st.html(
            '<div class="section-description">Generated by the MechCare AI multi-agent engineering workflow.</div>'
        )

        st.markdown(
            final_report
        )


        # =================================================
        # VOICE READER
        # =================================================

        st.html(
            '<div class="section-title" style="margin-top:25px;">🔊 Listen to AI Results</div>'
        )

        st.html(
            '<div class="section-description">Listen to the complete AI analysis, diagnosis, and final engineering report.</div>'
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

        st.html(
            '<div class="section-title" style="margin-top:25px;">📄 Engineering Report Export</div>'
        )

        st.html(
            '<div class="section-description">Generate and download the final engineering report as a PDF.</div>'
        )


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


footer_col1, footer_col2 = st.columns(2)


with footer_col1:

    st.caption(
        "⚙️ MechCare AI | AI-Based Mechanical Maintenance & Troubleshooting Assistant"
    )


with footer_col2:

    st.caption(
        "Designed for engineering decision support and educational use."
    )
