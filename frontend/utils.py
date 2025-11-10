import boto3
import os
import streamlit as st
from io import BytesIO
from botocore.exceptions import NoCredentialsError, ClientError e
from frontend.utils import speak_polly


def speak_polly(text: str):
    try:
        polly = boto3.client(
            "polly",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
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
