import boto3
import streamlit as st
from io import BytesIO

def speak_polly(text: str):
    try:
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
except NoCredentialsError:
        st.error("⚠️ AWS credentials not found. Check your Streamlit secrets.")
except ClientError as e:
        st.error(f"❌ AWS Polly error: {e.response['Error']['Message']}")
