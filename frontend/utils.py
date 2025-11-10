import boto3
import streamlit as st
from io import BytesIO

def speak_polly(text: str):
    polly = boto3.client(
        "polly",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets.get("AWS_REGION", "us-east-1")
    )

    response = polly.synthesize_speech(
        Text=text,
        VoiceId="Joanna",
        OutputFormat="mp3"
    )

    audio_bytes = response["AudioStream"].read()
    st.audio(BytesIO(audio_bytes), format="audio/mp3")
