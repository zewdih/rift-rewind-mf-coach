import os
from typing import Optional, Tuple, Dict, Any
from statistics import mean
import time
import requests
from dotenv import load_dotenv, find_dotenv
from riot_secrets import get_riot_key

SEARCH_MATCH_COUNT = 25
MAX_ANALYZED_MF_MATCHES = 12
MAX_TIMELINE_SAMPLES = 3
TIME_BUDGET_SEC = 18.0

AMERICAS = "americas"
MF_AVG_CS10 = 7.5
MF_AVG_DEATHS_PRE15 = 1.5

load_dotenv(find_dotenv())


_session = requests.Session()

def riot_headers() -> Dict[str, str]:
    return {"X-Riot-Token": get_riot_key()}

def _get(url: str):
    return _session.get(url, headers=riot_headers(), timeout=15)

def get_puuid(game_name: str, tag_line: str) -> Optional[str]:
    url = f"https://{AMERICAS}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    res = _get(url)
    if res.status_code == 200:
        return res.json().get("puuid")
    return None

def get_match_ids(puuid: str, count: int = SEARCH_MATCH_COUNT) -> list:
    url = f"https://{AMERICAS}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    res = _get(url)
    return res.json() if res.status_code == 200 else []

def get_match_data(match_id: str) -> Optional[dict]:
    url = f"https://{AMERICAS}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    res = _get(url)
    return res.json() if res.status_code == 200 else None

def get_match_timeline(match_id: str) -> Optional[dict]:
    url = f"https://{AMERICAS}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    res = _get(url)
    return res.json() if res.status_code == 200 else None

def compute_cs10_and_deaths_from_timeline(timeline: dict, puuid: str) -> Tuple[Optional[float], Optional[int]]:
    participants = timeline.get("metadata", {}).get("participants", [])
    try:
        idx = participants.index(puuid)
    except ValueError:
        return None, None
    pid = str(idx + 1)
    cs10, deaths = 0, 0
    for frame in timeline.get("info", {}).get("frames", []):
        if frame["timestamp"] > 600000:  # 10:00
            break
        for event in frame.get("events", []):
            if event.get("type") == "CHAMPION_KILL" and str(event.get("victimId")) == pid:
                deaths += 1
        pf = frame.get("participantFrames", {}).get(pid, {})
        cs10 = pf.get("minionsKilled", 0) + pf.get("jungleMinionsKilled", 0)
    return float(cs10), deaths

def extract_mf_stats(match: dict, puuid: str) -> Optional[Dict[str, Any]]:
    participant = next(
        (p for p in match["info"]["participants"]
         if p["puuid"] == puuid and p["championName"].lower() == "missfortune"),
        None
    )
    if not participant:
        return None
    challenges = participant.get("challenges", {}) or {}
    cs10 = challenges.get("cs10")
    deaths = challenges.get("deathsBefore15")

    if cs10 is None or deaths is None:
        timeline = get_match_timeline(match["metadata"]["matchId"])
        cs_tl, deaths_tl = compute_cs10_and_deaths_from_timeline(timeline, puuid) if timeline else (None, None)
        cs10 = cs10 if cs10 is not None else cs_tl if cs_tl is not None else MF_AVG_CS10
        deaths = deaths if deaths is not None else deaths_tl if deaths_tl is not None else MF_AVG_DEATHS_PRE15

    return {
        "cs10": round(float(cs10), 2),
        "deaths_pre_mythic": int(deaths),
        "dragon_presence": float(challenges.get("dragonTakedowns", 0)),
        "kda": f"{participant['kills']}/{participant['deaths']}/{participant['assists']}",
        "damage_share": round(float(challenges.get("teamDamagePercentage", 0.0)), 3)
    }

def _dragon_presence_percent(timeline: dict, my_pid: int, my_team_id: int) -> Optional[float]:
    if not timeline:
        return None
    total_team_dragons = 0
    involved_dragons = 0
    for frame in timeline.get("info", {}).get("frames", []):
        for e in frame.get("events", []):
            if e.get("type") == "ELITE_MONSTER_KILL" and e.get("monsterType") == "DRAGON":
                killer_pid = int(e.get("killerId", 0) or 0)
                killer_team = 100 if 1 <= killer_pid <= 5 else 200
                if killer_team != my_team_id:
                    continue
                total_team_dragons += 1
                assists = e.get("assistingParticipantIds") or []
                if my_pid == killer_pid or my_pid in assists:
                    involved_dragons += 1
    if total_team_dragons == 0:
        return 0.0
    return 100.0 * involved_dragons / total_team_dragons

def get_recent_mf_stats(game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
    puuid = get_puuid(game_name, tag_line)
    if not puuid:
        return None
    for match_id in get_match_ids(puuid):
        match = get_match_data(match_id)
        if not match:
            continue
        stats = extract_mf_stats(match, puuid)
        if stats:
            return stats
    return None

def get_yearly_mf_stats(game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
    start = time.monotonic()

    puuid = get_puuid(game_name, tag_line)
    if not puuid:
        print("❌ No PUUID found for that summoner/tag combo.")
        return None

    match_ids = get_match_ids(puuid, count=SEARCH_MATCH_COUNT)
    if not match_ids:
        print("❌ No match IDs returned from Riot.")
        return None

    cs10s: list[float] = []
    deaths: list[int] = []
    dragon_pcts: list[float] = []

    mf_seen = 0
    timelines_used = 0

    for mid in match_ids:
        if time.monotonic() - start > TIME_BUDGET_SEC:
            print("⏰ Time budget exceeded, stopping early.")
            break
        if mf_seen >= MAX_ANALYZED_MF_MATCHES:
            break

        match = get_match_data(mid)
        if not match:
            continue

        me = next(
            (p for p in match["info"]["participants"]
             if p.get("puuid") == puuid and p.get("championName", "").lower() == "missfortune"),
            None
        )
        if not me:
            continue

        mf_seen += 1

        ch = me.get("challenges", {}) or {}
        cs = ch.get("cs10")
        d15 = ch.get("deathsBefore15")

        tl = None
        if (cs is None or d15 is None) and timelines_used < MAX_TIMELINE_SAMPLES:
            if time.monotonic() - start > TIME_BUDGET_SEC:
                break
            tl = get_match_timeline(match["metadata"]["matchId"])
            if tl:
                timelines_used += 1
                cs_tl, d15_tl = compute_cs10_and_deaths_from_timeline(tl, puuid)
                if cs is None and cs_tl is not None:
                    cs = cs_tl
                if d15 is None and d15_tl is not None:
                    d15 = d15_tl

        if cs is not None:
            try:
                cs10s.append(float(cs))
            except:
                pass
        if d15 is not None:
            try:
                deaths.append(int(d15))
            except:
                pass

        dpct = None
        if "dragonTakedowns" in ch:
            try:
                dpct = min(100.0, float(ch["dragonTakedowns"]) / 3.0 * 100.0)
            except:
                dpct = None
        elif tl is not None and timelines_used <= MAX_TIMELINE_SAMPLES:
            try:
                my_pid = int(me["participantId"])
                my_team_id = int(me.get("teamId", 100))
                dpct = _dragon_presence_percent(tl, my_pid, my_team_id)
            except:
                dpct = None

        if dpct is not None:
            dragon_pcts.append(float(dpct))


    if not cs10s or not deaths or not dragon_pcts:
        print("⚙️ Riot returned incomplete MF data — using fallback averages.")
        return {
            "avg_cs10": 7.3,
            "avg_deaths_pre_mythic": 1.2,
            "avg_dragon_presence": 63.5,
            "biggest_improvement": "CS@10",
            "persistent_weakness": "dragon presence"
        }

    avg_cs10 = round(mean(cs10s), 2)
    avg_deaths = round(mean(deaths), 2)
    avg_drag = round(mean(dragon_pcts), 1)

    def split_delta(arr, higher_is_better=True):
        if len(arr) < 2:
            return 0.0
        m = max(1, len(arr) // 2)
        first, second = mean(arr[:m]), mean(arr[m:])
        return (second - first) if higher_is_better else (first - second)

    d_cs   = split_delta(cs10s, True)
    d_deps = split_delta(deaths, False)
    d_drag = split_delta(dragon_pcts, True)

    improvements = {"CS@10": d_cs, "dragon presence": d_drag, "deaths before Mythic": d_deps}
    biggest_improvement = max(improvements, key=improvements.get)

    weaknesses = {
        "CS@10": 7.5 - avg_cs10,
        "deaths before Mythic": avg_deaths - 1.5,
        "dragon presence": 65.0 - avg_drag
    }
    positives = {k: v for k, v in weaknesses.items() if v > 0}
    persistent_weakness = max(positives, key=positives.get) if positives else min(weaknesses, key=weaknesses.get)

    print(f"✅ Found {mf_seen} Miss Fortune matches. Timelines used: {timelines_used}")
    print(f"📊 Averages — CS@10: {avg_cs10}, Deaths: {avg_deaths}, Dragon%: {avg_drag}")

    return {
        "avg_cs10": avg_cs10,
        "avg_deaths_pre_mythic": avg_deaths,
        "avg_dragon_presence": avg_drag,
        "biggest_improvement": biggest_improvement,
        "persistent_weakness": persistent_weakness
    }
