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

# --- THE 200 VOCABULARY LIST ---
initial_word_data = [
    # Baseball Positions & People (1-30)
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
    
    # Advanced Adjectives (31-90)
    {"word": "Phenomenal", "def": "非凡的", "ex": "His ability to hit the ball is simply ___."},
    {"word": "Legendary", "def": "傳奇的", "ex": "Babe Ruth is a ___ figure in baseball history."},
    {"word": "Dominant", "def": "佔優勢的", "ex": "The pitcher was ___ and didn't allow any hits."},
    {"word": "Versatile", "def": "全能的", "ex": "He is a ___ player who can play any position."},
    {"word": "Aggressive", "def": "積極的", "ex": "The runner made an ___ slide into second base."},
    {"word": "Defensive", "def": "防守的", "ex": "He made an incredible ___ play to save the game."},
    {"word": "Offensive", "def": "進攻的", "ex": "The team has a very strong ___ lineup this year."},
    {"word": "Spectacular", "def": "精彩的", "ex": "The center fielder made a ___ diving catch."},
    {"word": "Consistent", "def": "穩定的", "ex": "She is a ___ hitter who gets a hit in every game."},
    {"word": "Athletic", "def": "體格健壯的", "ex": "Shortstops must be very ___ to reach fast grounders."},
    {"word": "Talented", "def": "有天賦的", "ex": "The scout noticed the ___ player at the high school game."},
    {"word": "Professional", "def": "專業的", "ex": "He signed a ___ contract with the Yankees."},
    {"word": "Competitive", "def": "好勝的", "ex": "The two teams are very ___ and always play close games."},
    {"word": "Accurate", "def": "準確的", "ex": "The catcher made an ___ throw to catch the runner."},
    {"word": "Powerful", "def": "有力的", "ex": "He used a ___ swing to drive the ball over the fence."},
    {"word": "Incredible", "def": "難以置信的", "ex": "It was ___ that he caught that ball!"},
    {"word": "Historic", "def": "歷史性的", "ex": "Winning the World Series was a ___ moment for the city."},
    {"word": "Memorable", "def": "難忘的", "ex": "The walk-off home run was a ___ end to the season."},
    {"word": "Intense", "def": "激烈的", "ex": "The rivalry between the two teams is very ___."},
    {"word": "Reliable", "def": "可靠的", "ex": "He is the most ___ relief pitcher on the team."},
    {"word": "Remarkable", "def": "卓越的", "ex": "His speed on the bases is truly ___."},
    {"word": "Outstanding", "def": "傑出的", "ex": "The pitcher gave an ___ performance tonight."},
    {"word": "Determined", "def": "堅決的", "ex": "He was ___ to win the game for his teammates."},
    {"word": "Confident", "def": "有自信的", "ex": "The batter looked ___ as he walked to the plate."},
    {"word": "Ambitious", "def": "有野心的", "ex": "The ___ player wants to break the home run record."},
    {"word": "Energetic", "def": "精力充沛的", "ex": "The fans were ___ and cheered loudly all night."},
    {"word": "Precise", "def": "精確的", "ex": "The pitcher has ___ control of his curveball."},
    {"word": "Rapid", "def": "迅速的", "ex": "He has a ___ delivery that surprises many hitters."},
    {"word": "Resilient", "def": "有韌性的", "ex": "The team was ___ and came back from a 5-run lead."},
    {"word": "Strategic", "def": "策略性的", "ex": "The manager made a ___ decision to bunt the ball."},
    {"word": "Dynamic", "def": "充滿活力的", "ex": "The duo at shortstop and second base is very ___."},
    {"word": "Exceptional", "def": "優越的", "ex": "His hand-eye coordination is ___."},
    {"word": "Fearless", "def": "大膽的", "ex": "The ___ catcher blocked the plate against the runner."},
    {"word": "Elite", "def": "精英的", "ex": "Only an ___ group of players make the All-Star team."},
    {"word": "Formidable", "def": "強大的", "ex": "Their pitching staff is a ___ opponent for any team."},
    {"word": "Skillful", "def": "熟練的", "ex": "The ___ shortstop made the double play look easy."},
    {"word": "Impactful", "def": "有影響力的", "ex": "His home run was the most ___ play of the game."},
    {"word": "Unstoppable", "def": "無法阻擋的", "ex": "When he is hitting like this, he is ___."},
    {"word": "Disciplined", "def": "守紀律的", "ex": "A ___ hitter waits for the perfect pitch."},
    {"word": "Cooperative", "def": "合作的", "ex": "The team is very ___ and works well together."},
    {"word": "Courageous", "def": "英勇的", "ex": "It was a ___ decision to play with a minor injury."},
    {"word": "Vibrant", "def": "充滿生機的", "ex": "The atmosphere in the stadium was incredibly ___."},
    {"word": "Limitless", "def": "無限的", "ex": "The young outfielder has ___ potential."},
    {"word": "Majestic", "def": "雄偉的", "ex": "The ball flew in a ___ arc over the scoreboard."},
    {"word": "Graceful", "def": "優雅的", "ex": "His slide into home plate was perfectly ___."},
    {"word": "Rigorous", "def": "嚴格的", "ex": "Spring training involves a ___ schedule for all players."},
    {"word": "Intricate", "def": "複雜的", "ex": "The pitcher uses an ___ set of signals with the catcher."},
    {"word": "Vigorous", "def": "有力的", "ex": "The fans gave a ___ round of applause."},
    {"word": "Authentic", "def": "真實的", "ex": "He owns an ___ signed bat from a legendary player."},
    {"word": "Brilliant", "def": "燦爛的/聰明的", "ex": "The coach came up with a ___ plan to win the game."},
    {"word": "Diligent", "def": "勤奮的", "ex": "The ___ player never misses a day of practice."},
    {"word": "Efficient", "def": "高效率的", "ex": "The pitcher was very ___, needing only 90 pitches for a full game."},
    {"word": "Flexible", "def": "靈活的", "ex": "You need to be ___ to catch balls in the dirt."},
    {"word": "Glorious", "def": "光榮的", "ex": "It was a ___ day for a championship parade."},
    {"word": "Harmonious", "def": "和諧的", "ex": "The team has a ___ relationship between players and coaches."},
    {"word": "Influential", "def": "有影響力的", "ex": "The retired player remains an ___ figure in the sport."},
    {"word": "Keen", "def": "敏銳的", "ex": "A good hitter has a ___ eye for the strike zone."},
    {"word": "Luminous", "def": "發光的", "ex": "The ___ lights of the stadium could be seen from miles away."},
    {"word": "Meticulous", "def": "一絲不苟的", "ex": "Groundkeepers are ___ about the condition of the grass."},
    {"word": "Noble", "def": "高尚的", "ex": "He showed ___ character by admitting he missed the tag."},
    
    # Verbs (91-150)
    {"word": "Sprint", "def": "衝刺", "ex": "You must ___ to first base to beat the throw."},
    {"word": "Launch", "def": "大力擊出", "ex": "He managed to ___ the ball deep into the stands."},
    {"word": "Celebrate", "def": "慶祝", "ex": "The team will ___ their win with a parade."},
    {"word": "Achieve", "def": "達成", "ex": "He worked hard to ___ his goal of 30 home runs."},
    {"word": "Defeat", "def": "擊敗", "ex": "Our goal today is to ___ our rivals."},
    {"word": "Conquer", "def": "征服", "ex": "They hope to ___ the league and win the title."},
    {"word": "Participate", "def": "參加", "ex": "Every player got a chance to ___ in the All-Star game."},
    {"word": "Improve", "def": "進步", "ex": "You must practice daily to ___ your batting average."},
    {"word": "Demonstrate", "def": "展示", "ex": "The coach will ___ how to slide safely."},
    {"word": "Perform", "def": "表現", "ex": "Players must ___ well under high pressure."},
    {"word": "Injure", "def": "受傷", "ex": "Be careful not to ___ your arm by throwing too hard."},
    {"word": "Recover", "def": "康復", "ex": "It took him two months to ___ from the knee surgery."},
    {"word": "Retire", "def": "退休", "ex": "The pitcher decided to ___ after 20 years in baseball."},
    {"word": "Draft", "def": "選秀", "ex": "The team will ___ new players from college next month."},
    {"word": "Trade", "def": "交易", "ex": "The two teams agreed to ___ their star players."},
    {"word": "Encourage", "def": "鼓勵", "ex": "Fans continue to ___ the team even when they lose."},
    {"word": "Inspire", "def": "啟發", "ex": "The captain's speech helped to ___ the younger players."},
    {"word": "Represent", "def": "代表", "ex": "He was chosen to ___ his country in the Olympics."},
    {"word": "Compete", "def": "競爭", "ex": "Athletes travel from all over to ___ in this league."},
    {"word": "Train", "def": "訓練", "ex": "They ___ for hours every day in the batting cages."},
    {"word": "Exceed", "def": "超過", "ex": "He hopes to ___ the record for most stolen bases."},
    {"word": "Concentrate", "def": "專注", "ex": "The pitcher must ___ on the catcher's glove."},
    {"word": "Anticipate", "def": "預期", "ex": "The fielder was able to ___ where the ball would land."},
    {"word": "Coordinate", "def": "協調", "ex": "Shortstops must ___ with the second baseman."},
    {"word": "Sacrifice", "def": "犧牲", "ex": "He hit a ___ fly to bring the runner home."},
    {"word": "Transform", "def": "轉變", "ex": "A good coach can ___ a weak team into a winner."},
    {"word": "Strengthen", "def": "加強", "ex": "Lifting weights will help to ___ your throwing arm."},
    {"word": "Motivate", "def": "激勵", "ex": "The crowd's cheers help to ___ the players."},
    {"word": "Analyze", "def": "分析", "ex": "Coaches ___ video to find weaknesses in the opponent."},
    {"word": "Overcome", "def": "克服", "ex": "The player had to ___ a lot of pain to stay in the game."},
    {"word": "Persist", "def": "堅持", "ex": "You must ___ even when the training is difficult."},
    {"word": "Succeed", "def": "成功", "ex": "Hard work is the only way to ___ in the Big Leagues."},
    {"word": "Prepare", "def": "準備", "ex": "Teams arrive early to ___ for the double-header."},
    {"word": "Adjust", "def": "調整", "ex": "The batter had to ___ his stance for the fast pitcher."},
    {"word": "Execute", "def": "執行", "ex": "They were able to ___ the perfect double play."},
    {"word": "Dominate", "def": "主宰", "ex": "The ace pitcher continues to ___ the hitters."},
    {"word": "Master", "def": "精通", "ex": "It takes years to ___ the knuckleball pitch."},
    {"word": "Sustain", "def": "維持", "ex": "It is hard to ___ such a high level of play all season."},
    {"word": "Vocalize", "def": "喊出", "ex": "Fielders must ___ when they are going for the fly ball."},
    {"word": "Collaborate", "def": "協作", "ex": "The pitcher and catcher must ___ on every pitch choice."},
    {"word": "Accelerate", "def": "加速", "ex": "You need to ___ quickly to catch a deep fly ball."},
    {"word": "Bypass", "def": "繞過", "ex": "The runner tried to ___ the tag by sliding wide."},
    {"word": "Cultivate", "def": "培養", "ex": "Managers try to ___ a winning culture in the clubhouse."},
    {"word": "Dedicate", "def": "致力於", "ex": "He decided to ___ his life to becoming a pro baseball player."},
    {"word": "Elevate", "def": "提升", "ex": "A great leader can ___ the performance of everyone around them."},
    {"word": "Focus", "def": "聚焦", "ex": "You must ___ on the ball all the way into the glove."},
    {"word": "Generate", "def": "產生", "ex": "The pitcher uses his legs to ___ power for his fastball."},
    {"word": "Hasten", "def": "加速", "ex": "The rain began to ___, so the game was called early."},
    {"word": "Illuminate", "def": "照亮", "ex": "The scoreboard will ___ once the game starts."},
    {"word": "Justify", "def": "證明...有理", "ex": "He tried to ___ his expensive salary with a home run."},
    {"word": "Kindle", "def": "點燃", "ex": "The win helped to ___ hope for a championship."},
    {"word": "Liberate", "def": "解放", "ex": "Winning the game seemed to ___ the team from their stress."},
    {"word": "Magnify", "def": "放大", "ex": "Every mistake is ___ during the World Series."},
    {"word": "Negotiate", "def": "談判", "ex": "The agent will ___ a new contract for the pitcher."},
    {"word": "Observe", "def": "觀察", "ex": "Hitter carefully ___ the pitcher's motion for clues."},
    {"word": "Ponder", "def": "思索", "ex": "The coach will ___ the starting lineup overnight."},
    {"word": "Quicken", "def": "加快", "ex": "He tried to ___ his pace while running the bases."},
    {"word": "Radiate", "def": "散發", "ex": "The fans' excitement began to ___ throughout the stadium."},
    {"word": "Stimulate", "def": "刺激", "ex": "Loud music is used to ___ the crowd's energy."},
    {"word": "Terminate", "def": "終止", "ex": "The umpire has the power to ___ the game if it rains too much."},
    
    # Concepts & Nouns (151-200)
    {"word": "Opportunity", "def": "機會", "ex": "Every at-bat is an ___ to help the team win."},
    {"word": "Strategy", "def": "策略", "ex": "The manager's ___ won them the game in the end."},
    {"word": "Technique", "def": "技巧", "ex": "Proper pitching ___ prevents arm injuries."},
    {"word": "Victory", "def": "勝利", "ex": "Nothing feels better than a hard-earned ___."},
    {"word": "Dedication", "def": "奉獻", "ex": "It takes ___ to practice in the rain and cold."},
    {"word": "Obstacle", "def": "障礙", "ex": "Injuries are the biggest ___ for an athlete."},
    {"word": "Challenge", "def": "挑戰", "ex": "Playing against the best team is a great ___."},
    {"word": "Record", "def": "紀錄", "ex": "He holds the ___ for the most home runs in a season."},
    {"word": "Highlight", "def": "亮點", "ex": "The diving catch was the ___ of the evening."},
    {"word": "Career", "def": "職業生涯", "ex": "He had a long and successful ___ in baseball."},
    {"word": "Biography", "def": "傳記", "ex": "I am reading a ___ of Shohei Ohtani."},
    {"word": "Interview", "def": "採訪", "ex": "The MVP gave an ___ right after the game."},
    {"word": "Season", "def": "賽季", "ex": "The baseball ___ lasts from spring until fall."},
    {"word": "Series", "def": "系列賽", "ex": "The World ___ is the most important event in baseball."},
    {"word": "Generation", "def": "世代", "ex": "He is the best player of this ___."},
    {"word": "Nation", "def": "國家", "ex": "Baseball is the favorite pastime of the ___."},
    {"word": "Pressure", "def": "壓力", "ex": "There is a lot of ___ on the pitcher in the 9th inning."},
    {"word": "Success", "def": "成功", "ex": "His ___ is due to years of hard work."},
    {"word": "Failure", "def": "失敗", "ex": "Don't let a ___ like a strikeout discourage you."},
    {"word": "Effort", "def": "努力", "ex": "Winning requires a team ___ from everyone."},
    {"word": "Endurance", "def": "耐力", "ex": "Pitchers need great ___ to throw 100 pitches."},
    {"word": "Potential", "def": "潛力", "ex": "The young player has the ___ to be a superstar."},
    {"word": "Agility", "def": "敏捷", "ex": "Shortstops need great ___ to reach the ball quickly."},
    {"word": "Momentum", "def": "動力", "ex": "The home run gave the team the ___ they needed."},
    {"word": "Rivalry", "def": "競爭關係", "ex": "The ___ between the Red Sox and Yankees is famous."},
    {"word": "Leadership", "def": "領導力", "ex": "The catcher showed great ___ on the field."},
    {"word": "Integrity", "def": "誠信", "ex": "A good player always plays with ___ and honesty."},
    {"word": "Loyalty", "def": "忠誠", "ex": "He showed ___ by staying with the same team for his career."},
    {"word": "Ambition", "def": "雄心", "ex": "His ___ is to become the best pitcher in the world."},
    {"word": "Legacy", "def": "傳承", "ex": "The retired player left behind a great ___ for the team."},
    {"word": "Adversity", "def": "逆境", "ex": "A true champion can overcome ___ to win."},
    {"word": "Foundation", "def": "基礎", "ex": "Basic skills are the ___ of becoming a great player."},
    {"word": "Magnitude", "def": "量級", "ex": "The ___ of his achievement was felt by the whole world."},
    {"word": "Excellence", "def": "卓越", "ex": "The team strives for ___ in every game they play."},
    {"word": "Perspective", "def": "視角", "ex": "The coach gave him a new ___ on how to bat."},
    {"word": "Inspiration", "def": "靈感", "ex": "His success is an ___ to young players everywhere."},
    {"word": "Preparation", "def": "準備", "ex": "Winning is 90% ___ and 10% execution."},
    {"word": "Achievement", "def": "成就", "ex": "Winning the MVP is a massive ___."},
    {"word": "Motivation", "def": "動機", "ex": "His primary ___ is his love for the game."},
    {"word": "Commitment", "def": "承諾", "ex": "Playing baseball requires a deep ___ to practice."},
    {"word": "Collaboration", "def": "合作", "ex": "The double play required perfect ___ between infielders."},
    {"word": "Precision", "def": "精確性", "ex": "A pitcher needs incredible ___ to hit the corners of the zone."},
    {"word": "Resilience", "def": "韌性", "ex": "The team's ___ helped them recover from a losing streak."},
    {"word": "Authenticity", "def": "真實性", "ex": "The collector verified the ___ of the old jersey."},
    {"word": "Diversity", "def": "多樣性", "ex": "Major League Baseball celebrates the ___ of its players."},
    {"word": "Empowerment", "def": "授權/賦能", "ex": "The new manager's focus is on the ___ of young players."},
    {"word": "Fortitude", "def": "堅毅", "ex": "It takes mental ___ to pitch during a cold, rainy game."},
    {"word": "Gratefulness", "def": "感激", "ex": "The player expressed his ___ to the fans after the game."},
    {"word": "Humility", "def": "謙遜", "ex": "The star showed great ___ when interviewed about his record."},
    {"word": "Innovation", "def": "創新", "ex": "New technology in training is an important ___ for teams."}
]

# ---------------------------
# Helpers
# ---------------------------
def fresh_initial_state():
    data = copy.deepcopy(initial_word_data)
    for item in data:
        item.setdefault("score", 0)
        item.setdefault("last_correct_time", None)
        item.setdefault("ex", "")
        try:
            item["score"] = int(item.get("score", 0))
        except:
            item["score"] = 0
        lct = item.get("last_correct_time")
        item["last_correct_time"] = float(lct) if lct is not None else None
    return data

def merge_progress(loaded):
    base = fresh_initial_state()
    if not isinstance(loaded, list): return base
    index = {w.get("word"): w for w in loaded if isinstance(w, dict) and w.get("word")}
    for item in base:
        src = index.get(item["word"])
        if src:
            item["score"] = int(src.get("score", 0))
            lct = src.get("last_correct_time")
            item["last_correct_time"] = float(lct) if lct is not None else None
    return base

# --- SESSION STATE ---
DEFAULTS = {
    "current_index": 0,
    "game_score": 0,
    "game_active": False,
    "current_question": None,
    "options": [],
    "feedback": "",
    "current_audio": None,
    "session_words": [],
    "session_finished": False
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = copy.deepcopy(v)

if "vocab_data" not in st.session_state:
    st.session_state.vocab_data = fresh_initial_state()

# --- AUDIO ---
@st.cache_data(show_spinner=False)
def tts_mp3_bytes(txt: str) -> bytes:
    try:
        tts = gTTS(text=txt, lang="en")
        f = io.BytesIO()
        tts.write_to_fp(f)
        return f.getvalue()
    except: return b""

def get_audio(txt):
    b = tts_mp3_bytes(txt)
    return io.BytesIO(b) if b else None

# --- LOGIC ---
def start_game():
    cands = [w for w in st.session_state.vocab_data if w["score"] < MASTERY_THRESHOLD]
    if not cands:
        st.session_state.game_active = "WON"
        return
    st.session_state.session_words = random.sample(cands, min(ROUNDS_PER_GAME, len(cands)))
    st.session_state.current_index = 0
    st.session_state.game_score = 0
    st.session_state.game_active = True
    st.session_state.session_finished = False
    st.session_state.feedback = ""
    next_q()

def next_q():
    if st.session_state.current_index < len(st.session_state.session_words):
        t = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question = t
        st.session_state.current_audio = get_audio(t["word"])
        pool = list(dict.fromkeys([w["def"] for w in st.session_state.vocab_data if w["def"] != t["def"]]))
        opts = [t["def"]] + random.sample(pool, min(3, len(pool)))
        random.shuffle(opts)
        st.session_state.options = opts
    else:
        st.session_state.game_active = False
        st.session_state.session_finished = True

def check(ans):
    t, now = st.session_state.current_question, time.time()
    if not t: return
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
                i["score"] = max(0, i["score"] - 1)
                break
    st.session_state.current_index += 1
    next_q()

# --- UI ---
st.set_page_config(page_title="Baseball Superstars Vocab", page_icon="⚾")
st.title("⚾ 200 Baseball & Elite English Vocab")

# Sidebar
st.sidebar.header("Manager's Office")
up = st.sidebar.file_uploader("Upload Progress (.json)", type="json")
if up:
    try:
        st.session_state.vocab_data = merge_progress(json.load(up))
        st.sidebar.success("Stats Loaded!")
    except: st.sidebar.error("File Error.")

mastered = sum(1 for w in st.session_state.vocab_data if w["score"] >= MASTERY_THRESHOLD)
st.sidebar.metric("Mastered Words", f"{mastered} / {len(st.session_state.vocab_data)}")
st.sidebar.download_button("💾 Save Progress", data=json.dumps(st.session_state.vocab_data, indent=4, ensure_ascii=False), file_name="progress.json")

# Screens
if st.session_state.game_active == "WON":
    st.balloons()
    st.success("🏆 MVP! ALL 200 WORDS MASTERED!")
    if st.button("Reset Everything"):
        st.session_state.vocab_data = fresh_initial_state()
        for k in DEFAULTS: st.session_state[k] = copy.deepcopy(DEFAULTS[k])
        st.rerun()

elif st.session_state.session_finished:
    st.header("📊 Game Over: Final Scoreboard")
    score = st.session_state.game_score
    total = len(st.session_state.session_words)
    percent = (score/total) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Final Score", f"{score} / {total}")
    col2.metric("Accuracy", f"{int(percent)}%")
    
    if percent == 100: st.success("🎯 PERFECT GAME! You're a superstar!")
    elif percent >= 80: st.info("🔥 ALL-STAR! You have a great eye for English.")
    elif percent >= 60: st.warning("⚾ SOLID PERFORMANCE. Keep practicing in the bullpen.")
    else: st.error("👟 ROOKIE SEASON. Time to hit the batting cages!")
    
    if st.button("Play Another Game", use_container_width=True):
        st.session_state.session_finished = False
        start_game()
        st.rerun()

elif not st.session_state.game_active:
    st.header("Ready for Batting Practice?")
    
    if st.button("▶️ Start Game (20 Rounds)", use_container_width=True):
        start_game()
        st.rerun()

    df = pd.DataFrame(st.session_state.vocab_data)
    if not df.empty and df["score"].sum() > 0:
        st.subheader("Your Top Performers (Mastery)")
        st.table(df[df["score"] > 0].sort_values("score", ascending=False).head(10)[["word", "def", "score"]])

else:
    # Game UI
    total = len(st.session_state.session_words)
    st.progress(st.session_state.current_index / total)
    st.metric("In-Game Score", st.session_state.game_score)

    q = st.session_state.current_question
    st.markdown(f"## Word: **{q['word']}**")
    st.info(f"💡 **Sentence:** {q.get('ex', '')}")

    if st.session_state.current_audio: st.audio(st.session_state.current_audio)

    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.options):
        if cols[i % 2].button(opt, use_container_width=True, key=f"btn_{st.session_state.current_index}_{i}"):
            check(opt)
            st.rerun()

    if st.session_state.feedback:
        if "✅" in st.session_state.feedback: st.success(st.session_state.feedback)
        else: st.error(st.session_state.feedback)
