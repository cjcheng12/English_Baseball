import streamlit as st
import random
import json
import time
from gtts import gTTS
import io
import copy
import pandas as pd
import re

# =========================
# CONFIGURATION
# =========================
ROUNDS_PER_GAME = 20
MASTERY_THRESHOLD = 5
COOLDOWN_SECONDS = 86400  # 24 hours

# =========================
# FULL 200-WORD VOCAB LIST
# Each item: word / def / ex  (ex uses ___ blank for clean replacement)
# =========================
initial_word_data = [
    # --- 1-50: Baseball terms / nouns ---
    {"word": "Bullpen", "def": "牛棚", "ex": "The reliever warmed up in the ___."},
    {"word": "Roster", "def": "球員名單", "ex": "The team updated its ___ today."},
    {"word": "Statistic", "def": "統計數據", "ex": "OPS is an important ___."},
    {"word": "League", "def": "聯盟", "ex": "He dreams of playing in the major ___."},
    {"word": "Tournament", "def": "錦標賽", "ex": "They entered a national ___."},
    {"word": "Championship", "def": "冠軍賽", "ex": "They won the ___ and celebrated."},
    {"word": "Trophy", "def": "獎盃", "ex": "The captain lifted the ___."},
    {"word": "MVP", "def": "最有價值球員", "ex": "He was named ___ for the season."},
    {"word": "Rookie", "def": "新秀", "ex": "The ___ hit a home run in his debut."},
    {"word": "Veteran", "def": "老將", "ex": "The ___ guided the younger players."},
    {"word": "Manager", "def": "總教練", "ex": "The ___ called for a pitching change."},
    {"word": "Stadium", "def": "體育場", "ex": "Fans packed the ___."},
    {"word": "Grand Slam", "def": "滿貫全壘打", "ex": "He hit a ___ with the bases loaded."},
    {"word": "Strikeout", "def": "三振出局", "ex": "The pitcher recorded a ___."},
    {"word": "Walk", "def": "保送", "ex": "He earned a ___ to first base."},
    {"word": "Helmet", "def": "頭盔", "ex": "Wear a ___ to protect your head."},
    {"word": "Jersey", "def": "球衣", "ex": "He wore his favorite ___."},
    {"word": "Mascot", "def": "吉祥物", "ex": "The ___ danced to cheer the crowd."},
    {"word": "Scoreboard", "def": "計分板", "ex": "The ___ showed a tie game."},
    {"word": "Spectator", "def": "觀眾", "ex": "Every ___ stood up and cheered."},
    {"word": "Diamond", "def": "棒球場內野", "ex": "They ran around the ___ after the win."},
    {"word": "Shortstop", "def": "游擊手", "ex": "The ___ made a smooth backhand play."},
    {"word": "Batting Average", "def": "打擊率", "ex": "His ___ improved this month."},
    {"word": "ERA", "def": "防禦率", "ex": "The pitcher lowered his ___."},
    {"word": "Lineup", "def": "打線／先發名單", "ex": "The ___ has two power hitters."},
    {"word": "Bench", "def": "板凳（替補席）", "ex": "He started the game on the ___."},
    {"word": "Glove", "def": "手套", "ex": "Bring your ___ to practice."},
    {"word": "Bat", "def": "球棒", "ex": "He gripped the ___ tightly."},
    {"word": "Cleats", "def": "釘鞋", "ex": "The player wore new ___."},
    {"word": "Fastball", "def": "快速球", "ex": "He threw a ___ up and in."},
    {"word": "Curveball", "def": "曲球", "ex": "The ___ broke sharply."},
    {"word": "Slider", "def": "滑球", "ex": "His ___ fooled the hitter."},
    {"word": "Changeup", "def": "變速球", "ex": "The ___ looked like a fastball at first."},
    {"word": "Steal", "def": "盜壘", "ex": "He tried to ___ second base."},
    {"word": "Bunt", "def": "觸擊", "ex": "He laid down a perfect ___."},

    # --- 51-100: Advanced adjectives (50) ---
    {"word": "Phenomenal", "def": "非凡的", "ex": "His performance was ___ tonight."},
    {"word": "Legendary", "def": "傳奇的", "ex": "That was a ___ moment in baseball history."},
    {"word": "Dominant", "def": "佔優勢的", "ex": "The pitcher was ___ from start to finish."},
    {"word": "Versatile", "def": "全能的", "ex": "He is a ___ player who can play anywhere."},
    {"word": "Aggressive", "def": "積極的", "ex": "The runner made an ___ move toward second."},
    {"word": "Defensive", "def": "防守的", "ex": "They shifted into a ___ alignment."},
    {"word": "Offensive", "def": "進攻的", "ex": "The team has a strong ___ lineup."},
    {"word": "Spectacular", "def": "精彩的", "ex": "That catch was absolutely ___."},
    {"word": "Consistent", "def": "穩定的", "ex": "He is a ___ hitter."},
    {"word": "Athletic", "def": "體格健壯的", "ex": "Shortstops must be very ___."},
    {"word": "Talented", "def": "有天賦的", "ex": "The scout found a ___ teenager."},
    {"word": "Professional", "def": "專業的", "ex": "He handled the interview in a ___ way."},
    {"word": "Competitive", "def": "好勝的", "ex": "She is extremely ___."},
    {"word": "Accurate", "def": "準確的", "ex": "The throw was ___ and on time."},
    {"word": "Powerful", "def": "有力的", "ex": "He has a ___ swing."},
    {"word": "Incredible", "def": "難以置信的", "ex": "It was ___ that he caught it."},
    {"word": "Historic", "def": "歷史性的", "ex": "That was a ___ win."},
    {"word": "Memorable", "def": "難忘的", "ex": "The ending was ___."},
    {"word": "Intense", "def": "激烈的", "ex": "The rivalry is ___."},
    {"word": "Reliable", "def": "可靠的", "ex": "He is the most ___ reliever on the team."},
    {"word": "Remarkable", "def": "卓越的", "ex": "His speed is ___."},
    {"word": "Outstanding", "def": "傑出的", "ex": "She gave an ___ performance."},
    {"word": "Determined", "def": "堅決的", "ex": "He looked ___ to win."},
    {"word": "Confident", "def": "有自信的", "ex": "The batter felt ___ at the plate."},
    {"word": "Ambitious", "def": "有野心的", "ex": "The ___ rookie wants to be the best."},
    {"word": "Energetic", "def": "精力充沛的", "ex": "The crowd was ___ all night."},
    {"word": "Precise", "def": "精確的", "ex": "His control is ___."},
    {"word": "Rapid", "def": "迅速的", "ex": "He has a ___ release."},
    {"word": "Resilient", "def": "有韌性的", "ex": "They stayed ___ after falling behind."},
    {"word": "Strategic", "def": "策略性的", "ex": "It was a ___ decision."},
    {"word": "Dynamic", "def": "充滿活力的", "ex": "He is a ___ leadoff hitter."},
    {"word": "Exceptional", "def": "優越的", "ex": "His defense is ___."},
    {"word": "Fearless", "def": "大膽的", "ex": "The catcher was ___ at the plate."},
    {"word": "Elite", "def": "精英的", "ex": "Only an ___ group makes the team."},
    {"word": "Formidable", "def": "強大的", "ex": "They have a ___ pitching staff."},
    {"word": "Skillful", "def": "熟練的", "ex": "The ___ shortstop turned two."},
    {"word": "Impactful", "def": "有影響力的", "ex": "That home run was ___."},
    {"word": "Unstoppable", "def": "無法阻擋的", "ex": "He looked ___ at the plate."},
    {"word": "Disciplined", "def": "守紀律的", "ex": "A ___ hitter waits for his pitch."},
    {"word": "Cooperative", "def": "合作的", "ex": "The team is ___ and united."},
    {"word": "Tenacious", "def": "頑強的", "ex": "The runner was ___ on the bases."},
    {"word": "Meticulous", "def": "一絲不苟的", "ex": "He is ___ about his routine."},
    {"word": "Vigilant", "def": "警惕的", "ex": "Outfielders must stay ___."},
    {"word": "Prudent", "def": "謹慎的", "ex": "It was ___ to slow the game down."},
    {"word": "Vibrant", "def": "充滿生機的", "ex": "The stadium felt ___ tonight."},
    {"word": "Perceptive", "def": "敏銳的", "ex": "A ___ catcher reads hitters well."},
    {"word": "Immaculate", "def": "完美無瑕的", "ex": "He pitched an ___ inning."},
    {"word": "Luminous", "def": "明亮的", "ex": "The lights were ___ in the night sky."},
    {"word": "Eloquent", "def": "有說服力的", "ex": "He gave an ___ speech."},

    # --- 101-150: Verbs (50) ---
    {"word": "Sprint", "def": "衝刺", "ex": "You must ___ to beat the throw."},
    {"word": "Launch", "def": "大力擊出", "ex": "He ___ the ball into the stands."},
    {"word": "Celebrate", "def": "慶祝", "ex": "They ___ after the walk-off win."},
    {"word": "Achieve", "def": "達成", "ex": "He worked hard to ___ his goal."},
    {"word": "Defeat", "def": "擊敗", "ex": "They hope to ___ their rivals."},
    {"word": "Conquer", "def": "征服", "ex": "They want to ___ the league."},
    {"word": "Participate", "def": "參加", "ex": "Many players ___ in the tournament."},
    {"word": "Improve", "def": "進步", "ex": "Practice daily to ___ your swing."},
    {"word": "Demonstrate", "def": "展示", "ex": "The coach will ___ the bunt."},
    {"word": "Perform", "def": "表現", "ex": "Athletes must ___ under pressure."},
    {"word": "Injure", "def": "受傷", "ex": "Be careful not to ___ your arm."},
    {"word": "Recover", "def": "康復", "ex": "He will ___ after the surgery."},
    {"word": "Retire", "def": "退休", "ex": "The veteran decided to ___."},
    {"word": "Draft", "def": "選秀", "ex": "Teams ___ new players every year."},
    {"word": "Trade", "def": "交易", "ex": "The clubs agreed to ___ players."},
    {"word": "Encourage", "def": "鼓勵", "ex": "Fans ___ the team loudly."},
    {"word": "Inspire", "def": "啟發", "ex": "His story can ___ young athletes."},
    {"word": "Represent", "def": "代表", "ex": "He will ___ his country."},
    {"word": "Compete", "def": "競爭", "ex": "They ___ at a high level."},
    {"word": "Train", "def": "訓練", "ex": "They ___ every morning."},
    {"word": "Exceed", "def": "超過", "ex": "He hopes to ___ the record."},
    {"word": "Concentrate", "def": "專注", "ex": "You must ___ on the ball."},
    {"word": "Anticipate", "def": "預期", "ex": "Good fielders ___ the hop."},
    {"word": "Coordinate", "def": "協調", "ex": "Infielders must ___ on double plays."},
    {"word": "Sacrifice", "def": "犧牲", "ex": "He will ___ for the team."},
    {"word": "Transform", "def": "轉變", "ex": "A coach can ___ the culture."},
    {"word": "Strengthen", "def": "加強", "ex": "Weights ___ your core."},
    {"word": "Motivate", "def": "激勵", "ex": "The crowd can ___ players."},
    {"word": "Analyze", "def": "分析", "ex": "Coaches ___ video after games."},
    {"word": "Overcome", "def": "克服", "ex": "Champions ___ adversity."},
    {"word": "Persist", "def": "堅持", "ex": "You must ___ when it’s hard."},
    {"word": "Succeed", "def": "成功", "ex": "Work hard to ___."},
    {"word": "Prepare", "def": "準備", "ex": "Teams ___ for the postseason."},
    {"word": "Adjust", "def": "調整", "ex": "Hitters ___ to new pitchers."},
    {"word": "Execute", "def": "執行", "ex": "They ___ the plan perfectly."},
    {"word": "Dominate", "def": "主宰", "ex": "The ace continued to ___ hitters."},
    {"word": "Master", "def": "精通", "ex": "It takes time to ___ a changeup."},
    {"word": "Sustain", "def": "維持", "ex": "You must ___ focus all season."},
    {"word": "Vocalize", "def": "喊出", "ex": "Fielders must ___ 'Mine!'"}, 
    {"word": "Collaborate", "def": "協作", "ex": "Pitcher and catcher ___ every pitch."},
    {"word": "Accelerate", "def": "加速", "ex": "Runners ___ out of the box."},
    {"word": "Negotiate", "def": "談判", "ex": "Agents ___ contracts carefully."},
    {"word": "Observe", "def": "觀察", "ex": "Always ___ the pitcher’s move."},
    {"word": "Utilize", "def": "利用", "ex": "Teams ___ data to win games."},
    {"word": "Scrutinize", "def": "仔細檢查", "ex": "Officials ___ the bat for cracks."},
    {"word": "Mitigate", "def": "減輕", "ex": "Stretching helps ___ injury risk."},
    {"word": "Emulate", "def": "效法", "ex": "Kids ___ their favorite stars."},
    {"word": "Augment", "def": "加強", "ex": "He tried to ___ his arm strength."},

    # --- 151-200: Concepts / abstract nouns + extra baseball concepts (50) ---
    {"word": "Opportunity", "def": "機會", "ex": "Every at-bat is an ___."},
    {"word": "Strategy", "def": "策略", "ex": "The manager changed the ___."},
    {"word": "Technique", "def": "技巧", "ex": "Good ___ prevents injuries."},
    {"word": "Victory", "def": "勝利", "ex": "Nothing feels better than ___."},
    {"word": "Dedication", "def": "奉獻", "ex": "It takes ___ to practice daily."},
    {"word": "Obstacle", "def": "障礙", "ex": "Injuries are a major ___."},
    {"word": "Challenge", "def": "挑戰", "ex": "Facing the best team is a ___."},
    {"word": "Record", "def": "紀錄", "ex": "He broke the team ___."},
    {"word": "Highlight", "def": "亮點", "ex": "The catch was the ___ of the game."},
    {"word": "Career", "def": "職業生涯", "ex": "He had a long ___."},
    {"word": "Biography", "def": "傳記", "ex": "I read a ___ about a baseball star."},
    {"word": "Interview", "def": "採訪", "ex": "She gave an ___ after the win."},
    {"word": "Season", "def": "賽季", "ex": "The ___ starts in spring."},
    {"word": "Series", "def": "系列賽", "ex": "They won the playoff ___."},
    {"word": "Generation", "def": "世代", "ex": "He is the best of his ___."},
    {"word": "Nation", "def": "國家", "ex": "He played for his ___."},
    {"word": "Pressure", "def": "壓力", "ex": "There is huge ___ in the ninth inning."},
    {"word": "Success", "def": "成功", "ex": "His ___ came from hard work."},
    {"word": "Failure", "def": "失敗", "ex": "Learn from ___ and move on."},
    {"word": "Effort", "def": "努力", "ex": "Winning takes team ___."},
    {"word": "Endurance", "def": "耐力", "ex": "Pitchers need great ___."},
    {"word": "Potential", "def": "潛力", "ex": "The rookie has huge ___."},
    {"word": "Agility", "def": "敏捷", "ex": "Middle infielders need ___."},
    {"word": "Momentum", "def": "動力", "ex": "A homer gave them ___."},
    {"word": "Rivalry", "def": "競爭關係", "ex": "Their ___ is famous."},
    {"word": "Leadership", "def": "領導力", "ex": "The catcher showed ___."},
    {"word": "Integrity", "def": "誠信", "ex": "He played with ___."},
    {"word": "Loyalty", "def": "忠誠", "ex": "Fans showed ___ to the team."},
    {"word": "Ambition", "def": "雄心", "ex": "His ___ is to be MVP."},
    {"word": "Legacy", "def": "傳承", "ex": "He left a lasting ___."},
    {"word": "Adversity", "def": "逆境", "ex": "They overcame ___ to win."},
    {"word": "Foundation", "def": "基礎", "ex": "Basics are the ___ of greatness."},
    {"word": "Magnitude", "def": "量級", "ex": "The ___ of the moment was huge."},
    {"word": "Excellence", "def": "卓越", "ex": "They aim for ___ every day."},
    {"word": "Perspective", "def": "視角", "ex": "He gained a new ___ on hitting."},
    {"word": "Inspiration", "def": "靈感", "ex": "Her story is an ___ to kids."},
    {"word": "Preparation", "def": "準備", "ex": "Winning requires ___."},
    {"word": "Achievement", "def": "成就", "ex": "A title is a major ___."},
    {"word": "Motivation", "def": "動機", "ex": "His ___ is to improve."},
    {"word": "Commitment", "def": "承諾", "ex": "Baseball takes real ___."},
    # extra baseball concepts to reach 200
    {"word": "Clutch", "def": "關鍵時刻的表現", "ex": "He is known for his ___ hitting."},
    {"word": "Chemistry", "def": "默契", "ex": "Team ___ matters a lot."},
    {"word": "Discipline", "def": "自律", "ex": "Plate ___ leads to walks."},
    {"word": "Consistency", "def": "穩定性", "ex": "___ is the key to a great season."},
    {"word": "Adjustment", "def": "調整", "ex": "Mid-game ___ can change everything."},
    {"word": "Confidence", "def": "自信", "ex": "___ helps hitters stay calm."},
    {"word": "Focus", "def": "專注", "ex": "___ is required every pitch."},
    {"word": "Timing", "def": "時機／節奏", "ex": "Good ___ creates hard contact."},
    {"word": "Mechanics", "def": "動作機制", "ex": "Pitching ___ must be clean."},
    {"word": "Stamina", "def": "體力／續航", "ex": "A starter needs ___."},
]

# =========================
# Helpers: Progress merge + type safety
# =========================
def fresh_initial_state():
    data = copy.deepcopy(initial_word_data)
    for item in data:
        item.setdefault("score", 0)
        item.setdefault("last_correct_time", None)
        item.setdefault("misses", 0)
        item.setdefault("ex", "")

        # normalize types
        try:
            item["score"] = int(item["score"])
        except Exception:
            item["score"] = 0

        try:
            item["misses"] = int(item["misses"])
        except Exception:
            item["misses"] = 0

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
    Merge uploaded progress into canonical list by 'word'.
    Keeps def/ex from initial list, merges score/last_correct_time/misses.
    """
    base = fresh_initial_state()
    if not isinstance(loaded, list):
        return base

    idx = {w.get("word"): w for w in loaded if isinstance(w, dict) and w.get("word")}
    for item in base:
        src = idx.get(item["word"])
        if not src:
            continue

        if "score" in src:
            try:
                item["score"] = int(src.get("score", item["score"]))
            except Exception:
                pass

        if "misses" in src:
            try:
                item["misses"] = int(src.get("misses", item["misses"]))
            except Exception:
                pass

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


# =========================
# Session State
# =========================
DEFAULTS = {
    "current_index": 0,
    "game_score": 0,
    "game_active": False,  # False | True | "WON"
    "current_question": None,
    "options": [],
    "feedback": "",
    "word_audio": None,
    "sentence_audio": None,
    "session_words": [],
    "show_results": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = copy.deepcopy(v)

if "vocab_data" not in st.session_state:
    st.session_state.vocab_data = fresh_initial_state()

# =========================
# Audio (cached)
# =========================
@st.cache_data(show_spinner=False)
def tts_mp3_bytes(txt: str) -> bytes:
    try:
        tts = gTTS(text=txt, lang="en")
        f = io.BytesIO()
        tts.write_to_fp(f)
        return f.getvalue()
    except Exception:
        return b""

def get_audio_stream(txt: str):
    b = tts_mp3_bytes(txt)
    return io.BytesIO(b) if b else None
import re  # 若你前面還沒 import

def sentence_for_tts(ex: str, word: str) -> str:
    ex = (ex or "").strip()
    word = (word or "").strip()
    if not ex:
        return word

    # 把 ___ 換成真正的單字，避免 TTS 念 underscore
    if "___" in ex:
        ex = ex.replace("___", word)

    # 保險：移除任何殘留底線
    ex = re.sub(r"_+", " ", ex)

    return ex


# =========================
# Sentence highlight (28px)
# =========================
def render_sentence_box(word: str, sentence: str):
    if not sentence:
        sentence = ""

    # Prefer blank replacement (best for accuracy, including multi-word phrases)
    if "___" in sentence:
        shown = sentence.replace(
            "___",
            f"<span style='color:#e63946; font-weight:900; text-decoration:underline; text-underline-offset:4px;'>{word}</span>",
        )
    else:
        # Fallback: regex highlight occurrences (case-insensitive)
        escaped = re.escape(word.strip())
        if " " in word.strip():
            pattern = re.compile(escaped, re.IGNORECASE)
        else:
            pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)

        def repl(m):
            return (
                "<span style='color:#e63946; font-weight:900; text-decoration:underline; text-underline-offset:4px;'>"
                f"{m.group(0)}</span>"
            )

        shown = pattern.sub(repl, sentence)

    st.markdown(
        f"""
        <div style="
            font-size: 28px;
            line-height: 1.5;
            padding: 20px;
            background: #f0f2f6;
            border-radius: 10px;
            border-left: 6px solid #1f77b4;
            margin-top: 8px;
            margin-bottom: 14px;
        ">
            💡 {shown}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Game Logic
# =========================
def start_game():
    cands = [w for w in st.session_state.vocab_data if w["score"] < MASTERY_THRESHOLD]
    if not cands:
        st.session_state.game_active = "WON"
        st.session_state.show_results = False
        return

    st.session_state.session_words = random.sample(cands, min(ROUNDS_PER_GAME, len(cands)))
    st.session_state.current_index = 0
    st.session_state.game_score = 0
    st.session_state.game_active = True
    st.session_state.show_results = False
    st.session_state.feedback = ""
    next_q()

def next_q():
    if st.session_state.current_index < len(st.session_state.session_words):
        t = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question = t
        st.session_state.word_audio = get_audio_stream(t["word"])
        st.session_state.sentence_audio = get_audio_stream(
    sentence_for_tts(t.get("ex", ""), t.get("word", ""))
)


        pool = [w["def"] for w in st.session_state.vocab_data if w["def"] != t["def"]]
        pool = list(dict.fromkeys(pool))  # de-dup

        k = min(3, len(pool))
        opts = [t["def"]] + (random.sample(pool, k) if k > 0 else [])
        random.shuffle(opts)
        st.session_state.options = opts
    else:
        st.session_state.game_active = False
        st.session_state.show_results = True
        st.session_state.current_question = None
        st.session_state.options = []
        st.session_state.word_audio = None
        st.session_state.sentence_audio = None

def check(ans: str):
    t, now = st.session_state.current_question, time.time()
    if not t:
        return

    if ans == t["def"]:
        st.session_state.game_score += 1

        for i in st.session_state.vocab_data:
            if i["word"] == t["word"]:
                last = i.get("last_correct_time")

                # ✅ 24h cooldown logic (your requirement)
                if last is None or (now - last > COOLDOWN_SECONDS):
                    i["score"] += 1
                    i["last_correct_time"] = now
                    st.session_state.feedback = f"✅ Correct! (+1 Mastery Point)  {t['word']} = {t['def']}"
                else:
                    remaining = max(0, COOLDOWN_SECONDS - (now - last))
                    h = int(remaining // 3600)
                    m = int((remaining % 3600) // 60)
                    st.session_state.feedback = f"✅ Correct! (Next mastery point in {h}h {m}m)  {t['word']} = {t['def']}"

                break
    else:
        st.session_state.feedback = f"❌ Wrong. {t['word']} = {t['def']} (-1 Mastery)"
        for i in st.session_state.vocab_data:
            if i["word"] == t["word"]:
                i["score"] = max(0, i["score"] - 1)
                i["misses"] = int(i.get("misses", 0)) + 1
                break

    st.session_state.current_index += 1
    next_q()

# =========================
# UI
# =========================
st.set_page_config(page_title="Baseball Superstars Trainer", page_icon="⚾")
st.title("⚾ Pro English & Baseball Trainer (200 Words)")

# --- Sidebar ---
st.sidebar.header("📋 Manager's Office")

up = st.sidebar.file_uploader("Upload Progress (.json)", type="json")
if up:
    try:
        loaded = json.load(up)
        st.session_state.vocab_data = merge_progress(loaded)
        st.sidebar.success("Loaded!")
    except Exception:
        st.sidebar.error("Invalid file.")

mastered = sum(1 for w in st.session_state.vocab_data if w["score"] >= MASTERY_THRESHOLD)
st.sidebar.metric("Roster Mastered", f"{mastered} / {len(st.session_state.vocab_data)}")

with st.sidebar.expander("🔍 Scouting Report", expanded=False):
    df = pd.DataFrame(st.session_state.vocab_data)

    # Slumping: most misses
    if not df.empty and "misses" in df.columns:
        slump = df[df["misses"] > 0].sort_values("misses", ascending=False).head(5)
        if not slump.empty:
            st.subheader("📉 Slumping Words")
            for _, row in slump.iterrows():
                st.write(f"**{row['word']}**: {int(row['misses'])} errors")

    # Rising: close to mastery
    if not df.empty and "score" in df.columns:
        rising = df[(df["score"] > 0) & (df["score"] < MASTERY_THRESHOLD)].sort_values("score", ascending=False).head(5)
        if not rising.empty:
            st.subheader("⭐ Rising Stars")
            for _, row in rising.iterrows():
                st.write(f"**{row['word']}**: Level {int(row['score'])}")

st.sidebar.download_button(
    "💾 Save Progress",
    data=json.dumps(st.session_state.vocab_data, indent=4, ensure_ascii=False),
    file_name="progress.json",
)

# --- Main screens ---
if st.session_state.game_active == "WON":
    st.balloons()
    st.success("🏆 MVP! All words mastered!")
    if st.button("Restart Season"):
        st.session_state.vocab_data = fresh_initial_state()
        for k, v in DEFAULTS.items():
            st.session_state[k] = copy.deepcopy(v)
        st.rerun()

elif st.session_state.show_results:
    st.header("📊 Post-Game Analysis")
    score = st.session_state.game_score
    total = len(st.session_state.session_words)
    st.metric("Final Score", f"{score} / {total}")

    if st.button("Back to Clubhouse"):
        st.session_state.show_results = False
        st.rerun()

elif not st.session_state.game_active:
    st.header("Welcome to the Stadium")
    st.caption("Rule: Correct answers may only grant +1 mastery point once every 24 hours per word.")
    if st.button("▶️ Play Ball (20 Rounds)", use_container_width=True):
        start_game()
        st.rerun()

    # Optional overview table (only show if some progress exists)
    df = pd.DataFrame(st.session_state.vocab_data)
    if not df.empty and df["score"].sum() > 0:
        st.subheader("Current Training Stats (Top 15)")
        st.table(
            df[df["score"] > 0]
            .sort_values(["score", "misses"], ascending=[False, False])
            .head(15)[["word", "def", "score", "misses"]]
        )

else:
    q = st.session_state.current_question
    total = max(1, len(st.session_state.session_words))
    st.progress(st.session_state.current_index / total)

    st.markdown(f"## Word: **{q['word']}**")

    c1, c2 = st.columns(2)
    with c1:
        st.write("🔊 **Word**")
        if st.session_state.word_audio:
            st.audio(st.session_state.word_audio)
    with c2:
        st.write("📖 **Sentence**")
        if st.session_state.sentence_audio:
            st.audio(st.session_state.sentence_audio)

    # 28px sentence + highlighted correct word
    render_sentence_box(q["word"], q.get("ex", ""))

    # Options
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.options):
        if cols[i % 2].button(opt, use_container_width=True, key=f"q_{st.session_state.current_index}_{i}"):
            check(opt)
            st.rerun()

    if st.session_state.feedback:
        if "✅" in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
