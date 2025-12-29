import streamlit as st
import random
import json
import time
from gtts import gTTS
import io

# --- CONFIGURATION ---
ROUNDS_PER_GAME = 20
MASTERY_THRESHOLD = 5
COOLDOWN_SECONDS = 86400  # 24 Hours

# --- THE 150 VOCABULARY LIST ---
initial_word_data = [
    # Baseball Terms
    {"word": "Pitcher", "def": "投手"}, {"word": "Catcher", "def": "捕手"},
    {"word": "Umpire", "def": "裁判"}, {"word": "Inning", "def": "局 (比賽的)"},
    {"word": "Dugout", "def": "球員休息區"}, {"word": "Bullpen", "def": "牛棚"},
    {"word": "Roster", "def": "球員名單"}, {"word": "Statistic", "def": "統計數據"},
    {"word": "League", "def": "聯盟"}, {"word": "Tournament", "def": "錦標賽"},
    {"word": "Championship", "def": "冠軍賽"}, {"word": "Trophy", "def": "獎盃"},
    {"word": "MVP", "def": "最有價值球員"}, {"word": "Rookie", "def": "新秀"},
    {"word": "Veteran", "def": "老將"}, {"word": "Manager", "def": "總教練"},
    {"word": "Stadium", "def": "體育場"}, {"word": "Grand Slam", "def": "滿貫全壘打"},
    {"word": "Strikeout", "def": "三振出局"}, {"word": "Walk", "def": "保送"},
    {"word": "Infielder", "def": "內野手"}, {"word": "Outfielder", "def": "外野手"},
    {"word": "Mound", "def": "投手丘"}, {"word": "Batter", "def": "打擊者"},
    {"word": "Helmet", "def": "頭盔"}, {"word": "Jersey", "def": "球衣"},
    {"word": "Mascot", "def": "吉祥物"}, {"word": "Scoreboard", "def": "計分板"},
    {"word": "Spectator", "def": "觀眾"}, {"word": "Diamond", "def": "棒球場內野"},
    # Advanced Adjectives
    {"word": "Phenomenal", "def": "非凡的"}, {"word": "Legendary", "def": "傳奇的"},
    {"word": "Dominant", "def": "佔優勢的"}, {"word": "Versatile", "def": "全能的"},
    {"word": "Aggressive", "def": "積極的"}, {"word": "Defensive", "def": "防守的"},
    {"word": "Offensive", "def": "進攻的"}, {"word": "Spectacular", "def": "精彩的"},
    {"word": "Consistent", "def": "穩定的"}, {"word": "Athletic", "def": "體格健壯的"},
    {"word": "Talented", "def": "有天賦的"}, {"word": "Professional", "def": "專業的"},
    {"word": "Competitive", "def": "好勝的"}, {"word": "Accurate", "def": "準確的"},
    {"word": "Powerful", "def": "有力的"}, {"word": "Incredible", "def": "難以置信的"},
    {"word": "Historic", "def": "歷史性的"}, {"word": "Memorable", "def": "難忘的"},
    {"word": "Intense", "def": "激烈的"}, {"word": "Reliable", "def": "可靠的"},
    {"word": "Remarkable", "def": "卓越的"}, {"word": "Outstanding", "def": "傑出的"},
    {"word": "Determined", "def": "堅決的"}, {"word": "Confident", "def": "有自信的"},
    {"word": "Ambitious", "def": "有野心的"}, {"word": "Energetic", "def": "精力充沛的"},
    {"word": "Precise", "def": "精確的"}, {"word": "Rapid", "def": "迅速的"},
    {"word": "Resilient", "def": "有韌性的"}, {"word": "Strategic", "def": "策略性的"},
    {"word": "Dynamic", "def": "充滿活力的"}, {"word": "Exceptional", "def": "優越的"},
    {"word": "Fearless", "def": "大膽的"}, {"word": "Elite", "def": "精英的"},
    {"word": "Formidable", "def": "強大的"}, {"word": "Skillful", "def": "熟練的"},
    {"word": "Impactful", "def": "有影響力的"}, {"word": "Unstoppable", "def": "無法阻擋的"},
    {"word": "Disciplined", "def": "守紀律的"}, {"word": "Cooperative", "def": "合作的"},
    # Verbs
    {"word": "Sprint", "def": "衝刺"}, {"word": "Launch", "def": "大力擊出"},
    {"word": "Celebrate", "def": "慶祝"}, {"word": "Achieve", "def": "達成"},
    {"word": "Defeat", "def": "擊敗"}, {"word": "Conquer", "def": "征服"},
    {"word": "Participate", "def": "參加"}, {"word": "Improve", "def": "進步"},
    {"word": "Demonstrate", "def": "展示"}, {"word": "Perform", "def": "表現"},
    {"word": "Injure", "def": "受傷"}, {"word": "Recover", "def": "康復"},
    {"word": "Retire", "def": "退休"}, {"word": "Draft", "def": "選秀"},
    {"word": "Trade", "def": "交易"}, {"word": "Encourage", "def": "鼓勵"},
    {"word": "Inspire", "def": "啟發"}, {"word": "Represent", "def": "代表"},
    {"word": "Compete", "def": "競爭"}, {"word": "Train", "def": "訓練"},
    {"word": "Exceed", "def": "超過"}, {"word": "Concentrate", "def": "專注"},
    {"word": "Anticipate", "def": "預期"}, {"word": "Coordinate", "def": "協調"},
    {"word": "Sacrifice", "def": "犧牲"}, {"word": "Transform", "def": "轉變"},
    {"word": "Strengthen", "def": "加強"}, {"word": "Motivate", "def": "激勵"},
    {"word": "Analyze", "def": "分析"}, {"word": "Overcome", "def": "克服"},
    {"word": "Persist", "def": "堅持"}, {"word": "Succeed", "def": "成功"},
    {"word": "Prepare", "def": "準備"}, {"word": "Adjust", "def": "調整"},
    {"word": "Execute", "def": "執行"}, {"word": "Dominate", "def": "主宰"},
    {"word": "Master", "def": "精通"}, {"word": "Sustain", "def": "維持"},
    {"word": "Vocalize", "def": "喊出"}, {"word": "Collaborate", "def": "協作"},
    # Concepts
    {"word": "Opportunity", "def": "機會"}, {"word": "Strategy", "def": "策略"},
    {"word": "Technique", "def": "技巧"}, {"word": "Victory", "def": "勝利"},
    {"word": "Dedication", "def": "奉獻"}, {"word": "Obstacle", "def": "障礙"},
    {"word": "Challenge", "def": "挑戰"}, {"word": "Record", "def": "紀錄"},
    {"word": "Highlight", "def": "亮點"}, {"word": "Career", "def": "職業生涯"},
    {"word": "Biography", "def": "傳記"}, {"word": "Interview", "def": "採訪"},
    {"word": "Season", "def": "賽季"}, {"word": "Series", "def": "系列賽"},
    {"word": "Generation", "def": "世代"}, {"word": "Nation", "def": "國家"},
    {"word": "Pressure", "def": "壓力"}, {"word": "Success", "def": "成功"},
    {"word": "Failure", "def": "失敗"}, {"word": "Effort", "def": "努力"},
    {"word": "Endurance", "def": "耐力"}, {"word": "Potential", "def": "潛力"},
    {"word": "Agility", "def": "敏捷"}, {"word": "Momentum", "def": "動力"},
    {"word": "Rivalry", "def": "競爭關係"}, {"word": "Leadership", "def": "領導力"},
    {"word": "Integrity", "def": "誠信"}, {"word": "Loyalty", "def": "忠誠"},
    {"word": "Ambition", "def": "雄心"}, {"word": "Legacy", "def": "傳承"},
    {"word": "Adversity", "def": "逆境"}, {"word": "Foundation", "def": "基礎"},
    {"word": "Magnitude", "def": "量級"}, {"word": "Excellence", "def": "卓越"},
    {"word": "Perspective", "def": "視角"}, {"word": "Inspiration", "def": "靈感"},
    {"word": "Preparation", "def": "準備"}, {"word": "Achievement", "def": "成就"},
    {"word": "Motivation", "def": "動機"}, {"word": "Commitment", "def": "承諾"}
]

# --- SESSION INITIALIZATION ---
if 'vocab_data' not in st.session_state:
    for item in initial_word_data:
        item['score'] = 0
        item['last_correct_time'] = None
    st.session_state.vocab_data = initial_word_data

keys = ['current_index', 'game_score', 'game_active', 'current_question', 'options', 'feedback', 'current_audio']
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None if 'audio' in k or 'question' in k else (False if 'active' in k else ("" if 'feedback' in k else ([] if 'options' in k else 0)))

# --- LOGIC ---
def get_audio(txt):
    try:
        tts = gTTS(text=txt, lang='en')
        f = io.BytesIO()
        tts.write_to_fp(f)
        f.seek(0)
        return f
    except: return None

def start_game():
    cands = [w for w in st.session_state.vocab_data if w['score'] < MASTERY_THRESHOLD]
    if not cands: st.session_state.game_active = "WON"; return
    st.session_state.session_words = random.sample(cands, min(ROUNDS_PER_GAME, len(cands)))
    st.session_state.current_index, st.session_state.game_score, st.session_state.game_active, st.session_state.feedback = 0, 0, True, ""
    next_q()

def next_q():
    if st.session_state.current_index < len(st.session_state.session_words):
        t = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question, st.session_state.current_audio = t, get_audio(t['word'])
        opts = [t['def']] + random.sample([w['def'] for w in st.session_state.vocab_data if w['def'] != t['def']], 3)
        random.shuffle(opts)
        st.session_state.options = opts
    else: st.session_state.game_active = False

def check(ans):
    t, now = st.session_state.current_question, time.time()
    if ans == t['def']:
        st.session_state.game_score += 1
        for i in st.session_state.vocab_data:
            if i['word'] == t['word']:
                last = i.get('last_correct_time')
                if last is None or (now - last > COOLDOWN_SECONDS):
                    i['score'], i['last_correct_time'] = i['score'] + 1, now
                    st.session_state.feedback = "✅ Correct! (+1 Mastery Point)"
                else:
                    h = int((COOLDOWN_SECONDS - (now - last)) / 3600)
                    st.session_state.feedback = f"✅ Correct! (Practice again in {h}h for a point)"
                break
    else:
        st.session_state.feedback = f"❌ Wrong. '{t['word']}' = '{t['def']}' (-1 Point)"
        for i in st.session_state.vocab_data:
            if i['word'] == t['word']: i['score'] = max(0, i['score'] - 1); break
    st.session_state.current_index += 1
    next_q()

# --- UI ---
st.set_page_config(page_title="Baseball Vocab", page_icon="⚾")
st.title("⚾ 150 Baseball Superstars Vocab")

st.sidebar.header("Progress Manager")
up = st.sidebar.file_uploader("Upload Progress (.json)", type="json")
if up:
    st.session_state.vocab_data = json.load(up)
    st.sidebar.success("Loaded!")

mastered = sum(1 for w in st.session_state.vocab_data if w['score'] >= MASTERY_THRESHOLD)
st.sidebar.metric("Mastered", f"{mastered} / 150")
st.sidebar.download_button("💾 Save Progress", json.dumps(st.session_state.vocab_data, indent=4), "progress.json")

if st.session_state.game_active == "WON":
    st.balloons(); st.success("🏆 MVP! You've mastered the book!")
    if st.button("Restart All"): st.session_state.vocab_data = initial_word_data; st.rerun()
elif not st.session_state.game_active:
    st.header("Ready to Practice?")
    if st.button("▶️ Start Game"): start_game(); st.rerun()
else:
    st.progress(st.session_state.current_index / len(st.session_state.session_words))
    st.metric("Session Score", st.session_state.game_score)
    st.markdown(f"### Word: **{st.session_state.current_question['word']}**")
    if st.session_state.current_audio: st.audio(st.session_state.current_audio)
    
    cols = st.columns(2)
    for i, o in enumerate(st.session_state.options):
        if cols[i%2].button(o, use_container_width=True): check(o); st.rerun()
    
    if st.session_state.feedback:
        if "Correct" in st.session_state.feedback: st.success(st.session_state.feedback)
        else: st.error(st.session_state.feedback)
