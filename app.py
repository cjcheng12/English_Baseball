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

# --- THE 200 ADVANCED VOCABULARY LIST ---
initial_word_data = [
    # --- PRO BASEBALL BASICS (1-30) ---
    {"word": "Pitcher", "def": "投手", "ex": "The ___ threw a fast ball at 100 mph!"},
    {"word": "Catcher", "def": "捕手", "ex": "The ___ caught the ball behind home plate."},
    {"word": "Umpire", "def": "裁判", "ex": "The ___ shouted 'Strike!' to the batter."},
    {"word": "Inning", "def": "局 (比賽的)", "ex": "The home team scored three runs in the first ___."},
    {"word": "Dugout", "def": "球員休息區", "ex": "The players sat in the ___ waiting for their turn to bat."},
    {"word": "Bullpen", "def": "牛棚", "ex": "The relief pitcher is warming up in the ___."},
    {"word": "Roster", "def": "球員名單", "ex": "The team's ___ includes several young superstars."},
    {"word": "Stadium", "def": "體育場", "ex": "Thousands of fans packed the ___ for the night game."},
    {"word": "Grand Slam", "def": "滿貫全壘打", "ex": "The bases were loaded when he hit a spectacular ___!"},
    {"word": "Strikeout", "def": "三振出局", "ex": "The pitcher recorded his tenth ___ of the game."},
    {"word": "Infielder", "def": "內野手", "ex": "The ___ caught the ground ball and threw it to first."},
    {"word": "Outfielder", "def": "外野手", "ex": "The ___ ran back and caught the ball near the wall."},
    {"word": "Mound", "def": "投手丘", "ex": "The pitcher stood on the ___ and looked at the catcher."},
    {"word": "Batter", "def": "打擊者", "ex": "The ___ stepped into the box and gripped the bat."},
    {"word": "Helmet", "def": "頭盔", "ex": "Always wear your ___ to protect your head from the ball."},
    {"word": "Jersey", "def": "球衣", "ex": "He wore his lucky team ___ to every game."},
    {"word": "Scoreboard", "def": "計分板", "ex": "The ___ showed that the game was tied in the 9th."},
    {"word": "Spectator", "def": "觀眾", "ex": "Every ___ stood up to cheer when the ball left the park."},
    {"word": "Diamond", "def": "棒球場內野", "ex": "The players ran around the ___ after the home run."},
    {"word": "Triple", "def": "三壘安打", "ex": "He sprinted around the bases for a standing-up ___."},
    
    # --- ELITE PLAYER SKILLS (ADJECTIVES 31-100) ---
    {"word": "Phenomenal", "def": "非凡的", "ex": "His ability to hit the ball is simply ___."},
    {"word": "Dominant", "def": "佔優勢的", "ex": "The pitcher was ___ and didn't allow any hits."},
    {"word": "Versatile", "def": "全能的", "ex": "He is a ___ player who can play any position."},
    {"word": "Aggressive", "def": "積極的", "ex": "The runner made an ___ slide into second base."},
    {"word": "Consistent", "def": "穩定的", "ex": "She is a ___ hitter who gets a hit in every game."},
    {"word": "Athletic", "def": "體格健壯的", "ex": "Shortstops must be very ___ to reach fast grounders."},
    {"word": "Accurate", "def": "準確的", "ex": "The catcher made an ___ throw to catch the runner."},
    {"word": "Powerful", "def": "有力的", "ex": "He used a ___ swing to drive the ball over the fence."},
    {"word": "Resilient", "def": "有韌性的", "ex": "The team was ___ and came back from a 5-run lead."},
    {"word": "Strategic", "def": "策略性的", "ex": "The manager made a ___ decision to bunt the ball."},
    {"word": "Exceptional", "def": "優越的", "ex": "His hand-eye coordination is ___."},
    {"word": "Fearless", "def": "大膽的", "ex": "The ___ catcher blocked the plate against the runner."},
    {"word": "Disciplined", "def": "守紀律的", "ex": "A ___ hitter waits for the perfect pitch."},
    {"word": "Vibrant", "def": "充滿生機的", "ex": "The atmosphere in the stadium was incredibly ___."},
    {"word": "Limitless", "def": "無限的", "ex": "The young outfielder has ___ potential."},
    {"word": "Majestic", "def": "雄偉的", "ex": "The ball flew in a ___ arc over the scoreboard."},
    {"word": "Graceful", "def": "優雅的", "ex": "His slide into home plate was perfectly ___."},
    {"word": "Rigorous", "def": "嚴格的", "ex": "Spring training involves a ___ schedule for all players."},
    {"word": "Intricate", "def": "複雜的", "ex": "The pitcher uses an ___ set of signals with the catcher."},
    {"word": "Authentic", "def": "真實的", "ex": "He owns an ___ signed bat from a legendary player."},
    {"word": "Diligent", "def": "勤奮的", "ex": "The ___ player never misses a day of practice."},
    {"word": "Efficient", "def": "高效率的", "ex": "The pitcher was very ___, needing only 90 pitches."},
    {"word": "Flexible", "def": "靈活的", "ex": "You need to be ___ to catch balls in the dirt."},
    {"word": "Influential", "def": "有影響力的", "ex": "The retired player remains an ___ figure in the sport."},
    {"word": "Keen", "def": "敏銳的", "ex": "A good hitter has a ___ eye for the strike zone."},
    {"word": "Meticulous", "def": "一絲不苟的", "ex": "Groundkeepers are ___ about the condition of the grass."},
    {"word": "Tenacious", "def": "頑強的", "ex": "The runner showed a ___ spirit by never giving up on the play."},
    {"word": "Formidable", "def": "強大的", "ex": "The opponent has a ___ pitching rotation."},
    {"word": "Infallible", "def": "絕無錯誤的", "ex": "No player is ___; everyone makes mistakes sometimes."},
    {"word": "Spontaneous", "def": "自發的", "ex": "The crowd broke into a ___ cheer after the double play."},
    {"word": "Substantial", "def": "重大的", "ex": "Winning the game gave the team a ___ lead in the standings."},
    {"word": "Adept", "def": "熟練的", "ex": "He is very ___ at catching fly balls in the sun."},
    {"word": "Elated", "def": "興高采烈的", "ex": "The team was ___ after winning the championship."},
    {"word": "Exuberant", "def": "精力充沛的", "ex": "The rookie’s ___ energy cheered up the whole dugout."},
    {"word": "Immaculate", "def": "潔淨無暇的", "ex": "He pitched an ___ inning: 9 pitches, 3 strikeouts."},
    {"word": "Perceptive", "def": "感知的/敏銳的", "ex": "The ___ coach noticed the pitcher was getting tired."},
    {"word": "Redoubtable", "def": "令人敬畏的", "ex": "The pitcher is a ___ opponent on the mound."},
    {"word": "Sovereign", "def": "至高無上的", "ex": "The World Series winner is the ___ team of baseball."},
    {"word": "Unanimous", "def": "全體一致的", "ex": "He was the ___ choice for the MVP award."},
    {"word": "Venerable", "def": "受人尊敬的", "ex": "Fenway Park is a ___ stadium with a long history."},
    {"word": "Versatile", "def": "多才多藝的", "ex": "Being ___ means you can play infield and outfield."},
    {"word": "Zealous", "def": "熱心的", "ex": "The ___ fans stayed in the rain to finish the game."},
    {"word": "Abundant", "def": "豐富的", "ex": "There is ___ talent in the minor league system."},
    {"word": "Benevolent", "def": "仁慈的", "ex": "The ___ star player donated gloves to the youth team."},
    {"word": "Capacious", "def": "容量大的", "ex": "The new stadium is ___, holding over 50,000 fans."},
    {"word": "Eloquent", "def": "雄辯的/有說服力的", "ex": "The captain gave an ___ speech before the game."},
    {"word": "Fervent", "def": "熱烈的", "ex": "He has a ___ desire to win the World Series."},
    {"word": "Inquisitive", "def": "好奇的", "ex": "The ___ rookie asked many questions about strategy."},
    {"word": "Luminous", "def": "明亮的", "ex": "The stadium lights were ___ against the night sky."},
    {"word": "Prudent", "def": "謹慎的", "ex": "It was a ___ decision to walk the dangerous hitter."},
    {"word": "Resplendent", "def": "燦爛的", "ex": "The trophy looked ___ in the morning sun."},
    {"word": "Stedfast", "def": "堅定的", "ex": "The fans remained ___ even when the team was losing."},
    {"word": "Vigilant", "def": "警惕的", "ex": "Outfielders must be ___ to see where the ball is hit."},
    {"word": "Acrimonious", "def": "尖刻的/嚴厲的", "ex": "The argument with the umpire became quite ___."},
    {"word": "Bustling", "def": "熙熙攘攘的", "ex": "The stadium was ___ with fans buying snacks."},
    {"word": "Candid", "def": "坦率的", "ex": "The manager was ___ about why the team lost."},
    {"word": "Dauntless", "def": "無所畏懼的", "ex": "The ___ runner slid head-first into home."},
    {"word": "Ephemeral", "def": "短暫的", "ex": "Fame in baseball can be ___; you must keep working hard."},
    {"word": "Garrulous", "def": "喋喋不休的", "ex": "The ___ announcer talked through the whole inning."},
    {"word": "Haughty", "def": "傲慢的", "ex": "He tried not to be ___ after hitting four home runs."},
    {"word": "Indomitable", "def": "不屈不撓的", "ex": "The team’s ___ spirit led them to a comeback win."},
    {"word": "Jovial", "def": "快樂的", "ex": "The dugout was in a ___ mood after the victory."},
    {"word": "Languid", "def": "慢悠悠的/無力的", "ex": "The game moved at a ___ pace on the hot afternoon."},
    {"word": "Munificent", "def": "慷慨的", "ex": "The owner was ___ in providing new gear for players."},
    {"word": "Nefarious", "def": "邪惡的/不法的", "ex": "Stealing signs electronically is considered ___."},
    {"word": "Obsequious", "def": "諂媚的", "ex": "He didn't like how the agent was being ___ to the owner."},
    {"word": "Pugnacious", "def": "好鬥的", "ex": "The ___ batter was ready to argue every strike call."},
    {"word": "Quixotic", "def": "不切實際的", "ex": "It was a ___ attempt to catch a ball 20 feet over the fence."},
    {"word": "Raucous", "def": "喧鬧的", "ex": "The crowd became ___ when the home team scored."},
    {"word": "Sagacious", "def": "聰敏的", "ex": "The ___ veteran knew exactly where the ball would be hit."},

    # --- PRO PLAYER ACTIONS (VERBS 101-160) ---
    {"word": "Sprint", "def": "衝刺", "ex": "You must ___ to first base to beat the throw."},
    {"word": "Launch", "def": "大力擊出", "ex": "He managed to ___ the ball deep into the stands."},
    {"word": "Achieve", "def": "達成", "ex": "He worked hard to ___ his goal of 30 home runs."},
    {"word": "Defeat", "def": "擊敗", "ex": "Our goal today is to ___ our rivals."},
    {"word": "Participate", "def": "參加", "ex": "Every player got a chance to ___ in the All-Star game."},
    {"word": "Improve", "def": "進步", "ex": "You must practice daily to ___ your batting average."},
    {"word": "Demonstrate", "def": "展示", "ex": "The coach will ___ how to slide safely."},
    {"word": "Recover", "def": "康復", "ex": "It took him two months to ___ from the knee surgery."},
    {"word": "Inspire", "def": "啟發", "ex": "The captain's speech helped to ___ the younger players."},
    {"word": "Exceed", "def": "超過", "ex": "He hopes to ___ the record for most stolen bases."},
    {"word": "Anticipate", "def": "預期", "ex": "The fielder was able to ___ where the ball would land."},
    {"word": "Analyze", "def": "分析", "ex": "Coaches ___ video to find weaknesses in the opponent."},
    {"word": "Overcome", "def": "克服", "ex": "The player had to ___ a lot of pain to stay in the game."},
    {"word": "Succeed", "def": "成功", "ex": "Hard work is the only way to ___ in the Big Leagues."},
    {"word": "Adjust", "def": "調整", "ex": "The batter had to ___ his stance for the fast pitcher."},
    {"word": "Master", "def": "精通", "ex": "It takes years to ___ the knuckleball pitch."},
    {"word": "Collaborate", "def": "協作", "ex": "The pitcher and catcher must ___ on every pitch choice."},
    {"word": "Accelerate", "def": "加速", "ex": "You need to ___ quickly to catch a deep fly ball."},
    {"word": "Elevate", "def": "提升", "ex": "A great leader can ___ the performance of everyone."},
    {"word": "Generate", "def": "產生", "ex": "The pitcher uses his legs to ___ power."},
    {"word": "Negotiate", "def": "談判", "ex": "The agent will ___ a new contract for the pitcher."},
    {"word": "Observe", "def": "觀察", "ex": "Hitter carefully ___ the pitcher's motion for clues."},
    {"word": "Terminate", "def": "終止", "ex": "The umpire can ___ the game if it rains too much."},
    {"word": "Augment", "def": "增加/加強", "ex": "He tried to ___ his strength by lifting weights."},
    {"word": "Belittle", "def": "輕視", "ex": "Never ___ your teammates for making an error."},
    {"word": "Concur", "def": "同意", "ex": "The umpires had to ___ on the final home run call."},
    {"word": "Delineate", "def": "描繪/畫出", "ex": "The lines ___ the fair and foul territory."},
    {"word": "Emulate", "def": "效法", "ex": "Young players try to ___ Ohtani's hitting style."},
    {"word": "Fabricate", "def": "捏造", "ex": "Don't ___ excuses for missing batting practice."},
    {"word": "Garner", "def": "獲得", "ex": "He managed to ___ enough votes to be an All-Star."},
    {"word": "Hinder", "def": "阻礙", "ex": "The rain might ___ the pitcher's ability to grip the ball."},
    {"word": "Impediment", "def": "妨礙 (名詞用作動詞意涵)", "ex": "The injury was an ___ to his season goals."},
    {"word": "Juxtapose", "def": "並列對比", "ex": "The coach likes to ___ the stats of the two hitters."},
    {"word": "Kindle", "def": "點燃", "ex": "A lead-off double can ___ a big scoring inning."},
    {"word": "Lament", "def": "哀悼/遺憾", "ex": "Fans will ___ the loss of the legendary announcer."},
    {"word": "Mitigate", "def": "減輕", "ex": "Wearing a helmet helps ___ the risk of injury."},
    {"word": "Nullify", "def": "使無效", "ex": "A foul ball will ___ the play that just happened."},
    {"word": "Obliterate", "def": "衝刷/抹除", "ex": "He managed to ___ the old home run record."},
    {"word": "Pacify", "def": "安撫", "ex": "The manager tried to ___ the angry player."},
    {"word": "Quell", "def": "平息", "ex": "The pitcher’s strikeout helped ___ the opponent’s rally."},
    {"word": "Reciprecate", "def": "回報", "ex": "The fans ___ the players’ effort with a standing ovation."},
    {"word": "Scrutinize", "def": "詳細檢查", "ex": "Umpires will ___ the replay to see if he was safe."},
    {"word": "Thwart", "def": "挫敗/阻撓", "ex": "The catcher’s throw helped ___ the stolen base attempt."},
    {"word": "Utilize", "def": "利用", "ex": "Teams ___ data to position their outfielders."},
    {"word": "Vindicate", "def": "證明清白", "ex": "The replay helped ___ the umpire's original call."},
    {"word": "Waive", "def": "放棄/豁免", "ex": "The team decided to ___ the struggling pitcher."},
    {"word": "Exacerbate", "def": "使惡化", "ex": "Running on a sore ankle will only ___ the injury."},
    {"word": "Forfeit", "def": "喪失/棄權", "ex": "If a team doesn't show up, they must ___ the game."},
    {"word": "Instigate", "def": "煽動/發起", "ex": "The runner tried to ___ a mistake by dancing off base."},
    {"word": "Ostracize", "def": "排斥", "ex": "Players who cheat are often ___ by the league."},
    {"word": "Pervade", "def": "彌漫/普及", "ex": "A sense of excitement began to ___ the stadium."},
    {"word": "Reiterate", "def": "重申", "ex": "The coach had to ___ the importance of bunting."},
    {"word": "Supplant", "def": "取代", "ex": "The rookie might ___ the veteran in the starting lineup."},
    {"word": "Transcend", "def": "超越", "ex": "Great players ___ the sport and become world icons."},
    {"word": "Usurp", "def": "篡奪/奪取", "ex": "He tried to ___ the captain's role on the team."},
    {"word": "Vacillate", "def": "猶豫", "ex": "The hitter shouldn't ___; he needs to swing with confidence."},
    {"word": "Wane", "def": "減少/衰落", "ex": "The pitcher's velocity began to ___ in the 9th inning."},
    {"word": "Ameliorate", "def": "改善", "ex": "New turf was installed to ___ the playing conditions."},
    {"word": "Castigate", "def": "嚴厲斥責", "ex": "The manager will ___ any player who breaks team rules."},
    {"word": "Disseminate", "def": "散播/宣傳", "ex": "The team uses social media to ___ game updates."},

    # --- THE MENTAL GAME (CONCEPTS/NOUNS 161-200) ---
    {"word": "Opportunity", "def": "機會", "ex": "Every at-bat is an ___ to help the team win."},
    {"word": "Victory", "def": "勝利", "ex": "Nothing feels better than a hard-earned ___."},
    {"word": "Obstacle", "def": "障礙", "ex": "Injuries are the biggest ___ for an athlete."},
    {"word": "Highlight", "def": "亮點", "ex": "The diving catch was the ___ of the evening."},
    {"word": "Pressure", "def": "壓力", "ex": "There is a lot of ___ in the 9th inning."},
    {"word": "Potential", "def": "潛力", "ex": "The young player has the ___ to be a superstar."},
    {"word": "Leadership", "def": "領導力", "ex": "The catcher showed great ___ on the field."},
    {"word": "Integrity", "def": "誠信", "ex": "A good player always plays with ___ and honesty."},
    {"word": "Legacy", "def": "傳承", "ex": "The retired player left behind a great ___."},
    {"word": "Adversity", "def": "逆境", "ex": "A true champion can overcome ___ to win."},
    {"word": "Excellence", "def": "卓越", "ex": "The team strives for ___ in every game."},
    {"word": "Inspiration", "def": "靈感", "ex": "His success is an ___ to young players."},
    {"word": "Motivation", "def": "動機", "ex": "His primary ___ is his love for the game."},
    {"word": "Precision", "def": "精確性", "ex": "A pitcher needs incredible ___ to hit the corners."},
    {"word": "Innovation", "def": "創新", "ex": "New technology in training is an important ___."},
    {"word": "Animosity", "def": "仇恨/敵意", "ex": "There is no ___ between the rival pitchers."},
    {"word": "Benevolence", "def": "仁慈", "ex": "The player is known for his ___ off the field."},
    {"word": "Celerity", "def": "迅速/敏捷", "ex": "The runner moved with great ___ around second base."},
    {"word": "Dichotomy", "def": "二分法/對立", "ex": "There is a ___ between his calm personality and his fast pitching."},
    {"word": "Epitome", "def": "縮影/典型", "ex": "He is the ___ of a professional athlete."},
    {"word": "Fidelity", "def": "忠誠", "ex": "He showed great ___ to his original team."},
    {"word": "Gregariousness", "def": "愛交際 (名詞)", "ex": "The player’s ___ made him very popular with the fans."},
    {"word": "Hiatus", "def": "停工/間斷", "ex": "The season took a short ___ for the All-Star break."},
    {"word": "Impartiality", "def": "公正", "ex": "The league expects total ___ from all umpires."},
    {"word": "Jubilation", "def": "歡慶", "ex": "There was great ___ in the city after the big win."},
    {"word": "Knack", "def": "本領/技巧", "ex": "He has a ___ for hitting home runs in big moments."},
    {"word": "Lethargy", "def": "無精打采", "ex": "The team had to overcome their ___ after a long road trip."},
    {"word": "Magnitude", "def": "量級/重大", "ex": "The ___ of the game felt like a World Series final."},
    {"word": "Nostalgia", "def": "懷舊", "ex": "Old fans feel ___ when they see the classic jerseys."},
    {"word": "Opulence", "def": "富饒/奢華", "ex": "The new luxury suites show the ___ of the stadium."},
    {"word": "Paragon", "def": "典範", "ex": "He is considered a ___ of sportsmanship."},
    {"word": "Quagmire", "def": "困境", "ex": "The team is in a ___ after losing five games in a row."},
    {"word": "Resilience", "def": "韌性", "ex": "The ___ of the pitcher helped him after giving up a run."},
    {"word": "Sagacity", "def": "睿智", "ex": "The manager’s ___ led to a game-winning substitution."},
    {"word": "Trepidation", "def": "恐懼/憂慮", "ex": "The rookie felt some ___ before his first major league start."},
    {"word": "Ubiquity", "def": "無所不在", "ex": "Baseball’s ___ in Japan is obvious in every park."},
    {"word": "Venerability", "def": "尊嚴/受尊敬 (名詞)", "ex": "The ___ of the old stadium is felt by all who visit."},
    {"word": "Wary", "def": "警惕的 (用作名詞意涵)", "ex": "Being ___ of the pitcher's pick-off move is important."},
    {"word": "Zenith", "def": "鼎盛/頂點", "ex": "Winning the World Series was the ___ of his career."},
    {"word": "Acumen", "def": "敏銳/聰明", "ex": "The player's business ___ helped him sign a great deal."}
]

# ---------------------------
# HELPERS
# ---------------------------
def fresh_initial_state():
    data = copy.deepcopy(initial_word_data)
    for item in data:
        item.setdefault("score", 0)
        item.setdefault("last_correct_time", None)
        item.setdefault("ex", "")
        try:
            item["score"] = int(item["score"])
        except:
            item["score"] = 0
        if item["last_correct_time"] is not None:
            try:
                item["last_correct_time"] = float(item["last_correct_time"])
            except:
                item["last_correct_time"] = None
    return data

def merge_progress(loaded):
    base = fresh_initial_state()
    if not isinstance(loaded, list): return base
    index = {w.get("word"): w for w in loaded if isinstance(w, dict)}
    for item in base:
        src = index.get(item["word"])
        if src:
            item["score"] = int(src.get("score", item["score"]))
            lct = src.get("last_correct_time")
            item["last_correct_time"] = float(lct) if lct else None
    return base

# --- SESSION STATE ---
DEFAULTS = {
    "current_index": 0, "game_score": 0, "game_active": False,
    "current_question": None, "options": [], "feedback": "",
    "current_audio": None, "session_words": [], "show_results": False
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = copy.deepcopy(v)

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
    st.session_state.show_results = False
    st.session_state.feedback = ""
    next_q()

def next_q():
    if st.session_state.current_index < len(st.session_state.session_words):
        t = st.session_state.session_words[st.session_state.current_index]
        st.session_state.current_question = t
        st.session_state.current_audio = get_audio(t["word"])
        pool = [w["def"] for w in st.session_state.vocab_data if w["def"] != t["def"]]
        pool = list(dict.fromkeys(pool))
        k = min(3, len(pool))
        opts = [t["def"]] + (random.sample(pool, k) if k > 0 else [])
        random.shuffle(opts)
        st.session_state.options = opts
    else:
        st.session_state.game_active = False
        st.session_state.show_results = True

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
st.set_page_config(page_title="Baseball Superstars", page_icon="⚾")
st.title("⚾ Advanced English Superstars Trainer")

# Sidebar
st.sidebar.header("Manager's Office")
up = st.sidebar.file_uploader("Upload Progress", type="json")
if up:
    try:
        st.session_state.vocab_data = merge_progress(json.load(up))
        st.sidebar.success("Stats Loaded!")
    except: st.sidebar.error("File Error.")

mastered = sum(1 for w in st.session_state.vocab_data if w["score"] >= MASTERY_THRESHOLD)
st.sidebar.metric("Mastered", f"{mastered} / {len(st.session_state.vocab_data)}")
st.sidebar.download_button("💾 Save Progress", data=json.dumps(st.session_state.vocab_data, indent=4, ensure_ascii=False), file_name="progress.json")

# Result Screen
if st.session_state.show_results:
    st.header("📊 Game Finished!")
    score = st.session_state.game_score
    total = len(st.session_state.session_words)
    percent = (score/total) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Correct Answers", f"{score} / {total}")
    col2.metric("Accuracy", f"{int(percent)}%")
    
    if percent >= 90: st.balloons(); st.success("🏆 MVP! You had a perfect game!")
    elif percent >= 70: st.info("🔥 All-Star! Great hitting today.")
    else: st.warning("👟 Rookie! Back to the batting cages for practice.")
    
    if st.button("Play Another Session", use_container_width=True):
        st.session_state.show_results = False
        start_game()
        st.rerun()

elif st.session_state.game_active == "WON":
    st.balloons(); st.success("🏆 MVP! You've mastered all 200 words!")
    if st.button("Restart Season"):
        st.session_state.vocab_data = fresh_initial_state()
        for k, v in DEFAULTS.items(): st.session_state[k] = copy.deepcopy(v)
        st.rerun()

elif not st.session_state.game_active:
    st.header("Ready for Training?")
    
    if st.button("▶️ Start Game (20 Rounds)", use_container_width=True):
        start_game(); st.rerun()
    
    df = pd.DataFrame(st.session_state.vocab_data)
    if not df.empty and df["score"].sum() > 0:
        st.subheader("Your Top Players (Words)")
        st.table(df[df["score"] > 0].sort_values("score", ascending=False).head(10)[["word", "def", "score"]])

else:
    # Game UI
    total = max(1, len(st.session_state.session_words))
    st.progress(st.session_state.current_index / total)
    st.metric("Session Score", st.session_state.game_score)

    q = st.session_state.current_question
    if q:
        st.markdown(f"## Word: **{q['word']}**")
        sentence = q.get("ex", "").replace("___", f"<span style='color:#e63946; font-weight:700;'>{q['word']}</span>")
        st.markdown(f'<div style="font-size: 28px; padding: 15px; background: #f0f2f6; border-radius: 10px; margin-bottom: 20px;">💡 <b>Sentence:</b><br>{sentence}</div>', unsafe_allow_html=True)

        if st.session_state.current_audio: st.audio(st.session_state.current_audio)

        cols = st.columns(2)
        for i, opt in enumerate(st.session_state.options):
            if cols[i % 2].button(opt, use_container_width=True, key=f"btn_{st.session_state.current_index}_{i}"):
                check(opt); st.rerun()

        if st.session_state.feedback:
            if "✅" in st.session_state.feedback: st.success(st.session_state.feedback)
            else: st.error(st.session_state.feedback)
