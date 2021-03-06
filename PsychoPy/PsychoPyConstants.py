# Settings 

RUN_TYPE_DEBUG = 0
RUN_TYPE_START = 1
RUN_TYPE_SHORT = 2
RUN_TYPE_LONG = 3
RUN_TYPE_SUPER_LONG = 4

run_type = RUN_TYPE_SUPER_LONG

# Number of articles to read. 
NUM_TO_READ = 2 if (run_type < 2 or run_type == RUN_TYPE_SUPER_LONG) else 5
# Number of articles to show without meme distrctions
NUM_ARTICLES_WITHOUT_MEMES = 0 if run_type < 2 else 3
TO_MEME_OR_NOT_TO_MEME = [0, 0] if (run_type < 2 or run_type == RUN_TYPE_SUPER_LONG) else [0, 1, 0, 1, 0, 1]
SHOW_INTRO = True if run_type == RUN_TYPE_START else False

# Articles paths
START_ARTICLES_PATH = "./articles start"
SHORT_ARTICLES_PATH = "./articles short"
LONG_ARTICLES_PATH = "./articles long"
SUPER_LONG_ARTICLES_PATH = "./articles super_long"

if run_type == RUN_TYPE_SHORT: 
    articles_path = SHORT_ARTICLES_PATH
elif run_type == RUN_TYPE_LONG: 
    articles_path = LONG_ARTICLES_PATH
elif run_type == RUN_TYPE_SUPER_LONG: 
    articles_path = SUPER_LONG_ARTICLES_PATH
else :
    articles_path = START_ARTICLES_PATH


## BELOW SHOULD BE IDENTICAL to file in DATA Analysis

NUM_SECONDS_BEFORE_MEME = 0
POSITIVE_POINTS_MEMES_ONLY = False
CALIBRATE_EYE = True

NUM_SECONDS_SHOW_MEME = 2
NUM_SECONDS_HIDE_MEME_INCREMENT = 0

# Strings
introductionText = "MyND: MyNeuroDetector"

calibrationText = "Calibration stage \n\nFollow the instructions that pop up, while keeping head as still as possible." 
lookHereText = "Look Here\ncount to 1\nthen Press Space"
blinkText = "Blink twice\n\nthen Press Space"
closeEyeText = "Close your eyes for 5 secs\n\nthen Press Space"
openEyeText = "Stare there --> <-- for 5 secs\nthen Press Space"
relaxText = "Relax for at least 5 secs\n\nthen Press Space"


instructionsText1 = "Task:\n\n"+\
    "Gain as many points as possible by identifying the words that contain the target letters.\n\n"+\
    "There will be " + str(NUM_TO_READ) + " groups of words / articles for you to process in this session. Each article has their own target letters. All words will appear in the center of the screen. \n\n"+\
    "Please carefully review the controls and point system next."


instructionsText2 = "Controls:\n"+\
    "> Press 'space' to identify a word as having at least one target letter\n> Press 'm' to display the target letters again \n\n"+\
    "Points:\n"+\
    "+1 if identified correctly: \n > Pressed 'space' when a word with target letter is shown.\n\n-1 if identified incorrectly:\n > Missed a word with target letter\n > Pressed 'space' when there are no target letters in word"


instructionsText3 = "Extra Tips: \n\n"+\
    "> There may be some distractors that appear, you may do whatever you want with them as long as you complete your task.\n\n"+\
    "> There will be a leaderboard shown at the end!\n\n"+\
    "Ready? A list of letters for you to memorize will appear next."


# PsychoPy Positioning
MEME_OPACITY = 0.3
image_pos = (0.3, 0)
image_pos_2 = (-0.75, 0)
word_pos = (-0.4, 0)
points_pos = (0, 0.3)
PERCENT_SHOW = 0.5#0.8 # Percentage of time the text should be shown in TimedTextWithSpaceExit

RAND_SECS_LOWERBOUND = 0.7#0.9 # min Number of seconds to display the word for
RAND_SECS_STARTBOUND = 1.0#1.2 # starting number of seconds to display word for

SCALE_FACTOR_EEG = (4500000)/24/(2**23-1) #uV/count
SCALE_FACTOR_AUX = 0.002 / (2**4)

# Num prev to include in performance
MAX_PREV_TO_INCLUDE = 10

# For eye tracking calibration
LEFT_X_COORD = -0.7
RIGHT_X_COORD = 0.7
TOP_Y_COORD = -0.45
BOTTOM_Y_COORD = 0.45

# Markers
SINGLETON_SECTIONS = {"psychopy", "calibration", "instruction", "blink", "openEye", "closeEye", "relax"}
ARTICLE_SECTIONS = {"memorization", "response"}
SINGLE_LABELS = {"lettersShown", "newWord", "endWord", "blank", "newMeme", "memeShown", "memeHidden", "newArticle", "spacePressed", "spaceNotPressed", "targetWord", "notTargetWord"}
RESPONSE_LABELS = {"correct", "incorrect"}

SINGLETON_SECTIONS_MARKERS = {}
for section in SINGLETON_SECTIONS :
    SINGLETON_SECTIONS_MARKERS[section+"Start"] = "--"+section.capitalize()+"Start"
    SINGLETON_SECTIONS_MARKERS[section+"Stop"] = "--"+section.capitalize()+"Stop"

ARTICLE_SECTIONS_MARKERS = {}
for section in ARTICLE_SECTIONS :
    ARTICLE_SECTIONS_MARKERS[section+"Start"] = "--"+section.capitalize()+"Start"
    ARTICLE_SECTIONS_MARKERS[section+"Stop"] = "--"+section.capitalize()+"Stop"

SINGLE_LABELS_MARKERS = {}
for label in SINGLE_LABELS :
    SINGLE_LABELS_MARKERS[label] = "--"+label[0].capitalize()+label[1:]

RESPONSE_LABELS_MARKERS = {}
for label in RESPONSE_LABELS :
    RESPONSE_LABELS_MARKERS[label] = "--"+label.capitalize()+"Response"

PSYCHO_PY_MARKERS = {}
PSYCHO_PY_MARKERS.update(SINGLETON_SECTIONS_MARKERS)
PSYCHO_PY_MARKERS.update(ARTICLE_SECTIONS_MARKERS)
PSYCHO_PY_MARKERS.update(SINGLE_LABELS_MARKERS)
PSYCHO_PY_MARKERS.update(RESPONSE_LABELS_MARKERS)