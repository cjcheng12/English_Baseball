import streamlit as st
import random
import json
import time
from gtts import gTTS
import io
import copy
import pandas as pd

# --- CONFIGURATION ---
ROUNDS_PER_GAME = 20
MASTERY_THRESHOLD = 5
COOLDOWN_SECONDS = 86400  # 24 Hours

# --- THE 150 VOCABULARY LIST WITH EXAMPLES ---
# NOTE: keep your full 150 items here. This sample shows the structure.
initial_word_data = [
    {"word": "Pitcher", "def": "投手", "ex": "The ___ threw a fast ball at 100 mph!"},
    {"word": "Catcher", "def": "捕手", "ex": "The ___ caught the ball behind home plate."},
    {"word": "Umpire", "def": "裁判", "ex": "The ___ shouted 'Strike!' to the batter."},
    {"word": "Inning", "def": "局 (比賽的)", "ex": "The home team scored three runs in the first ___."},
    {"word": "Dugout", "def": "球員休息區", "ex": "The players sat in the ___ waiting for their turn to bat."},
    {"word": "Bullpen", "def": "牛棚", "ex": "The relief pitcher is warming up in the ___."},
    {"word": "Roster", "def": "球員名單", "ex": "The team's ___ includes several young superstars."},
    {"word": "Statistic", "def": "統計數據", "ex": "The batting average is an important ___ for players."},
    {"word": "League", "def": "聯盟", "ex": "Playing in the Major ___ is every player's dream."},
    {"word": "Tournament", "def": "錦標賽", "ex": "Teams from across the country entered the big ___."},
    {"word": "Championship", "def": "冠軍賽", "ex": "They won the ___ and received gold rings."},
    {"word": "Trophy", "def": "獎盃", "ex": "The captain lifted the silver ___ over his head."},
    {"word": "MVP", "def": "最有價值球員", "ex": "Ohtani won the ___ award for his amazing season."},
    {"word": "Rookie", "def": "新秀", "ex": "The young ___ hit a home run in his very first game."},
    {"word": "Veteran", "def": "老將", "ex": "The team relies on the ___ for his years of experience."},
    {"word": "Manager", "def": "總教練", "ex": "The ___ decided to change the pitcher in the 8th inning."},
    {"word": "Stadium", "def": "體育場", "ex": "Thousands of fans packed the ___ for the night game."},
    {"word": "Grand Slam", "def": "滿貫全壘打", "ex": "The bases were loaded when he hit a spectacular ___!"},
    {"word": "Strikeout", "def": "三振出局", "ex": "The pitcher recorded his tenth ___ of the game."},
    {"word": "Walk", "def": "保送", "ex": "The batter didn't swing and earned a ___ to first base."},
    {"word": "Infielder", "def": "內野手", "ex": "The ___ caught the ground ball and threw it to first."},
    {"word": "Outfielder", "def": "外野手", "ex": "The ___ ran back and caught the ball near the wall."},
    {"word": "Mound", "def": "投手丘", "ex": "The pitcher stood on the ___ and looked at the catcher."},
    {"word": "Batter", "def": "打擊者", "ex": "The ___ stepped into the box and gripped the bat."},
    {"word": "Helmet", "def": "頭盔", "ex": "Always wear your ___ to protect your head from the ball."},
    {"word": "Jersey", "def": "球衣", "ex": "He wore his lucky team ___ to every game."},
    {"word": "Mascot", "def": "吉祥物", "ex": "The team ___ danced to cheer the fans."},
    {"word": "Scoreboard", "def": "計分板", "ex": "The ___ showed that the game was tied in the 9th."},
    {"word": "Spectator", "def": "觀眾", "ex": "Every ___ stood up to cheer when the ball left the park."},
    {"word": "Diamond", "def": "棒球場內野", "ex": "The players ran around the ___ after the home run."},

    # ... add the rest of your list here ...
]

# ---------------------------
# Helpers: Initialization & Progress (type-safe)
# ---------------------------
def fresh_initial_state():
    data = copy.deepcopy(initial_word_data)
    for item in data:
        item.setdefault("score", 0)
        item.setdefault("last_correct_time", None)
        item.setdefault("ex", "")

        # normalize types
        try:
            item["score"] = int(item.get("score", 0))
        except Exception:
            item["score"] = 0

        lct = item.get("last_correct_time")
        if lct is None:
            item["last_correct_time"] = None
        else:
            try:
                item["last_correct_time"] = float(lct)
            except Exception:
                item["last_correct_time"] = None

    return data


def merge_progress(loaded):
    """
    Merge uploaded progress into the canonical list by 'word'.
    Keeps your examples from initial_word_data; only merges score/last_correct_time.
    """
    base = fresh_initial_state()
    if not isinstance(loaded, list):
        return base

    index = {w.get("word"): w for w in loaded if isinstance(w, dict) and w.get("word")}
    for item in base:
        src = index.get(item["word"])
        if not src:
            continue

        # score
        if "score" in src:
            try:
                item["score"] = int(src.get("score", 0))
            except Exception:
                pass

        # last_correct_time
        if "last_correct_time" in src:
            lct = src.get("last_correct_time")
            if lct is None:
                item["last_correct_time"] = None
            else:
                try:
                    item["last_correct_time"] = float(lct)
                except Exception:
                    item["last_correct_time"] = None

    return base


# --- SESSION STATE DEFAULTS ---
DEFAULTS = {
    "current_index": 0,
    "game_score": 0,
    "game_active": False,  # False | True | "WON"
    "current_question": None,
    "options": [],
    "feedback": "",
    "current_audio": None,
    "session_words": [],
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = copy.deepcopy(v)

if "vocab_data" not in st.session_state:
    st.session_state.vocab_data = fresh_initial_state()

# ---------------------------
# Audio (cached)
# ---------------------------
@st.cache_data(show_spinner=False)
def tts_mp3_bytes(txt: str) -> bytes:
    try:
        tts = gTTS(text=txt, lang="en")
        f = io.BytesIO()
        tts.write_to_fp(f)
        return f.getvalue()
    except Exception:
        return b""


def get_audio(txt):
    b = tts_mp3_bytes(txt)
    return io.BytesIO(b) if b else None

# ---------------------------
# Game logic
# ---------------------------
def start_game():
    cands = [w for w in st.session_state.vocab_data if w["score"] < MASTERY_THRESHOLD]
    if not cands:
        st.session_state.game_active = "WON"
        return

    st.session_state.session_words = random.sample(cands, min(ROUNDS_PER_GAME, len(cands)))
    st.session_state.current_index = 0
    st.session_state.game_score = 0
    st.session_state.game_active = True
    st.session_state.feedback = ""
    next_q()


def next_q():
    if st.session_state.current_index < len(st.session_state.session_words):
        t = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question = t
        st.session_state.current_audio = get_audio(t["word"])

        # Create multiple choice options (safe)
        pool = [w["def"] for w in st.session_state.vocab_data if w["def"] != t["def"]]
        pool = list(dict.fromkeys(pool))  # de-dup, keep order

        k = min(3, len(pool))
        opts = [t["def"]] + (random.sample(pool, k) if k > 0 else [])
        random.shuffle(opts)
        st.session_state.options = opts
    else:
        st.session_state.game_active = False
        st.session_state.current_question = None
        st.session_state.options = []
        st.session_state.current_audio = None


def check(ans):
    t, now = st.session_state.current_question, time.time()
    if not t:
        return

    # -------- MASTERY RULES (as you designed) --------
    if ans == t["def"]:
        st.session_state.game_score += 1
        for i in st.session_state.vocab_data:
            if i["word"] == t["word"]:
                last = i.get("last_correct_time")
                if last is None or (now - last > COOLDOWN_SECONDS):
                    i["score"] += 1
                    i["last_correct_time"] = now
                    st.session_state.feedback = f"✅ Correct! '{t['word']}' (+1 Mastery Point)"
                else:
                    h = int((COOLDOWN_SECONDS - (now - last)) / 3600)
                    st.session_state.feedback = f"✅ Correct! (Gain next point in {h}h)"
                break
    else:
        st.session_state.feedback = f"❌ Wrong. '{t['word']}' = '{t['def']}' (-1 Point)"
        for i in st.session_state.vocab_data:
            if i["word"] == t["word"]:
                i["score"] = max(0, i["score"] - 1)  # Penalty
                break
    # -----------------------------------------------

    st.session_state.current_index += 1
    next_q()

# ---------------------------
# UI
# ---------------------------
st.set_page_config(page_title="Baseball Vocab", page_icon="⚾")
st.title("⚾ 150 Baseball Superstars Vocab")

# Sidebar: load/save + stats
st.sidebar.header("Progress")

up = st.sidebar.file_uploader("Upload Progress (.json)", type="json")
if up:
    try:
        loaded = json.load(up)
        st.session_state.vocab_data = merge_progress(loaded)
        st.sidebar.success("Loaded!")
    except Exception:
        st.sidebar.error("Invalid file.")

mastered = sum(1 for w in st.session_state.vocab_data if w["score"] >= MASTERY_THRESHOLD)
st.sidebar.metric("Mastered", f"{mastered} / {len(st.session_state.vocab_data)}")

st.sidebar.download_button(
    "💾 Save Progress",
    data=json.dumps(st.session_state.vocab_data, indent=4, ensure_ascii=False),
    file_name="progress.json",
)

# Main screens
if st.session_state.game_active == "WON":
    st.balloons()
    st.success("🏆 MVP! All words mastered!")
    if st.button("Restart Season"):
        st.session_state.vocab_data = fresh_initial_state()
        for k, v in DEFAULTS.items():
            st.session_state[k] = copy.deepcopy(v)
        st.rerun()

elif not st.session_state.game_active:
    st.header("Ready for Batting Practice?")
    if st.button("▶️ Start Game (20 Rounds)", use_container_width=True):
        start_game()
        st.rerun()

    df = pd.DataFrame(st.session_state.vocab_data)
    if not df.empty and "score" in df.columns and df["score"].sum() > 0:
        st.subheader("Current Training Stats")
        st.table(
            df[df["score"] > 0]
            .sort_values("score", ascending=False)
            .head(10)[["word", "def", "score"]]
        )

else:
    total = max(1, len(st.session_state.session_words))  # avoid divide-by-zero
    st.progress(st.session_state.current_index / total)
    st.metric("Session Score", st.session_state.game_score)

    q = st.session_state.current_question
    if q is None:
        st.info("No active question. Click Start Game to begin.")
    else:
        st.markdown(f"## Word: **{q['word']}**")
        st.info(f"💡 **Sentence:** {q.get('ex', '')}")

        if st.session_state.current_audio:
            st.audio(st.session_state.current_audio)

        cols = st.columns(2)
        for i, opt in enumerate(st.session_state.options):
            # include current_index in key to avoid stale button state across reruns
            if cols[i % 2].button(opt, use_container_width=True, key=f"btn_{st.session_state.current_index}_{i}"):
                check(opt)
                st.rerun()

        if st.session_state.feedback:
            if "✅" in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
