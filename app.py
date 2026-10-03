import streamlit as st
import asyncio
import json
import re
import streamlit.components.v1 as components

from crew import run_mechcare
from pdf_report import create_pdf_report


# =========================================================
# VOICE READER
# =========================================================

def speak_text(text):

    report_json = json.dumps(str(text))

    voice_html = r"""
        <div style="
            background:#162235;
            border:1px solid #2A3A52;
            border-radius:14px;
            padding:20px;
            color:#F1F5F9;
            font-family:Arial, sans-serif;
            box-shadow:
                0 12px 30px rgba(0,0,0,0.20),
                0 0 24px rgba(25,195,216,0.06);
        ">

            <h3 style="
                margin-top:0;
                color:#F1F5F9;
                font-size:18px;
                font-weight:800;
            ">
                🔊 Listen to MechCare AI Results
            </h3>

            <p style="
                color:#CBD5E1;
                margin-bottom:17px;
                font-size:13px;
                line-height:1.6;
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

                <button onclick="playSpeech()" style="
                    padding:9px 18px;
                    border:1px solid #1687D9;
                    border-radius:8px;
                    cursor:pointer;
                    font-size:14px;
                    font-weight:700;
                    color:#ffffff;
                    background:#1687D9;
                ">
                    ▶️ Play
                </button>

                <button onclick="pauseSpeech()" style="
                    padding:9px 18px;
                    border:1px solid #64748B;
                    border-radius:8px;
                    cursor:pointer;
                    font-size:14px;
                    font-weight:700;
                    color:#F1F5F9;
                    background:#24344D;
                ">
                    ⏸️ Pause
                </button>

                <button onclick="stopSpeech()" style="
                    padding:9px 18px;
                    border:1px solid #EF5350;
                    border-radius:8px;
                    cursor:pointer;
                    font-size:14px;
                    font-weight:700;
                    color:#ffffff;
                    background:#EF5350;
                ">
                    ⏹️ Stop
                </button>

                <label style="
                    color:#CBD5E1;
                    font-size:14px;
                    font-weight:600;
                ">
                    Speed:
                </label>

                <select id="speed" onchange="changeSpeed()" style="
                    padding:8px 12px;
                    border-radius:7px;
                    border:1px solid #2A3A52;
                    background:#0B1220;
                    color:#F1F5F9;
                    font-size:14px;
                    outline:none;
                ">
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

            <div id="voiceStatus" style="
                margin-top:16px;
                color:#20C997;
                font-size:13px;
                font-weight:700;
            ">
                ● Ready to play
            </div>

        </div>

        <script>

        const rawReportText = __REPORT_JSON__;

        const reportText = rawReportText
            .replace(/^#+\s*/gm, "")
            .replace(/\*\*(.*?)\*\*/g, "$1")
            .replace(/\*(.*?)\*/g, "$1")
            .replace(/`(.*?)`/g, "$1")
            .replace(/^(---+|___+|\*\*\*+)\s*$/gm, "")
            .replace(/^\s*[-*+]\s+/gm, "")
            .replace(/^\s*\d+[.)]\s+/gm, "")
            .replace(/^\s*[#*_]+\s*/gm, "")
            .replace(/[ \t]+/g, " ")
            .replace(/\n\n+/g, "\n\n")
            .trim();

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

        function createSpeechChunks(text) {

            const normalizedText =
                text.replace(/\s+/g, " ").trim();

            if (!normalizedText) {
                return [];
            }

            const sentences =
                normalizedText.match(
                    /[^.!?]+[.!?]+|[^.!?]+$/g
                ) || [normalizedText];

            const chunks = [];
            let currentChunk = "";

            sentences.forEach(function(sentence) {

                const cleanSentence =
                    sentence.trim();

                if (!cleanSentence) {
                    return;
                }

                if (
                    (currentChunk + " " + cleanSentence).length
                    <= 450
                ) {

                    currentChunk =
                        currentChunk
                            ? currentChunk + " " + cleanSentence
                            : cleanSentence;

                } else {

                    if (currentChunk) {
                        chunks.push(currentChunk);
                    }

                    currentChunk = cleanSentence;
                }
            });

            if (currentChunk) {
                chunks.push(currentChunk);
            }

            return chunks;
        }

        const speechChunks =
            createSpeechChunks(reportText);

        function loadAvailableVoice() {

            if (!("speechSynthesis" in window)) {
                return;
            }

            const voices =
                window.speechSynthesis.getVoices();

            if (!voices || voices.length === 0) {
                return;
            }

            availableVoice =
                voices.find(function(voice) {
                    return voice.lang === "en-US";
                });

            if (!availableVoice) {
                availableVoice =
                    voices.find(function(voice) {
                        return voice.lang === "en-GB";
                    });
            }

            if (!availableVoice) {
                availableVoice =
                    voices.find(function(voice) {
                        return voice.lang &&
                            voice.lang.toLowerCase().startsWith("en");
                    });
            }

            if (!availableVoice && voices.length > 0) {
                availableVoice = voices[0];
            }
        }

        if ("speechSynthesis" in window) {

            loadAvailableVoice();

            window.speechSynthesis.onvoiceschanged =
                function() {
                    loadAvailableVoice();
                };
        }

        function updateStatus(message) {

            const status =
                document.getElementById("voiceStatus");

            if (status) {
                status.innerText = message;
            }
        }

        function speakCurrentChunk(startPosition) {

            if (!("speechSynthesis" in window)) {

                updateStatus(
                    "❌ Text-to-speech is not supported by this browser."
                );

                return;
            }

            if (currentChunkIndex >= speechChunks.length) {

                currentChunkIndex = 0;
                currentChunkPosition = 0;
                speechStartPosition = 0;
                speech = null;
                isPaused = false;
                isStopped = false;
                isChangingSpeed = false;

                updateStatus("✅ Finished");

                return;
            }

            const chunk =
                speechChunks[currentChunkIndex];

            if (!chunk) {

                currentChunkIndex++;
                currentChunkPosition = 0;
                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;
            }

            let position =
                typeof startPosition === "number"
                    ? startPosition
                    : currentChunkPosition;

            if (position < 0) {
                position = 0;
            }

            if (position >= chunk.length) {

                currentChunkIndex++;
                currentChunkPosition = 0;
                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;
            }

            const remainingText =
                chunk.substring(position);

            if (!remainingText.trim()) {

                currentChunkIndex++;
                currentChunkPosition = 0;
                speechStartPosition = 0;

                speakCurrentChunk(0);

                return;
            }

            currentChunkPosition = position;
            speechStartPosition = position;

            speechSession++;

            const thisSession =
                speechSession;

            speech =
                new SpeechSynthesisUtterance(
                    remainingText
                );

            speech.rate = currentSpeed;
            speech.pitch = 1;
            speech.volume = 1;

            if (availableVoice) {
                speech.voice = availableVoice;
            }

            if (
                availableVoice &&
                availableVoice.lang
            ) {

                speech.lang =
                    availableVoice.lang;

            } else {

                speech.lang =
                    "en-US";
            }

            isStopped = false;

            speech.onstart = function(){

                if (thisSession !== speechSession) {
                    return;
                }

                isPaused = false;

                updateStatus(
                    "🔊 Speaking at " +
                    currentSpeed +
                    "×..."
                );
            };

            speech.onboundary = function(event) {

                if (thisSession !== speechSession) {
                    return;
                }

                if (
                    typeof event.charIndex === "number"
                ) {

                    currentChunkPosition =
                        speechStartPosition +
                        event.charIndex;
                }
            };

            speech.onpause = function(event) {

                if (thisSession !== speechSession) {
                    return;
                }

                if (
                    event &&
                    typeof event.charIndex === "number"
                ) {

                    currentChunkPosition =
                        speechStartPosition +
                        event.charIndex;
                }

                isPaused = true;

                if (isChangingSpeed) {

                    updateStatus(
                        "🔄 Changing speed..."
                    );

                } else {

                    updateStatus(
                        "⏸️ Paused — press Play to continue"
                    );
                }
            };

            speech.onresume = function() {

                if (thisSession !== speechSession) {
                    return;
                }

                isPaused = false;

                updateStatus(
                    "🔊 Speaking at " +
                    currentSpeed +
                    "×..."
                );
            };

            speech.onend = function() {

                if (thisSession !== speechSession) {
                    return;
                }

                speech = null;

                if (isPaused) {
                    return;
                }

                if (isChangingSpeed) {
                    return;
                }

                currentChunkIndex++;
                currentChunkPosition = 0;
                speechStartPosition = 0;

                if (isStopped) {
                    return;
                }

                setTimeout(function() {

                    if (
                        thisSession !== speechSession ||
                        isStopped ||
                        isPaused ||
                        isChangingSpeed
                    ) {
                        return;
                    }

                    speakCurrentChunk(0);

                }, 40);
            };

            speech.onerror = function(event) {

                if (thisSession !== speechSession) {
                    return;
                }

                if (
                    event.error === "canceled" ||
                    event.error === "interrupted"
                ) {
                    return;
                }

                speech = null;

                updateStatus(
                    "❌ Voice playback error. Please press Play again."
                );
            };

            window.speechSynthesis.speak(
                speech
            );
        }

        function playSpeech() {

            if (!("speechSynthesis" in window)) {

                updateStatus(
                    "❌ Text-to-speech is not supported by this browser."
                );

                return;
            }

            loadAvailableVoice();

            if (isPaused) {

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

                setTimeout(function() {

                    if (
                        !isStopped &&
                        !isPaused
                    ) {

                        speakCurrentChunk(
                            savedPosition
                        );
                    }

                }, 200);

                return;
            }

            if (
                speech &&
                window.speechSynthesis.speaking
            ) {
                return;
            }

            if (
                currentChunkIndex >=
                speechChunks.length
            ) {

                currentChunkIndex = 0;
                currentChunkPosition = 0;
                speechStartPosition = 0;
            }

            isStopped = false;
            isPaused = false;
            isChangingSpeed = false;

            window.speechSynthesis.cancel();

            setTimeout(function() {

                if (!isStopped) {

                    speakCurrentChunk(
                        currentChunkPosition
                    );
                }

            }, 150);
        }

        function pauseSpeech() {

            if (!("speechSynthesis" in window)) {
                return;
            }

            if (
                !speech ||
                isPaused ||
                isStopped
            ) {
                return;
            }

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

            setTimeout(function() {

                if (isPaused) {

                    updateStatus(
                        "⏸️ Paused — press Play to continue"
                    );
                }

            }, 250);
        }

        function stopSpeech() {

            if ("speechSynthesis" in window) {

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
            }
        }

        function changeSpeed() {

            const selectedSpeed =
                parseFloat(
                    document.getElementById("speed").value
                );

            if (isNaN(selectedSpeed)) {
                return;
            }

            currentSpeed =
                selectedSpeed;

            if (!("speechSynthesis" in window)) {
                return;
            }

            if (
                speech &&
                window.speechSynthesis.speaking &&
                !isPaused
            ){

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

                setTimeout(function() {

                    if (!isChangingSpeed) {
                        return;
                    }

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

                    setTimeout(function() {

                        if (!isStopped) {

                            isChangingSpeed = false;

                            speakCurrentChunk(
                                savedPosition
                            );
                        }

                    }, 200);

                }, 250);

                return;
            }

            if (isPaused) {

                updateStatus(
                    "⏸️ Paused — " +
                    currentSpeed +
                    "× selected. Press Play to continue."
                );

                return;
            }
        }

        </script>
    """

    voice_html = voice_html.replace(
        "__REPORT_JSON__",
        report_json
    )

    components.html(
        voice_html,
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
# CUSTOM CSS — EXACT BLUE / NAVY THEME
# =========================================================

st.markdown("""
<style>

/* =========================================================
   MECHCARE AI — EXACT SCREENSHOT BLUE / NAVY THEME
   ========================================================= */

:root {

    --bg-main: #031A39;
    --bg-main-dark: #02152D;

    --bg-sidebar: #032D5F;
    --bg-sidebar-dark: #031F43;

    --bg-card: #061B38;
    --bg-card-light: #102948;
    --bg-card-hover: #0A2342;

    --border: #124A78;
    --border-soft: #0D355C;
    --border-bright: #1A5F91;

    --primary: #0066C6;
    --primary-dark: #0055A8;

    --blue-bright: #008FE0;
    --accent: #00A9E9;
    --accent-light: #13C6E8;

    --success: #00D084;
    --warning: #F5B942;
    --danger: #B82F38;

    --pause: #335571;
    --offline: #637C96;

    --text-primary: #E8F1FA;
    --text-secondary: #B7CBE0;
    --text-muted: #8FA8C1;
    --text-disabled: #637C96;
}


.stApp {

    background:

        radial-gradient(
            circle at 91% 4%,
            rgba(0,169,233,0.08),
            transparent 23%
        ),

        radial-gradient(
            circle at 8% 45%,
            rgba(0,102,198,0.08),
            transparent 30%
        ),

        linear-gradient(
            135deg,
            #02152D 0%,
            #031A39 48%,
            #02182F 100%
        );

    color: var(--text-primary);
}


.main .block-container {

    padding-top: 1.2rem;
    padding-bottom: 2rem;

    max-width: 1500px;
}


[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {

    color: var(--text-secondary) !important;
}


[data-testid="stMarkdownContainer"] strong {

    color: var(--text-primary) !important;
}


[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {

    color: var(--text-primary) !important;
}


section[data-testid="stSidebar"] {

    background:

        linear-gradient(
            180deg,
            #032D5F 0%,
            #032650 45%,
            #021F42 100%
        );

    border-right: 1px solid #124A78;
}


section[data-testid="stSidebar"] > div {

    background: transparent;
}


section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {

    color: var(--text-secondary);
}


.sidebar-brand {

    padding: 10px 7px 20px 7px;

    border-bottom: 1px solid #124A78;

    margin-bottom: 18px;

    background:

        linear-gradient(
            135deg,
            rgba(0,102,198,0.18),
            rgba(0,169,233,0.05)
        );

    border-radius: 0 0 12px 12px;
}


.sidebar-brand-top {

    display: flex;

    align-items: center;

    gap: 11px;
}


.sidebar-gear {

    width: 42px;
    height: 42px;

    border-radius: 11px;

    display: flex;

    align-items: center;
    justify-content: center;

    background:

        linear-gradient(
            135deg,
            #0066C6,
            #00A9E9
        );

    color: white;

    font-size: 21px;

    box-shadow:
        0 0 24px rgba(0,169,233,0.28);
}


.sidebar-brand-title {

    font-size: 20px;

    font-weight: 800;

    color: #F1F7FD;

    letter-spacing: -0.4px;
}


.sidebar-brand-subtitle {

    font-size: 9px;

    color: #63D9F4;

    letter-spacing: 1.7px;

    margin-top: 2px;
}


.sidebar-section-title {

    color: #73CFF1;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 1.5px;

    text-transform: uppercase;

    margin: 18px 4px 9px 4px;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label {

    background: transparent;

    border-radius: 9px;

    padding: 9px 11px;

    margin-bottom: 3px;

    transition: all 0.2s ease;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label:hover {

    background: rgba(0,102,198,0.22);

    color: white;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label p {

    color: #D0E0EF !important;

    font-weight: 600 !important;
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label:has(input:checked) {

    background:

        linear-gradient(
            90deg,
            #0072D2,
            #0060B8
        ) !important;

    border: 1px solid rgba(0,169,233,0.45);

    box-shadow:
        0 5px 18px rgba(0,102,198,0.28);
}


section[data-testid="stSidebar"]
div[data-testid="stRadio"] label:has(input:checked) p {

    color: #FFFFFF !important;

    font-weight: 800 !important;
}


section[data-testid="stSidebar"] .stButton > button {

    background:

        linear-gradient(
            135deg,
            #0A3B6A,
            #082E55
        ) !important;

    border: 1px solid #15517E !important;

    color: #DCEAF6 !important;

    border-radius: 9px !important;

    font-weight: 650 !important;

    min-height: 42px;

    box-shadow:
        0 4px 14px rgba(0,0,0,0.20);

    transition: all 0.2s ease !important;
}


section[data-testid="stSidebar"] .stButton > button:hover {

    background:

        linear-gradient(
            135deg,
            #006FCF,
            #008EDB
        ) !important;

    border-color: #00A9E9 !important;

    color: white !important;

    transform: translateY(-1px);

    box-shadow:
        0 7px 22px rgba(0,122,210,0.30);
}


[data-baseweb="select"] > div {

    background: #061F40 !important;

    border: 1px solid #15517E !important;

    color: #E8F1FA !important;

    border-radius: 8px !important;
}


[data-baseweb="select"] span {

    color: #E8F1FA !important;
}


div[data-baseweb="input"] {

    background: #061F40 !important;

    border: 1px solid #15517E !important;

    border-radius: 8px !important;
}


div[data-baseweb="input"] input {

    color: #E8F1FA !important;
}


textarea {

    background: #061F40 !important;

    color: #E8F1FA !important;

    border: 1px solid #15517E !important;

    border-radius: 9px !important;
}


input {

    color: #E8F1FA !important;
}


textarea::placeholder,
input::placeholder {

    color: #7892AA !important;
}


[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"]:focus-within,
textarea:focus {

    border-color: #00A9E9 !important;

    box-shadow:
        0 0 0 1px rgba(0,169,233,0.25) !important;
}


.stButton > button {

    background:

        linear-gradient(
            135deg,
            #0066C6,
            #0055A8
        ) !important;

    color: #FFFFFF !important;

    border: 1px solid rgba(0,169,233,0.40) !important;

    border-radius: 9px !important;

    font-weight: 700 !important;

    min-height: 42px;

    transition: all 0.2s ease !important;

    box-shadow:
        0 5px 18px rgba(0,102,198,0.22);
}


.stButton > button:hover {

    background:

        linear-gradient(
            135deg,
            #00A9E9,
            #0066C6
        ) !important;

    border-color: #00C4EF !important;

    transform: translateY(-1px);

    box-shadow:
        0 7px 25px rgba(0,169,233,0.28);
}


.top-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding: 15px 20px;

    background:

        linear-gradient(
            90deg,
            rgba(4,28,57,0.96),
            rgba(2,23,49,0.96)
        );

    border: 1px solid #124A78;

    border-radius: 13px;

    margin-bottom: 15px;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.25);
}


.top-title {

    color: #EAF4FC;

    font-size: 18px;

    font-weight: 800;
}


.top-subtitle {

    color: #8EA9C1;

    font-size: 12px;

    margin-top: 3px;
}


.top-icons {

    color: #65CFEF;

    font-size: 18px;

    letter-spacing: 8px;
}


.online-badge {

    color: #00D084;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 0.8px;

    padding: 7px 11px;

    border-radius: 20px;

    background: rgba(0,208,132,0.08);

    border: 1px solid rgba(0,208,132,0.25);
}


.info-card {

    display: flex;

    align-items: center;

    gap: 13px;

    background: #061B38;

    border: 1px solid #124A78;

    border-left: 3px solid #00A9E9;

    border-radius: 11px;

    padding: 14px 17px;

    margin-bottom: 18px;

    box-shadow:
        0 5px 22px rgba(0,0,0,0.20);
}


.info-icon {

    font-size: 22px;

    color: #00B9EF;
}


.info-text {

    color: #B7CBE0;

    font-size: 13px;

    line-height: 1.5;
}


.info-text strong {

    color: #EDF6FD;
}


.hero {

    position: relative;

    overflow: hidden;

    background:

        linear-gradient(
            135deg,
            rgba(0,102,198,0.18),
            rgba(0,169,233,0.055)
        ),
        #061B38;

    border: 1px solid #124A78;

    border-radius: 16px;

    padding: 26px 28px;

    margin-bottom: 22px;

    box-shadow:
        0 10px 35px rgba(0,0,0,0.24);
}


.hero::after {

    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    right: -70px;
    top: -80px;

    border-radius: 50%;

    border: 1px solid rgba(0,169,233,0.20);

    box-shadow:
        0 0 60px rgba(0,169,233,0.08);
}


.hero h1 {

    margin: 0 0 6px 0;

    color: #F0F7FD !important;

    font-size: 31px;

    font-weight: 850;
}


.hero h3 {

    margin: 0 0 11px 0;

    color: #00B7EE !important;

    font-size: 16px;
}


.hero p {

    margin: 0;

    color: #B7CBE0 !important;

    max-width: 900px;

    line-height: 1.65;

    font-size: 13px;
}


.section-header {

    color: #EAF3FB;

    font-size: 19px;

    font-weight: 800;

    margin: 8px 0 12px 0;
}


.section-description {

    color: #8EA8C0;

    font-size: 12px;

    margin-bottom: 15px;
}


.ui-card {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 13px;

    padding: 17px;

    margin-bottom: 14px;

    box-shadow:
        0 7px 25px rgba(0,0,0,0.18);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}


.ui-card:hover {

    border-color: rgba(0,169,233,0.48);

    transform: translateY(-1px);

    box-shadow:
        0 9px 30px rgba(0,169,233,0.08);
}


.card-title {

    color: #EAF3FB;

    font-size: 15px;

    font-weight: 800;

    margin-bottom: 6px;
}


.card-description {

    color: #8FA8C1;

    font-size: 12px;

    line-height: 1.5;
}


.workflow-card {

    background:

        linear-gradient(
            135deg,
            #102948,
            #071F3D
        );

    border: 1px solid #124A78;

    border-left: 3px solid #0072D2;

    border-radius: 11px;

    padding: 14px;

    min-height: 110px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.16);

    transition: all 0.2s ease;
}


.workflow-card:hover {

    border-left-color: #00A9E9;

    border-color: rgba(0,169,233,0.40);

    box-shadow:
        0 0 22px rgba(0,169,233,0.10);

    transform: translateY(-1px);
}


.workflow-number {

    color: #00B9EF;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 1px;
}


.workflow-title {

    color: #EAF3FB;

    font-size: 14px;

    font-weight: 800;

    margin-top: 5px;
}


.workflow-text {

    color: #8FA8C1;

    font-size: 11px;

    margin-top: 5px;

    line-height: 1.45;
}


.status-card {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 11px;

    padding: 14px;

    min-height: 95px;
}


.status-label {

    color: #809AB3;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 1px;
}


.status-value {

    color: #EAF3FB;

    font-size: 18px;

    font-weight: 800;

    margin-top: 7px;
}


.status-green {

    color: #00D084;
}


.status-yellow {

    color: #F5B942;
}


.status-red {

    color: #FF555D;
}


.quick-card {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 13px;

    padding: 15px;

    margin-bottom: 13px;

    box-shadow:
        0 6px 22px rgba(0,0,0,0.16);
}


.quick-title {

    color: #EAF3FB;

    font-size: 14px;

    font-weight: 800;

    margin-bottom: 12px;
}


.quick-row {

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding: 9px 0;

    border-bottom: 1px solid #0D355C;
}


.quick-row:last-child {

    border-bottom: none;
}


.quick-label {

    color: #829CB5;

    font-size: 11px;
}


.quick-value {

    color: #BFD2E4;

    font-size: 11px;

    font-weight: 700;
}


.online-dot {

    display: inline-block;

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #00D084;

    box-shadow:
        0 0 9px rgba(0,208,132,0.65);

    margin-right: 5px;
}


.question-card {

    background: #0B2848;

    border: 1px solid #124A78;

    border-radius: 9px;

    padding: 11px 12px;

    margin-bottom: 7px;

    transition: all 0.2s ease;
}


.question-card:hover {

    border-color: rgba(0,169,233,0.45);

    background: #103454;
}


.question-number {

    color: #00B9EF;

    font-size: 9px;

    font-weight: 800;

    margin-right: 7px;
}


.question-text {

    color: #B7CBE0;

    font-size: 11px;

    line-height: 1.4;
}


.profile-header {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 14px;
}


.profile-icon {

    width: 36px;
    height: 36px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 9px;

    background:
        rgba(0,102,198,0.17);

    color: #00B9EF;

    border: 1px solid rgba(0,169,233,0.25);
}


.profile-title {

    color: #EAF3FB;

    font-size: 15px;

    font-weight: 800;
}


.profile-subtitle {

    color: #809AB3;

    font-size: 10px;
}


.result-card {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 14px;

    padding: 18px;

    margin-bottom: 15px;

    box-shadow:
        0 8px 28px rgba(0,0,0,0.18);
}


.result-title {

    color: #EAF3FB;

    font-size: 16px;

    font-weight: 800;

    margin-bottom: 10px;
}


.result-title span {

    color: #00B9EF;
}


.checklist-card {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 13px;

    padding: 17px;
}


.progress-label {

    color: #809AB3;

    font-size: 11px;

    margin-bottom: 6px;
}


div[data-testid="stProgressBar"] > div {

    background: #0C3558;
}


div[data-testid="stProgressBar"] > div > div {

    background:

        linear-gradient(
            90deg,
            #0066C6,
            #00A9E9
        );
}


.stDownloadButton > button {

    width: 100%;

    background:

        linear-gradient(
            90deg,
            #0066C6 0%,
            #008DDB 52%,
            #00B5E8 100%
        ) !important;

    color: #FFFFFF !important;

    border: none !important;

    border-radius: 9px !important;

    font-weight: 800 !important;

    min-height: 46px;

    box-shadow:
        0 7px 25px rgba(0,102,198,0.30);

    transition: all 0.2s ease !important;
}


.stDownloadButton > button:hover {

    background:

        linear-gradient(
            90deg,
            #008DDB,
            #00B5E8
        ) !important;

    box-shadow:
        0 9px 30px rgba(0,169,233,0.32);

    transform: translateY(-1px);
}


[data-testid="stCheckbox"] label {

    color: #B7CBE0 !important;
}


[data-testid="stCheckbox"] label:hover {

    color: #EAF3FB !important;
}


[data-testid="stMetric"] {

    background: #061B38;

    border: 1px solid #124A78;

    border-radius: 10px;

    padding: 12px;
}


[data-testid="stMetricLabel"] {

    color: #809AB3 !important;
}


[data-testid="stMetricValue"] {

    color: #EAF3FB !important;
}


hr {

    border-color: #0D355C !important;
}


.app-footer {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-top: 35px;

    padding: 14px 4px;

    border-top: 1px solid #0D355C;
}


.footer-left {

    color: #718AA3;

    font-size: 10px;
}


.footer-right {

    color: #B7CBE0;

    font-size: 11px;

    font-weight: 600;
}


::-webkit-scrollbar {

    width: 8px;
}


::-webkit-scrollbar-track {

    background: #02152D;
}


::-webkit-scrollbar-thumb {

    background: #15517E;

    border-radius: 10px;
}


::-webkit-scrollbar-thumb:hover {

    background: #0072D2;
}


@media (max-width: 900px) {

    .top-header {

        flex-direction: column;

        align-items: flex-start;

        gap: 10px;
    }


    .hero h1 {

        font-size: 25px;
    }


    .top-icons {

        display: none;
    }

}

</style>
""", unsafe_allow_html=True)


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
        "📋  Active Machine Profiles",
        use_container_width=True
    )

    st.button(
        "🛠️  Maintenance Logs",
        use_container_width=True
    )

    st.button(
        "📄  Generated Reports",
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

    st.caption(
        "Engineering decision support system"
    )


# =========================================================
# TOP HEADER
# =========================================================

st.html(
    """
    <div class="top-header">

        <div>

            <div class="top-title">
                AI-Powered Machine Monitoring
            </div>

            <div class="top-subtitle">
                Smarter Diagnostics &nbsp;|&nbsp;
                Safer Operations &nbsp;|&nbsp;
                Engineering Intelligence
            </div>

        </div>

        <div class="top-actions">

            <div class="top-action">
                🔔
            </div>

            <div class="top-action">
                ☀️
            </div>

            <div class="top-action">
                👤
            </div>

            <div class="top-action">
                ⋮
            </div>

            <div class="online-badge">
                ● AI SYSTEM READY
            </div>

        </div>

    </div>
    """
)


# =========================================================
# ENGINEERING INFORMATION CARD
# =========================================================

st.html(
    """
    <div class="info-card">

        <div class="info-icon">
            ⚙️
        </div>

        <div>

            <div class="info-title">
                Preventive Maintenance Reminder
            </div>

            <div class="info-text">
                Follow ABB's quarterly alignment and lubrication
                schedule to keep the pump operating safely.
            </div>

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

        <h1>
            ⚙️ MechCare AI
        </h1>

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

    st.html(
        '<div class="section-title" style="margin-top:22px;">💡 Engineering Questions</div>'
    )

    st.html(
        '<div class="section-description">Useful questions to consider during machine inspection.</div>'
    )

    engineering_questions = [

        ("01", "What changed before the problem started?"),
        ("02", "Does the symptom increase with machine speed?"),
        ("03", "Does the problem appear under heavy load?"),
        ("04", "Is the machine temperature higher than normal?"),
        ("05", "Has the machine recently been repaired or adjusted?"),
        ("06", "Is the vibration coming from a specific component?"),
        ("07", "When was the machine last lubricated?"),
        ("08", "Are there any unusual sounds, smells or leaks?"),
        ("09", "Has machine performance gradually decreased?"),
        ("10", "Could operating conditions have changed?")

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

    workflow_columns = st.columns(
        4,
        gap="small"
    )

    for column, agent in zip(
        workflow_columns,
        workflow
    ):

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

    st.write("")

    analyze_button = st.button(
        "🔍 Analyze Machine Problem",
        use_container_width=True
    )

    if analyze_button:

        if (
            not problem_description.strip()
            and not selected_symptoms
        ):

            st.warning(
                "Please provide a problem description or select at least one symptom."
            )

        else:

            selected_symptoms_text = (

                ", ".join(selected_symptoms)

                if selected_symptoms

                else "No specific symptoms selected"

            )

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

        problem_analysis = result["problem_analysis"]
        diagnosis_result = result["diagnosis"]
        final_report = result["final_report"]

        st.divider()

        st.html(
            '<div class="section-title">📊 Machine Health Dashboard</div>'
        )

        st.html(
            '<div class="section-description">AI-generated health and maintenance overview based on the current engineering analysis.</div>'
        )

        report_text = final_report

        priority = "Not specified"

        priority_match = re.search(
            r"(?im)^\s*##\s*Priority\s*$([\s\S]*?)(?=^\s*##\s+|\Z)",
            report_text
        )

        if priority_match:

            priority_section = priority_match.group(1).strip()

            severity_match = re.search(
                r"\b(Critical|Urgent|High|Medium|Moderate|Low)\b",
                priority_section,
                re.IGNORECASE
            )

            if severity_match:

                priority = (
                    severity_match
                    .group(1)
                    .capitalize()
                )

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

        dash1, dash2, dash3, dash4 = st.columns(
            4,
            gap="small"
        )

        with dash1:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-label">
                        MACHINE
                    </div>

                    <div class="status-value">
                        🏭 {machine_type}
                    </div>

                    <div style="color:#809AB3;font-size:11px;margin-top:5px;">
                        {machine_id}
                    </div>

                </div>
                """
            )

        with dash2:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-label">
                        HEALTH STATUS
                    </div>

                    <div class="status-value">
                        {health_status}
                    </div>

                    <div style="color:#809AB3;font-size:11px;margin-top:5px;">
                        AI assessment
                    </div>

                </div>
                """
            )

        with dash3:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-label">
                        PRIORITY
                    </div>

                    <div class="status-value">
                        ⚠️ {priority}
                    </div>

                    <div style="color:#809AB3;font-size:11px;margin-top:5px;">
                        Primary AI priority
                    </div>

                </div>
                """
            )

        with dash4:

            st.html(
                f"""
                <div class="status-card">

                    <div class="status-label">
                        MAINTENANCE
                    </div>

                    <div class="status-value">
                        🔧 {maintenance_status}
                    </div>

                    <div style="color:#809AB3;font-size:11px;margin-top:5px;">
                        Recommended action
                    </div>

                </div>
                """
            )

        st.markdown("")

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

        st.html(
            '<div class="section-title">📈 Additional Data Recommended</div>'
        )

        st.html(
            '<div class="section-description">Collecting these measurements or observations can help confirm the possible machine fault.</div>'
        )

        st.markdown(
            problem_analysis
        )

        st.html(
            '<div class="section-title" style="margin-top:25px;">🧠 Possible Faults & Diagnostic Checks</div>'
        )

        st.html(
            '<div class="section-description">Possible causes, their relationship with the symptoms, and suggested confirmation checks.</div>'
        )

        st.markdown(
            diagnosis_result
        )

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
            completed_count /
            len(checklist_items)
        )

        st.progress(
            progress_value,
            text=(
                f"{completed_count} of "
                f"{len(checklist_items)} checks completed"
            )
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

        st.html(
            '<div class="section-title" style="margin-top:25px;">📋 Engineering Analysis Report</div>'
        )

        st.html(
            '<div class="section-description">Generated by the MechCare AI multi-agent engineering workflow.</div>'
        )

        st.markdown(
            final_report
        )

        st.html(
            '<div class="section-title" style="margin-top:25px;">🔊 Listen to AI Results</div>'
        )

        st.html(
            '<div class="section-description">Listen to the complete AI analysis, diagnosis, and final engineering report.</div>'
        )

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

        st.html(
            '<div class="section-title" style="margin-top:25px;">📄 Engineering Report Export</div>'
        )

        st.html(
            '<div class="section-description">Generate and download the final engineering report as a PDF.</div>'
        )

        st.html(
            """
            <div class="ui-card">

                <div class="card-label">
                    ENGINEERING REPORT EXPORT
                </div>

                <div class="card-value">
                    📄 Final Engineering Report
                </div>

                <div class="card-small">
                    Generate and download the final engineering report
                    as a PDF for documentation and engineering review.
                </div>

            </div>
            """
        )

        pdf_filename = "MechCare_AI_Report.pdf"

        create_pdf_report(
            pdf_filename,
            machine_type,
            machine_id,
            manufacturer,
            final_report
        )

        with open(
            pdf_filename,
            "rb"
        ) as pdf_file:

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
