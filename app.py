
import streamlit as st
import random
import json
import time
from gtts import gTTS
import io

# --- CONFIGURATION ---
ROUNDS_PER_GAME = 20
MASTERY_THRESHOLD = 5
COOLDOWN_SECONDS = 86400  # 24 Hours in seconds

# --- THE VOCABULARY LIST ---
initial_word_data = [
    {"word": "Pitcher", "def": "投手"},
    {"word": "Catcher", "def": "捕手"},
    {"word": "Umpire", "def": "裁判"},
    {"word": "Inning", "def": "局 (棒球比賽的)"},
    {"word": "Dugout", "def": "球員休息區"},
    {"word": "Bullpen", "def": "牛棚 (投手練投區)"},
    {"word": "Roster", "def": "球員名單"},
    {"word": "Statistic", "def": "統計數據"},
    {"word": "League", "def": "聯盟"},
    {"word": "Tournament", "def": "錦標賽"},
    {"word": "Championship", "def": "冠軍賽"},
    {"word": "Trophy", "def": "獎盃"},
    {"word": "MVP", "def": "最有價值球員"},
    {"word": "Rookie", "def": "新秀 / 菜鳥"},
    {"word": "Veteran", "def": "老將 / 資深球員"},
    {"word": "Manager", "def": "總教練 / 經理"},
    {"word": "Stadium", "def": "體育場"},
    {"word": "Grand Slam", "def": "滿貫全壘打"},
    {"word": "Strikeout", "def": "三振出局"},
    {"word": "Walk", "def": "保送"},
    {"word": "Infielder", "def": "內野手"},
    {"word": "Outfielder", "def": "外野手"},
    {"word": "Mound", "def": "投手丘"},
    {"word": "Batter", "def": "打擊者"},
    {"word": "Helmet", "def": "頭盔"},
    {"word": "Jersey", "def": "球衣"},
    {"word": "Mascot", "def": "吉祥物"},
    {"word": "Scoreboard", "def": "計分板"},
    {"word": "Spectator", "def": "觀眾"},
    {"word": "Base", "def": "壘包"},
    {"word": "Phenomenal", "def": "非凡的 / 驚人的"},
    {"word": "Legendary", "def": "傳奇的"},
    {"word": "Dominant", "def": "佔優勢的 / 主導的"},
    {"word": "Versatile", "def": "多才多藝的 / 全能的"},
    {"word": "Aggressive", "def": "積極的 / 侵略性的"},
    {"word": "Defensive", "def": "防守的"},
    {"word": "Offensive", "def": "進攻的"},
    {"word": "Spectacular", "def": "壯觀的 / 精彩的"},
    {"word": "Consistent", "def": "始終如一的 / 穩定的"},
    {"word": "Athletic", "def": "運動的 / 體格健壯的"},
    {"word": "Talented", "def": "有天賦的"},
    {"word": "Famous", "def": "著名的"},
    {"word": "Professional", "def": "專業的 / 職業的"},
    {"word": "Competitive", "def": "競爭激烈的 / 好勝的"},
    {"word": "Accurate", "def": "準確的"},
    {"word": "Powerful", "def": "強大的 / 有力的"},
    {"word": "Incredible", "def": "難以置信的"},
    {"word": "Historic", "def": "歷史性的"},
    {"word": "Memorable", "def": "難忘的"},
    {"word": "Intense", "def": "強烈的 / 激烈的"},
    {"word": "Reliable", "def": "可靠的"},
    {"word": "Remarkable", "def": "卓越的 / 值得注意的"},
    {"word": "Outstanding", "def": "傑出的"},
    {"word": "Determined", "def": "堅決的"},
    {"word": "Confident", "def": "有自信的"},
    {"word": "Ambitious", "def": "有野心的"},
    {"word": "Energetic", "def": "精力充沛的"},
    {"word": "Focus", "def": "專注"},
    {"word": "Precise", "def": "精確的"},
    {"word": "Rapid", "def": "迅速的"},
    {"word": "Sprint", "def": "衝刺"},
    {"word": "Launch", "def": "發射 / 大力擊出"},
    {"word": "Celebrate", "def": "慶祝"},
    {"word": "Achieve", "def": "達成 / 實現"},
    {"word": "Defeat", "def": "擊敗"},
    {"word": "Conquer", "def": "征服 / 克服"},
    {"word": "Participate", "def": "參加"},
    {"word": "Improve", "def": "改善 / 進步"},
    {"word": "Demonstrate", "def": "示範 / 展示"},
    {"word": "Perform", "def": "表演 / 表現"},
    {"word": "Injure", "def": "受傷"},
    {"word": "Recover", "def": "恢復 / 康復"},
    {"word": "Retire", "def": "退休"},
    {"word": "Draft", "def": "徵召 / 選秀"},
    {"word": "Trade", "def": "交易"},
    {"word": "Encourage", "def": "鼓勵"},
    {"word": "Inspire", "def": "啟發 / 激勵"},
    {"word": "Represent", "def": "代表"},
    {"word": "Compete", "def": "競爭"},
    {"word": "Train", "def": "訓練"},
    {"word": "Opportunity", "def": "機會"},
    {"word": "Strategy", "def": "策略"},
    {"word": "Technique", "def": "技巧 / 技術"},
    {"word": "Victory", "def": "勝利"},
    {"word": "Dedication", "def": "奉獻 / 專注"},
    {"word": "Obstacle", "def": "障礙"},
    {"word": "Challenge", "def": "挑戰"},
    {"word": "Record", "def": "紀錄"},
    {"word": "Highlight", "def": "精彩片段 / 亮點"},
    {"word": "Career", "def": "職業生涯"},
    {"word": "Biography", "def": "傳記"},
    {"word": "Interview", "def": "採訪 / 面試"},
    {"word": "Season", "def": "賽季 / 季節"},
    {"word": "Series", "def": "系列賽"},
    {"word": "Generation", "def": "世代"},
    {"word": "Nation", "def": "國家"},
    {"word": "Pressure", "def": "壓力"},
    {"word": "Success", "def": "成功"},
    {"word": "Failure", "def": "失敗"},
    {"word": "Effort", "def": "努力"}
]

# --- INITIALIZE SESSION STATE ---
if 'vocab_data' not in st.session_state:
    # Initialize default data with 'score' and 'last_correct_time'
    for item in initial_word_data:
        item['score'] = 0
        item['last_correct_time'] = None 
    st.session_state.vocab_data = initial_word_data
else:
    # Ensure old save files get the new field if missing
    for item in st.session_state.vocab_data:
        if 'last_correct_time' not in item:
            item['last_correct_time'] = None

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'options' not in st.session_state:
    st.session_state.options = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None

# --- FUNCTIONS ---

def generate_audio(text):
    """Generates audio bytes for the given text using gTTS."""
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

def start_new_game():
    candidates = [w for w in st.session_state.vocab_data if w['score'] < MASTERY_THRESHOLD]
    
    if len(candidates) == 0:
        st.session_state.game_active = "WON"
        return

    num_rounds = min(ROUNDS_PER_GAME, len(candidates))
    st.session_state.session_words = random.sample(candidates, num_rounds)
    st.session_state.current_index = 0
    st.session_state.game_score = 0
    st.session_state.game_active = True
    st.session_state.feedback = ""
    load_next_question()

def load_next_question():
    if st.session_state.current_index < len(st.session_state.session_words):
        target = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question = target
        
        # Generate Audio for this word
        st.session_state.current_audio = generate_audio(target['word'])
        
        # Generate options
        correct_def = target['def']
        all_defs = [item['def'] for item in st.session_state.vocab_data if item['def'] != correct_def]
        wrong_defs = random.sample(all_defs, 3)
        options = wrong_defs + [correct_def]
        random.shuffle(options)
        st.session_state.options = options
    else:
        st.session_state.game_active = False

def check_answer(selected_option):
    target = st.session_state.current_question
    correct_def = target['def']
    
    if selected_option == correct_def:
        st.session_state.game_score += 1
        current_time = time.time()
        
        # Find item in main list to update
        for item in st.session_state.vocab_data:
            if item['word'] == target['word']:
                last_time = item.get('last_correct_time')
                
                # Check if 24 hours (86400 seconds) have passed OR if it's the first time
                if last_time is None or (current_time - last_time > COOLDOWN_SECONDS):
                    item['score'] += 1
                    item['last_correct_time'] = current_time
                    st.session_state.feedback = f"✅ Correct! (+1 Mastery Point)"
                else:
                    # Calculate hours left until next point
                    hours_left = int((COOLDOWN_SECONDS - (current_time - last_time)) / 3600)
                    st.session_state.feedback = f"✅ Correct! (Good practice! Come back in {hours_left}h to gain a Mastery Point)"
                
                if item['score'] >= MASTERY_THRESHOLD:
                     st.session_state.feedback += f" (🌟 MASTERED!)"
                break
    else:
        # Wrong Answer Logic
        st.session_state.feedback = f"❌ Wrong. '{target['word']}' means '{correct_def}' (-1 Mastery Point)"
        for item in st.session_state.vocab_data:
            if item['word'] == target['word']:
                # Minus 1, but don't go below 0
                item['score'] = max(0, item['score'] - 1)
                break
    
    st.session_state.current_index += 1
    load_next_question()

# --- APP LAYOUT ---

st.title("⚾ Baseball Superstars Vocab")

# SIDEBAR: Progress Management
st.sidebar.header("Save Your Progress")
uploaded_file = st.sidebar.file_uploader("Upload previous progress (.json)", type="json")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        # Fix for old save files that might miss 'last_correct_time'
        for item in data:
            if 'last_correct_time' not in item:
                item['last_correct_time'] = None
        st.session_state.vocab_data = data
        st.sidebar.success("Progress Loaded!")
    except:
        st.sidebar.error("Error loading file.")

mastered_count = sum(1 for w in st.session_state.vocab_data if w['score'] >= MASTERY_THRESHOLD)
total_count = len(st.session_state.vocab_data)
st.sidebar.metric("Words Mastered", f"{mastered_count} / {total_count}")

json_string = json.dumps(st.session_state.vocab_data, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="💾 Download Progress to Save",
    data=json_string,
    file_name="baseball_vocab_progress.json",
    mime="application/json"
)

# --- MAIN GAME AREA ---

if st.session_state.game_active == "WON":
    st.balloons()
    st.success("🎉 You have mastered EVERY word in the book! Amazing job!")

elif not st.session_state.game_active:
    st.header("Welcome!")
    st.write(f"Goal: Answer 20 questions. \n\n**Rules:** \n1. Get a word right to gain a point.\n2. You can only gain 1 point per word every 24 hours (Spaced Repetition!).\n3. Wrong answers remove a point.")
    if st.session_state.game_score > 0:
        st.info(f"Last Game Score: {st.session_state.game_score} / {ROUNDS_PER_GAME}")
    
    if st.button("▶️ Start New Game"):
        start_new_game()
        st.rerun()

else:
    # Game is running
    progress = st.session_state.current_index / len(st.session_state.session_words)
    st.progress(progress)
    st.caption(f"Question {st.session_state.current_index + 1} of {len(st.session_state.session_words)}")
    
    st.metric("Score", st.session_state.game_score)

    # Word and Audio Section
    st.markdown(f"### Word: **{st.session_state.current_question['word']}**")
    
    if st.session_state.current_audio:
        st.audio(st.session_state.current_audio, format="audio/mp3")
    else:
        st.warning("Audio not available")

    st.write("What is the Chinese definition?")

    # Buttons
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.options):
        if cols[i % 2].button(opt, use_container_width=True):
            check_answer(opt)
            st.rerun()

    if st.session_state.feedback:
        if "Correct" in st.session_state.feedback:
            st.success(st.session_state.feedback)
        else:
            st.error(st.session_state.feedback)
    
