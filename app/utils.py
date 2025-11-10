import boto3
import base64
import os

import boto3
import base64
import os

def speak_polly(text: str) -> str:
    polly = boto3.client("polly", region_name="us-east-1")

    response = polly.synthesize_speech(
        Text=text,
        VoiceId="Joanna",
        OutputFormat="mp3"
    )

    audio_stream = response.get("AudioStream")
    if not audio_stream:
        raise Exception("No AudioStream returned by Polly")

    audio_bytes = audio_stream.read()
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return audio_b64

def make_drills(cs10: float, deaths_pre_mythic: int, dragon_presence: float):
    drills = []


    if cs10 < 7.5:
        drills.append("Hit 8.0 CS@10 in 2 of your next 3 games.")
    if deaths_pre_mythic > 1:
        drills.append("No isolated fights before Mythic; cap early deaths at 1.")
    if dragon_presence < 65:
        drills.append("Be present for the next 3 dragons; ward 45s before.")
    while len(drills) < 3:
        drills.append("Buy 2 control wards by 12:00 and keep one for objectives.")
    return drills
