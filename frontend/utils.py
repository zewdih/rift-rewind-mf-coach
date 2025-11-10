import boto3
import streamlit as st
from io import BytesIO

def speak_polly(text: str):
    polly = boto3.client("polly")
    response = polly.synthesize_speech(
        Text=text,
        VoiceId="Joanna",
        OutputFormat="mp3"
    )
    audio_bytes = response["AudioStream"].read()
    st.audio(BytesIO(audio_bytes), format="audio/mp3")
