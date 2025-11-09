import streamlit as st
from vertexai.preview.generative_models import GenerativeModel
import vertexai
import requests

PROJECT_ID = "sonorous-crane-477702-s2"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("text-bison@001")

def lookup_player_id(player_name):
    """Look up a player ID on balldontlie by name"""
    res = requests.get(f"https://www.balldontlie.io/api/v1/players?search={player_name}")
    data = res.json().get("data", [])
    if data:
        return data[0]["id"], f"{data[0]['first_name']} {data[0]['last_name']}"
    return None, None

def get_season_averages(player_id, season=2023):
    """Get season averages for a player"""
    res = requests.get(
        f"https://www.balldontlie.io/api/v1/season_averages?season={season}&player_ids[]={player_id}"
    )
    data = res.json().get("data", [])
    if data:
        return data[0]
    return None

def fetch_player_stats(player_name):
    """Get full stats dict for a player"""
    player_id, full_name = lookup_player_id(player_name)
    if player_id is None:
        return None, None
    stats = get_season_averages(player_id)
    return full_name, stats

st.set_page_config(page_title="SmartPicks - AI Sports Agent", page_icon="🏀")
st.title("🏀 SmartPicks")
st.write("Ask your AI sports analyst anything about player performance or predictions.")

query = st.text_input("Enter your question (e.g. 'How many assists will LeBron James get tonight?')")

top_players = ["LeBron James", "Stephen Curry", "Nikola Jokic", "Luka Doncic", "Giannis Antetokounmpo", "Deandre Ayton"]

if st.button("Ask AI") and query:
    st.info("Checking query for player names and fetching stats...")
    
    player_found = None
    for player in top_players:
        if player.lower() in query.lower():
            player_found = player
            break

    players_stats = {}
    if player_found:
        full_name, stats = fetch_player_stats(player_found)
        if stats:
            players_stats[full_name] = {
                "points": stats.get("pts", 0),
                "rebounds": stats.get("reb", 0),
                "assists": stats.get("ast", 0)
            }
        else:
            st.warning(f"Could not fetch stats for {player_found}.")
    else:
        import random
        selected = random.sample(top_players, 3)
        for player in selected:
            full_name, stats = fetch_player_stats(player)
            if stats:
                players_stats[full_name] = {
                    "points": stats.get("pts", 0),
                    "rebounds": stats.get("reb", 0),
                    "assists": stats.get("ast", 0)
                }

    if not players_stats:
        st.error("No player stats found. Try a different query.")
    else:
        prompt = f"""
You are an expert sports analyst. Use the following player stats to answer the user's question.

Player Data:
{players_stats}

Question: {query}

Respond with:
1. Short analysis (2-3 sentences)
2. A final recommendation: the top player for this query.
"""

        # 4. Generate response
        with st.spinner("Analyzing stats with AI..."):
            try:
                response = model.generate_content(prompt)
                st.success("✅ SmartPicks Recommendation")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating response: {e}")

# -----------------------------
# 4. Optional: Add a simple "Generate Visual"
# -----------------------------
if st.button("Generate Visual Summary (Bonus)"):
    st.info("This feature could use Imagen 3 or Gemini Flash Image to generate visuals.")
    st.write("🖼️ Example: A dynamic stat card showing top player performance.")
