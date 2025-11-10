import random
from collections import deque
from typing import List, Dict, Optional

#File transforms FASTAPI content into MFs personality and voice

_RECENT: Dict[str, deque] = {}

#MFs Voice Library
INTRO_TAGS = [
    "Well, sugar,",
    "Listen up, sweetheart,",
    "Eyes up, gunslinger,",
    "Darlin’,",
    "Here’s the deal, hotshot:",
]

DRILL_PREFIX = [
    "Your next play:",
    "Let’s make it count:",
    "Here’s your target:",
    "Time to show off a little:",
    "Do this for me:",
]

CELEB_TAILS = [
    "Now that’s how you make ‘em pay.",
    "Told ya you had it in you.",
    "Keep that swagger, captain.",
    "That’s a kill worth braggin’ about.",
    "Mmm, music to my ears.",
]

ROASTS = [
    "Quit feedin’ before Mythic, sugar—coins don’t shoot themselves.",
    "You call that positioning? You’re makin’ it too easy for ‘em.",
    "Next time, try dodgin’ before they delete you.",
    "You’re supposed to hit your ult, not just make fireworks.",
    "You keep chasin’ kills like that, and you’ll end up on the wrong bounty poster.",
]

SIGNATURE = "— Miss Fortune 💄"

def _pick(key: str, pool: List[str], k_recent: int = 3) -> str:
    dq = _RECENT.setdefault(key, deque(maxlen=k_recent))
    choices = [x for x in pool if x not in dq] or pool[:]  # if exhausted, allow all
    choice = random.choice(choices)
    dq.append(choice)
    return choice

def mf_voice_adapter(report: Dict, features: Optional[Dict] = None) -> Dict:
    out = dict(report)
    cs10 = float(features.get("avg_cs10", 0)) if features else None
    dpm = int(features.get("avg_deaths_pre_mythic", 0)) if features else None
    drag = float(features.get("avg_dragon_presence", 0)) if features else None
    improvement = features.get("biggest_improvement")
    weakness = features.get("persistent_weakness")

    if cs10 is not None:
        if cs10 < 7.5:
            early = "Your CS is still shaky—time to hit the practice tool, sugar."
        elif cs10 < 8.5:
            early = "Not bad on the CS, but don’t miss cannon gold!"
        else:
            early = "You’ve mastered the lane—your early game’s lookin’ sharp."
    else:
        early = "I see you climbin’, just clean up those last-hits a bit more."

    if dpm is not None:
        if dpm > 1.5:
            mid = "Too many deaths early, darlin’. Play safer till you’ve got power."
        else:
            mid = "You’re stayin’ alive and spikin’ strong—smart play."
    else:
        mid = "Careful’s not cowardly. You last longer, you deal more."

    if drag is not None:
        if drag < 50:
            vision = "You missed some crucial dragons—time to fix that map awareness."
        else:
            vision = "Dragon calls? You showed up. That’s how games are won."
    else:
        vision = "Objectives win games—stay close when they spawn."


    summary = f"{_pick('intro', INTRO_TAGS)} Over the season, your biggest gain was in {improvement}. But watch out — you're still slippin’ with {weakness}."
    celebration = f"You kept at it all year, and it shows. {_pick('celeb', CELEB_TAILS)}"
    roast = f"{_pick('intro', INTRO_TAGS)} Still got work to do on that {weakness}. {_pick('roast', ROASTS)}"

    out["early_game"] = early
    out["mid_game"] = mid
    out["vision"] = vision
    out["summary"] = summary
    out["celebration"] = celebration
    out["roast"] = roast
    out["signature"] = SIGNATURE
    return out
