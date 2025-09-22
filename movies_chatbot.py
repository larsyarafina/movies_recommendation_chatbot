import streamlit as st
import pandas as pd
import random
from typing import List, Optional

# import gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage


# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("movies.csv")
    df = df.rename(columns={
        "MOVIES": "title",
        "GENRE": "genre",
        "ONE-LINE": "synopsis",
        "RunTime": "duration_min",
        "STARS": "stars",
        "YEAR": "year",
        "VOTES": "imdb_votes"
    })

    # clean duration
    df["duration_min"] = (
        df["duration_min"]
        .astype(str)
        .str.extract(r"(\d+)")      # get only digits
        .astype(float)
    )

    # 🟢 Clean imdb_votes: if exists
    if "imdb_votes" in df.columns:
        df["imdb_votes"] = pd.to_numeric(df["imdb_votes"], errors="coerce")

    # 🟢 Clean year: extract first 4-digit year, works for (2018–2020), etc.
    df["year"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")    # find first 4-digit number
        .astype(float)
    )
    return df

df = load_data()


def normalize_genre(g: str):
    return [x.strip().lower() for x in str(g).split(",") if x.strip()]

def recommend(df, genres: List[str], star_keywords: List[str], topk: int = 5):
    d = df.copy()

    # filter by genres
    if genres:
        d["genre_score"] = d["genre"].apply(
            lambda x: sum(1 for g in genres if g in normalize_genre(x))
        )
        d = d[d["genre_score"] > 0]

    # filter by actors/directors
    if star_keywords:
        d = d[d["stars"].str.lower().str.contains("|".join(star_keywords), na=False)]

    # ranking
    if "genre_score" in d.columns:
        d = d.sort_values(["genre_score", "imdb_votes"], ascending=[False, False])
    else:
        d = d.sort_values("imdb_votes", ascending=False)

    return d.head(topk).reset_index(drop=True)

def llm_bubble(prompt: str, api_key: Optional[str] = None):
    if not api_key:
        return random.choice([
            "Here are some great picks 🎬",
            "Nice — I’ve got some movies you might enjoy!",
            "Check these out, they’re trending and match your vibe!"
        ])
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
        )
        system = SystemMessage(content="You are a casual, friendly movie recommendation assistant. Keep answers short, helpful, and upbeat.")
        human = HumanMessage(content=prompt)
        resp = llm([system, human])
        return resp.content
    except Exception as e:
        return f"Error reaching Gemini: {e}"

# Streamlit UI

st.set_page_config(page_title="MovieMate 🎬", layout="wide")
st.title("🎬 MovieMate — Movie Recommender")

with st.sidebar:
    gemini_key = st.text_input("Gemini API Key", type="password")
    topk = st.slider("How many movies to recommend", 1, 10, 5)
    if st.button("Reset preferences"):
        st.session_state.genres = []
        st.session_state.stars = []
        st.session_state.messages = [
            {"role": "assistant", "text": "hi! 👋 Preferences cleared. What kind of movie do you want now?"}
        ]
        st.rerun()

# conversation state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"assistant", "text":"hi! 👋 Looking for action, romance, or maybe a movie with your favorite actor? Just ask!"}
    ]
if "genres" not in st.session_state:
    st.session_state.genres = []
if "stars" not in st.session_state:
    st.session_state.stars = []

# show chat history
for m in st.session_state.messages:
    if m["role"] == "user":
        st.chat_message("user").write(m["text"])
    else:
        st.chat_message("assistant").write(m["text"])

user_msg = st.chat_input("Say something...")

if user_msg:
    st.session_state.messages.append({"role":"user", "text": user_msg})
    low = user_msg.lower()

    # show available genres
    if "genres" in low:
        genres_list = ", ".join(sorted({g.strip() for g in ", ".join(df["genre"].dropna().tolist()).split(",")}))
        reply = f"Here are some genres: {genres_list}. Which one sounds good?"
        st.session_state.messages.append({"role":"assistant","text":reply})
        st.rerun()

    # detect genres mentioned
    genres_all = sorted({g for gg in df["genre"].dropna().str.split(",") for g in gg})
    for g in genres_all:
        if g.strip().lower() in low and g.strip().lower() not in st.session_state.genres:
            st.session_state.genres.append(g.strip().lower())

    # detect actors/directors mentioned
    all_stars = set()
    for val in df["stars"].dropna():
        for s in str(val).split(","):
            all_stars.add(s.strip().lower())
    for s in all_stars:
        if s in low and s not in st.session_state.stars:
            st.session_state.stars.append(s)

    # recommend movies
    recs = recommend(
        df,
        genres=st.session_state.genres,
        star_keywords=st.session_state.stars,
        topk=topk,
    )

    if recs.empty:
        st.session_state.messages.append(
            {"role":"assistant","text":"Hmm, nothing matches. Want me to relax the filters?"}
        )
        st.rerun()

    # Build recommendation text
    lines = []
    for _, row in recs.iterrows():
        desc = f"**{row['title']}** ({int(row['year']) if pd.notna(row['year']) else 'Unknown'}) — {int(row['duration_min']) if pd.notna(row['duration_min']) else '?'} min\n"
        desc += f"🎭 Genre: {row['genre']}\n"
        desc += f"⭐ Stars/Director: {row['stars']}\n"
        desc += f"📝 {row['synopsis']}\n"
        if pd.notna(row['imdb_votes']):
            desc += f"📊 IMDB Votes: {int(row['imdb_votes'])}\n"
        lines.append(desc)

    list_text = "\n\n".join(lines)
    prompt = f"User asked for movie recommendations. Suggest in a casual tone. Movies:\n{list_text}"
    blurb = llm_bubble(prompt, api_key=gemini_key)

    st.session_state.messages.append({"role":"assistant","text":blurb + "\n\n" + list_text})
    st.rerun()
