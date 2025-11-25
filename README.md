# 🎬 MovieMate: Casual Movie Recommender (Streamlit + Gemini)
An interactive Streamlit chatbot that recommends movies from a local dataset using Google Gemini (via LangChain).

**Purpose**: Help users find a movie by genre, actor/director, runtime, year and IMDB votes — via a friendly conversational UI.

# How it Looks
<img width="729" height="387" alt="image" src="https://github.com/larsyarafina/movies_recommendation_chatbot/blob/main/movies_chatbot.png" />
<img width="729" height="387" alt="image" src="https://github.com/larsyarafina/movies_recommendation_chatbot/blob/main/romance_movies.png" />


# 💡 GenAI, LLMs, LangChain 
* What is GenAI?
Generative AI (GenAI) refers to models that can generate text, images, audio, or other content given a prompt. Gemini (by Google) is a family of GenAI models optimized for conversational text generation.

* What is an LLM?
A Large Language Model (LLM) is a neural network trained on massive text data that can generate coherent text, answer questions, and follow instructions. Examples: GPT, Gemini.

* What is LangChain?
LangChain is a library that helps connect LLMs to external data, orchestrate prompts, manage system/human messages, build chains and retrieval-augmented generation (RAG). It simplifies:
- Prompt templates
- Message handling
- Integration with vector stores (FAISS, Pinecone)
- Agents & tool use

In this project: LangChain provides a unified interface to call Gemini (ChatGoogleGenerativeAI) and standardize messages.

# 🔎 Project demo 
MovieMate is a conversational recommender built with Streamlit and LangChain (Google Gemini), where users tell the bot about the movies they're looking for, with specific genre, actor, vibe, or rating. The bot will give a short Gemini-generated blurb plus a ranked list of matching movies from movies.csv, including title, year, runtime, synopsis, stars, IMDB votes. The bot remembers preferences across turns (conversation memory), therefore follow-up refinements combine filters naturally.

## ⚙️ Tech stack
* Frontend / deployment: Streamlit
* Conversational LLM: Google Gemini (via langchain_google_genai)
* Orchestration/abstraction: LangChain (light usage for consistent chat messages)
* Data: movies.csv
* Language: Python 3.10+

## 🧭 How to use (example prompts)
* “Recommend me some thrillers.”
* “I want something funny with Jim Carrey.”
* “What genres are there?”
* Follow-ups combine: “Make it under 120 minutes” or “Only movies that released 2010+”

## 🧩 Dataset (movies.csv)
* TITLE (string) → saved as title in code
* GENRE (comma-separated string) → genre
* ONE-LINE (string) → synopsis
* RunTime (string or number) → duration_min (cleaned to minutes)
* STARS (comma-separated string: actors, director) → stars
* YEAR (string/number; may contain ranges like "(2018–2020)") → year (cleaned)
* VOTES (optional numeric string) → imdb_votes

The app cleans Year and RunTime at load time to avoid parsing errors by extracts 4-digit year, extracts minute digits, and optionally convert 2h10m to 130 minutes if extended parsing added.

# 📄 Code walkthrough (key functions & logic)
## Conversation memory (Streamlit)
st.session_state stores:
* messages — chat history to render as st.chat_message()
* genres — accumulated genre preferences
* stars — accumulated actor/director preferences

Each user message updates these memory lists; subsequent recommendations use the accumulated filters. Sidebar offers a Reset preferences button to clear session_state.

## UI
* Uses st.chat_message() to render messages.st.chat_input() to capture user text.
* Sidebar has Gemini key input, recommend count slider, and reset button.

After creating a recommendation list, the app asks Gemini for a short casual blurb and displays it before the structured list.

# 💡 Prompt design and LangChain usage
* A short SystemMessage sets assistant behavior: casual, friendly, concise.
* The human prompt includes the selected movie items (title/year/runtime/IMDB votes/synopsis/stars) and asks Gemini to produce a 2–3 sentence blurb plus brief one-line descriptions.
* LangChain is used here mainly for consistent message schema (SystemMessage/HumanMessage).
