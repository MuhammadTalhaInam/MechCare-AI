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

                isStopped = false;


                // Invalidate every event belonging
                // to the previous utterance.

                speechSession++;


                // Completely cancel the old mobile
                // speech instance.

                window.speechSynthesis.cancel();

                speech = null;


                // Restore saved position.

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


                // Small delay is important on mobile
                // browsers after cancel().

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


            // -------------------------------------------------
            // IMPORTANT MOBILE FIX
            // -------------------------------------------------
            //
            // Do NOT depend on the mobile browser firing
            // onpause before we mark the player as paused.
            //
            // Save the latest position immediately.
            // onboundary continuously updates
            // currentChunkPosition while speaking.
            //

            const savedPosition =
                currentChunkPosition;


            isPaused = true;

            isChangingSpeed = false;


            currentChunkPosition =
                savedPosition;


            updateStatus(
                "⏸️ Pausing..."
            );


            // Ask the browser to pause.

            window.speechSynthesis.pause();


            // -------------------------------------------------
            // MOBILE FALLBACK
            // -------------------------------------------------
            //
            // Some mobile browsers do not reliably handle
            // speechSynthesis.pause().
            //
            // We keep the speech object paused for a short
            // moment, then Play will completely cancel it
            // and create a fresh utterance from the saved
            // position.
            //

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


            // -------------------------------------------------
            // CURRENTLY SPEAKING
            // -------------------------------------------------

            if (
                speech &&
                window.speechSynthesis.speaking &&
                !isPaused
            ) {{

                // Save the latest known position BEFORE
                // changing the speech object.

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


                // Pause the current speech first.

                window.speechSynthesis.pause();


                // -------------------------------------------------
                // RESTART FROM SAVED POSITION
                // -------------------------------------------------
                //
                // We do not use resume().
                //
                // Instead, cancel the old utterance and create
                // a new one with the selected speed.
                //

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


            // -------------------------------------------------
            // CURRENTLY PAUSED
            // -------------------------------------------------

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
                circle at 15% 10%,
                rgba(14, 116, 144, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(124, 58, 237, 0.08),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #050b14 0%,
                #081421 45%,
                #0a1724 100%
            );
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #07111d 0%,
                #081725 55%,
                #06101b 100%
            );

        border-right: 1px solid #17344b;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1;
    }

    .sidebar-brand {
        padding: 18px;
        border: 1px solid #1c4059;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #0c2032,
            #0b1827
        );
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }

    .sidebar-brand-title {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .sidebar-brand-subtitle {
        color: #38bdf8;
        font-size: 11px;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    .sidebar-section {
        color: #64748b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 22px;
        margin-bottom: 8px;
    }

    .sidebar-machine {
        background: #0c1b2a;
        border: 1px solid #1a3a50;
        border-radius: 14px;
        padding: 14px;
        margin-top: 15px;
    }

    .sidebar-machine-label {
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sidebar-machine-name {
        color: #f8fafc;
        font-size: 16px;
        font-weight: 700;
        margin-top: 4px;
    }

    .sidebar-status {
        display: inline-block;
        margin-top: 9px;
        padding: 5px 9px;
        border-radius: 999px;
        background: rgba(52,211,153,0.12);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        font-size: 11px;
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
        color: #8fa3b8;
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
        padding: 20px 22px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(13,34,56,0.95),
                rgba(9,24,39,0.95)
            );

        border: 1px solid #1a4059;
        border-radius: 18px;

        box-shadow:
            0 16px 40px rgba(0,0,0,0.22);
    }

    .top-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 850;
        margin: 0;
    }

    .top-subtitle {
        color: #8fa3b8;
        font-size: 13px;
        margin-top: 4px;
    }

    .online-badge {
        background: rgba(52,211,153,0.10);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.28);
        border-radius: 999px;
        padding: 8px 13px;
        font-size: 12px;
        font-weight: 700;
        white-space: nowrap;
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
                #0c243b 0%,
                #0b1b2c 60%,
                #111d31 100%
            );

        border: 1px solid #1d4d6b;
        border-radius: 20px;

        padding: 28px;

        margin-bottom: 20px;

        box-shadow:
            0 20px 50px rgba(0,0,0,0.25);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        border-radius: 50%;
        right: -70px;
        top: -70px;
        background: rgba(56,189,248,0.08);
    }

    .hero h1 {
        color: #f8fafc;
        font-size: 39px;
        margin: 0;
    }

    .hero h3 {
        color: #38bdf8 !important;
        font-size: 16px;
        margin-top: 6px;
    }

    .hero p {
        color: #b8c7d8;
        font-size: 14px;
        line-height: 1.75;
        max-width: 850px;
        margin-bottom: 0;
    }


    /* =====================================================
       CARDS
       ===================================================== */

    .ui-card {
        background: #0b1928;
        border: 1px solid #1b3b52;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 15px;

        box-shadow:
            0 12px 30px rgba(0,0,0,0.16);
    }

    .card-label {
        color: #64748b;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.3px;
        margin-bottom: 6px;
    }

    .card-value {
        color: #f8fafc;
        font-size: 19px;
        font-weight: 750;
    }

    .card-small {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 5px;
    }


    /* =====================================================
       STATUS CARDS
       ===================================================== */

    .status-card {
        background: #0b1928;
        border: 1px solid #1b3b52;
        border-radius: 16px;
        padding: 17px;
        min-height: 112px;

        box-shadow:
            0 10px 26px rgba(0,0,0,0.15);
    }

    .status-title {
        color: #64748b;
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
        color: #8fa3b8;
        font-size: 11px;
        margin-top: 5px;
    }


    /* =====================================================
       WORKFLOW
       ===================================================== */

    .workflow-card {
        background: #091725;
        border: 1px solid #1a3a50;
        border-radius: 16px;
        padding: 18px;
        height: 100%;
        min-height: 155px;

        box-shadow:
            0 10px 26px rgba(0,0,0,0.15);
    }

    .workflow-number {
        color: #38bdf8;
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
        color: #8fa3b8;
        font-size: 12px;
        line-height: 1.6;
        margin-top: 7px;
    }


    /* =====================================================
       SYMPTOM BOX
       ===================================================== */

    .symptom-box {
        background: rgba(14,116,144,0.12);
        border: 1px solid rgba(56,189,248,0.25);
        border-radius: 13px;
        padding: 13px 15px;
        color: #7dd3fc;
        margin-top: 10px;
        line-height: 1.6;
        font-size: 13px;
    }


    /* =====================================================
       REPORT
       ===================================================== */

    .report-box {
        background: #081522;
        border: 1px solid #1c4058;
        border-radius: 17px;
        padding: 24px;
        color: #dbeafe;
        line-height: 1.75;

        box-shadow:
            0 15px 35px rgba(0,0,0,0.18);
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 10px !important;
        border: 1px solid #245b7c !important;

        background:
            linear-gradient(
                135deg,
                #0e4566,
                #0b314b
            ) !important;

        color: #f8fafc !important;
        font-weight: 750 !important;

        min-height: 44px;

        transition:
            transform 0.15s ease,
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #38bdf8 !important;
        box-shadow:
            0 0 20px rgba(56,189,248,0.15);
        transform: translateY(-1px);
    }


    /* =====================================================
       INPUTS
       ===================================================== */

    div[data-baseweb="select"] > div {
        background-color: #0b1928 !important;
        border-color: #23455d !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #38bdf8 !important;
    }

    textarea {
        background-color: #0b1928 !important;
        border: 1px solid #23455d !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow:
            0 0 0 1px rgba(56,189,248,0.25) !important;
    }

    label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }


    /* =====================================================
       MULTISELECT
       ===================================================== */

    [data-baseweb="tag"] {
        background-color: #12405e !important;
        color: #dbeafe !important;
    }


    /* =====================================================
       CHECKBOX
       ===================================================== */

    [data-testid="stCheckbox"] label {
        color: #cbd5e1 !important;
        font-size: 13px !important;
    }


    /* =====================================================
       EXPANDERS / STATUS
       ===================================================== */

    [data-testid="stExpander"] {
        background: #0b1928;
        border: 1px solid #1b3b52;
        border-radius: 12px;
    }

    [data-testid="stStatusWidget"] {
        border-radius: 14px;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border-color: #17354a !important;
        margin-top: 25px !important;
        margin-bottom: 25px !important;
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

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                ⚙️ MechCare AI
            </div>

            <div class="sidebar-brand-subtitle">
                Engineering Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">Navigation</div>',
        unsafe_allow_html=True
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

    st.markdown(
        '<div class="sidebar-section">Machine Category</div>',
        unsafe_allow_html=True
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

    st.markdown(
        '<div class="sidebar-section">Quick System Links</div>',
        unsafe_allow_html=True
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

    st.markdown(
        '<div class="sidebar-section">Current Machine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    st.caption(
        "MechCare AI v1.0"
    )

    st.caption(
        "Engineering decision support system"
    )


# =========================================================
# TOP HEADER
# =========================================================

st.markdown(
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
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
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
    """,
    unsafe_allow_html=True
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

    st.markdown(
        '<div class="section-title">⚡ Quick Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">System information and quick diagnostic context.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )


# =========================================================
# CENTER WORKSPACE
# =========================================================

with main_column:

    # =====================================================
    # WORKFLOW
    # =====================================================

    st.markdown(
        '<div class="section-title">🤖 Multi-Agent Engineering Workflow</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">Your machine problem is processed through four specialized engineering agents.</div>',
        unsafe_allow_html=True
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

            st.markdown(
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
                """,
                unsafe_allow_html=True
            )


    st.divider()


    # =====================================================
    # MACHINE PROFILE
    # =====================================================

    st.markdown(
        '<div class="section-title">🏭 Machine Profile</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">Provide the machine context used by the AI diagnostic workflow.</div>',
        unsafe_allow_html=True
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

    st.markdown(
        '<div class="section-title">🔍 Observed Symptoms</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">Select all symptoms currently observed in the machine.</div>',
        unsafe_allow_html=True
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

        st.markdown(
            '<div class="symptom-box"><b>Selected Symptoms:</b> '
            + "  •  ".join(selected_symptoms)
            + "</div>",
            unsafe_allow_html=True
        )


    st.divider()


    # =====================================================
    # PROBLEM INFORMATION
    # =====================================================

    st.markdown(
        '<div class="section-title">🚨 Problem Information</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">Describe what is happening. More useful information gives the AI better engineering context.</div>',
        unsafe_allow_html=True
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


    # =====================================================
    # DISPLAY AI ANALYSIS
    # =====================================================

    if st.session_state.analysis_result is not None:

        result = st.session_state.analysis_result


        # -------------------------------------------------
        # GET PROBLEM ANALYSIS, DIAGNOSIS AND FINAL REPORT
        # -------------------------------------------------

        problem_analysis = result["problem_analysis"]
        diagnosis_result = result["diagnosis"]
        final_report = result["final_report"]


        # =================================================
        # HEALTH DASHBOARD
        # =================================================

        st.divider()

        st.markdown(
            '<div class="section-title">📊 Machine Health Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">AI-generated health and maintenance overview based on the current engineering analysis.</div>',
            unsafe_allow_html=True
        )


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

        dash1, dash2, dash3, dash4 = st.columns(4, gap="small")


        with dash1:

            st.markdown(
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
                """,
                unsafe_allow_html=True
            )


        with dash2:

            st.markdown(
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
                """,
                unsafe_allow_html=True
            )


        with dash3:

            st.markdown(
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
                """,
                unsafe_allow_html=True
            )


        with dash4:

            st.markdown(
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
                """,
                unsafe_allow_html=True
            )


        st.markdown("")


        # =================================================
        # ACTIVE MACHINE CARD
        # =================================================

        st.markdown(
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
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # ADDITIONAL DATA RECOMMENDED
        # =================================================

        st.markdown(
            '<div class="section-title">📈 Additional Data Recommended</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Collecting these measurements or observations can help confirm the possible machine fault.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="report-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            problem_analysis
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # SMART DIAGNOSIS
        # =================================================

        st.markdown(
            '<div class="section-title" style="margin-top:25px;">🧠 Possible Faults & Diagnostic Checks</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Possible causes, their relationship with the symptoms, and suggested confirmation checks.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="report-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            diagnosis_result
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # MAINTENANCE CHECKLIST
        # =================================================

        st.markdown(
            '<div class="section-title" style="margin-top:25px;">🔧 Maintenance Checklist</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Tick each inspection when it has been completed.</div>',
            unsafe_allow_html=True
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

        st.markdown(
            '<div class="section-title" style="margin-top:25px;">📋 Engineering Analysis Report</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Generated by the MechCare AI multi-agent engineering workflow.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="report-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            final_report
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # VOICE READER
        # =================================================

        st.markdown(
            '<div class="section-title" style="margin-top:25px;">🔊 Listen to AI Results</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Listen to the complete AI analysis, diagnosis, and final engineering report.</div>',
            unsafe_allow_html=True
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

        st.markdown(
            '<div class="section-title" style="margin-top:25px;">📄 Engineering Report Export</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">Generate and download the final engineering report as a PDF.</div>',
            unsafe_allow_html=True
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
