# 🌹 FortunAI — Miss Fortune Coach  

*Champion-specific AI coaching for League of Legends players*  
By **Zewdi H.** — Riot × AWS Hackathon 2025 Submission  

---

## 🚀 Overview  

**FortunAI** is champion-specific AI coaching assistant for League of Legends players, starting with Miss Fortune as the first supported champion.

It is not just an AI that talks like Miss Fortune, it is an analytical coaching tool built for Miss Fortune mains that helps players understand their gameplay, make smarter decisions, and master her mechanics through tailored insights.
Rather than a simple stat tracker, it acts as a coaching persona that deeply understands the champion herself, her tone, her playstyle, and her gameplay goals.

The system’s logic and phrasing were carefully curated to reflect Miss Fortune’s personality while teaching players how to optimize her strengths and fix common weaknesses.

In the long run, the vision is to grow FortunaAI into a full network of champion-specific AI mentors, each with its own personality and analytical style.
For example, Lux Librarian for support mages, Lee Sin Sensei for mechanical junglers, and Thresh Tactician for macro-heavy supports!

---

## 🎮 Demo  

- **Live App URL:** _Coming soon 
- **Demo Video:** _Coming soon 
---

## 🧠 Methodology Write-Up  

### **How the Coaching Agent Works**

**FortunaAI** has been carefully curated and designed to understand Miss Fortune’s playstyle, key metrics, and common pitfalls, offering actionable insights to help players improve their mastery of the champion. We begin by analyzing her key components.

1. **Data Retrieval**  
   The system uses the **Riot Games API** to collect recent match histories filtered for Miss Fortune games. To balance performance and cost, the API is intentionally capped at retrieving the **most recent 25 matches** per summoner. This keeps analysis fast and stable while still providing enough data for consistent, meaningful feedback.

2. **Champion-Specific Analysis Layer**  
   Each match is analyzed in Python to extract Miss Fortune–relevant features that define how well the player is leveraging her lane dominance and early power spikes.  
   The agent’s backend logic focuses on metrics that truly matter for Miss Fortune gameplay, including:

   - **CS @ 10 Minutes:**  
     Since Miss Fortune is an early lane-dominant ADC who spikes quickly with items such as *Eclipse* or *Kraken Slayer*, her creep score at 10 minutes is a vital early indicator of performance.A low CS@10 signals missed gold opportunities and delays her first item spike, which can completely shift her mid-game power curve.

   - **Deaths Pre-Mythic:**  
     Every death before completing a mythic item delays that crucial first power spike. Tracking pre-mythic deaths highlights poor trades, greedy recalls, or spacing mistakes—core issues for mastering Miss Fortune’s laning and positioning.

   - **Dragon Presence:**  
     Miss Fortune’s ultimate (*Bullet Time*) can decide teamfights at objectives. Measuring dragon fight participation helps assess a player’s macro awareness, rotation timing, and contribution to team objectives.These curated features allow the coach to evaluate not just generic stats, but **the decisions that make or break Miss Fortune’s early-game success.**

3. **Insight Generation (Planned Integration)**  
   The next version of the agent will integrate **Amazon Bedrock** to transform structured match data into narrative coaching feedback.The LLM will interpret the curated features above and generate insights written in Miss Fortune’s tone—teaching players how to adjust their play to hit key milestones faster and die less before major power spikes.While this stage is not yet live, the backend is fully prepared for seamless integration once deployed.

4. **Voice & Presentation Layer (Implemented)**  
   Current feedback is output through **Amazon Polly**, which converts the textual advice into Miss Fortune’s stylized voice.This transforms the data-driven analysis into an immersive coaching experience, letting players hear advice directly from the champion herself.

5. **Deployment & Delivery**  
   The **FastAPI** backend runs on **AWS Lambda** and is exposed publicly via **Amazon API Gateway**.This serverless architecture ensures scalability, low latency, and minimal maintenance while providing a smooth public endpoint for demonstrations and player interaction.

---

### **Approach, Logic, and Observations**

- **Data Sources:** Only the official **Riot Games API** is used. All insights are generated from the summoner’s match history data.  
- **Analytical Focus:** The current logic centers around Miss Fortune’s lane phase and early-mid game performance, with curated metrics (CS@10, deaths pre-mythic, and dragon presence) forming the foundation of her coaching recommendations.  
- **Design Assumptions:** The current version assumes the user is primarily a **Miss Fortune one-trick**. During testing, the API queries accounts whose last 25 games are Miss Fortune to ensure accurate data. Future iterations will include automated champion filtering.  
- **Development Challenges:** Larger data pulls caused stability issues and excessive memory use, leading to the capped 25-match retrieval limit.  
- **Key Insight:** Early CS, death timing before mythic completion, and dragon fight presence most strongly correlate with Miss Fortune’s success, confirming that gameplay awareness around farming, survivability, and objective timing are the biggest areas for improvement.
---

## ⚙️ Tooling (AWS Architecture)

| **AWS Service** | **Purpose** |
|-----------------|-------------|
| **Amazon Polly** | Converts Miss Fortune’s coaching text into lifelike speech. |
| **AWS Lambda** | Executes the FastAPI backend and coordinates Riot API + Polly calls. |
| **Amazon API Gateway** | Public HTTPS endpoint for user requests. |
| **Amazon S3** | (Optional) Cache and store generated audio files. |
| **Amazon Bedrock (Planned)** | Future integration for LLM-based coaching insights. |

The stack is fully **serverless**, minimizing cost and maintenance while scaling automatically.  

---

## 🔑 Environment Variables  

This project uses **two `.env` files** to separate Riot and AWS credentials.  

### 1️⃣ Root Directory `.env`
```env
RIOT_API_KEY=your_riot_api_key_here
RIOT_REGION=na1

### 2️⃣ 'app/.env'
```env
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
