import os
import boto3
from functools import lru_cache


@lru_cache
def get_riot_key():
    ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-1"))

    name = os.getenv("RIOT_API_KEY_PARAM", "/rift-rewind/riot-key")
    resp = ssm.get_parameter(Name=name, WithDecryption=True)

    return resp["Parameter"]["Value"]