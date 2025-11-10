import streamlit as st
import base64
import requests
import json
from utils import speak_polly

st.set_page_config(page_title="FortunAI", page_icon="🎯", layout="centered")

if "profile_loaded" not in st.session_state:
    st.session_state.profile_loaded = False
if "summoner_data" not in st.session_state:
    st.session_state.summoner_data = {}
if "mf_chat" not in st.session_state:
    st.session_state.mf_chat = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None


st.markdown("""
    <style>
        body { background-color: #ffe6f0; }
        .header-container { text-align: center; margin-bottom: 0; }
        .main-title {
            color: #ff3388; font-size: 2.8em; font-weight: 800;
            margin-bottom: 0.25em; margin-top: 0.2em;
        }
        .subtitle {
            text-align: center; font-size: 1.15em; color: #333;
            margin-top: -0.2em; line-height: 1.6em;
        }
        h1 a, h2 a, h3 a { display: none !important; }
    </style>

    <div class='header-container'>
        <h1 class='main-title'>🌸 FortunAI: Your Battle Companion</h1>
        <p class='subtitle'>
            Welcome aboard, <b>Summoner</b>! Let’s review your Miss Fortune matches together.<br>
            I’ll highlight your strengths, habits, and next areas to improve. 💋
        </p>
    </div>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .pulse-container {
        display: flex; justify-content: center; align-items: center;
        margin-top: 20px; margin-bottom: 20px;
    }
    .blob {
        width: 280px; height: 280px; border-radius: 50%;
        background: radial-gradient(circle, #ffcce0 0%, #ff99bb 80%);
        box-shadow: 0 0 30px rgba(255, 100, 150, 0.5);
        animation: idle-pulse 3s ease-in-out infinite;
    }
    @keyframes idle-pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(255,0,102,0.4); }
        50% { transform: scale(1.05); box-shadow: 0 0 40px rgba(255,0,102,0.7); }
    }
    </style>
    <div class="pulse-container"><div class="blob" id="mf-blob"></div></div>
""", unsafe_allow_html=True)


speak_polly("Ahoy, Summoner. What’s your in-game name and tagline?")
st.caption("🗣️ FortunAI is ready! Enter your details below to fetch your match history.")


if not st.session_state.profile_loaded:
    with st.form("summoner_form"):
        name = st.text_input("Summoner Name")
        tag = st.text_input("Tagline (e.g. NA1, EUW1)")
        submit = st.form_submit_button("Submit")

    if submit:
        if not name or not tag:
            st.warning("Please enter both a Summoner Name and Tagline.")
        else:
            st.info(f"Fetching data for **{name}#{tag}**... ⏳")
            try:
                response = requests.post(
                    "https://6xz8842kf7.execute-api.us-east-1.amazonaws.com/Prod/coach",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"game_name": name, "tag_line": tag})
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.profile_loaded = True
                    st.session_state.summoner_data = data
                    st.rerun()
                else:
                    st.error(f"Backend returned status code {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if st.session_state.profile_loaded:
    data = st.session_state.summoner_data

    stats = data.get("stats", {})
    avg_cs = stats.get("avg_cs10")
    avg_deaths = stats.get("avg_deaths_pre_mythic")
    avg_dragons = stats.get("avg_dragon_presence")


    if any([avg_cs, avg_deaths, avg_dragons]):
        st.markdown("### 🏅 Your Strengths This Season")
        if avg_cs:
            st.markdown(f"- **Lane Control:** Averaged **{avg_cs:.1f} CS by 10 minutes.** Solid early farming!")
        if avg_deaths is not None:
            st.markdown(f"- **Early Survival:** Only **{avg_deaths} deaths** before Mythic — staying alive pays off.")
        if avg_dragons:
            st.markdown(f"- **Objective Presence:** Present in **{avg_dragons:.1f}%** of dragon fights — keep improving your timing!")
    else:
        st.info("No recent match data found — go play a few rounds, sugar!")


    st.markdown("### ⚔️ Drills to Practice")
    drills = data.get("drill_next", [])
    if drills:
        for d in drills:
            st.markdown(f"- {d}")
    else:
        st.info("No drills queued — looks like you’ve been practicing, sugar!")


    st.markdown("### 💋 Miss Fortune’s Verdict")
    celebration = data.get("celebration", "")
    roast = data.get("roast", "")
    if celebration:
        st.success(f"💖 {celebration}")
    if roast:
        st.warning(f"🔥 {roast}")


    st.markdown("### 💬 Talk with Miss Fortune")

    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Say something to Miss Fortune:")
        send = st.form_submit_button("Send")

    if send and user_msg:
        st.session_state.mf_chat.append(("You", user_msg))
        try:
            response = requests.post(
                url = "https://6xz8842kf7.execute-api.us-east-1.amazonaws.com/Prod/talk",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"message": user_msg})
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "Can't hear ya over the gunfire, sugar.")
                st.session_state.mf_chat.append(("Miss Fortune", reply))
                if "audio" in data and data["audio"]:
                    st.session_state.last_audio = data["audio"]
            else:
                st.session_state.mf_chat.append(("Miss Fortune", "Backend’s quiet — maybe she’s reloading."))
        except Exception:
            st.session_state.mf_chat.append(("Miss Fortune", "Network’s down, sugar. Try again soon."))

    for speaker, msg in st.session_state.mf_chat:
        if speaker == "You":
            st.markdown(f"🧍 **You:** {msg}")
        else:
            st.markdown(f"💋 **Miss Fortune:** {msg}")

    if st.session_state.last_audio:
        st.audio(base64.b64decode(st.session_state.last_audio), format="audio/mp3")
