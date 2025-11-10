import os, json, boto3

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
brt = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

def mf_bedrock_summary(stats: dict, report: dict) -> str:
    prompt = f"""
    You are Miss Fortune from League of Legends — confident, witty, and playful, but always sharp.
    Speak directly to the player as if reviewing their 2025 ranked season.
    Focus on reflection and motivation, not just stats.

    Here are their performance highlights:
    - CS@10: {stats['avg_cs10']}
    - Deaths before Mythic: {stats['avg_deaths_pre_mythic']}
    - Dragon presence: {stats['avg_dragon_presence']}%
    - Biggest improvement: {stats['biggest_improvement']}
    - Persistent weakness: {stats['persistent_weakness']}

    Write a short recap (3–5 sentences) that includes:
    1. One compliment about progress or consistency
    2. One lighthearted roast about what still needs work
    3. One motivational line that fits Miss Fortune’s tone (sassy, confident, encouraging)

    Keep it concise, fun, and naturally written — no lists, just one flowing paragraph.
    """

    body = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    resp = brt.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
    data = json.loads(resp["body"].read())


    text = data["content"][0]["text"]
    text = text.replace("—", " - ")  # removes AI-sounding em dashes
    text = text.replace("–", "-")  # (optional) catches short dashes too
    text = text.strip()

    return text
