import streamlit as st
import pickle
import requests
import time

# Load similarity matrix and movies DataFrame
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_df = pickle.load(open("movies.pkl", "rb"))

# TMDB API Authorization
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NDRkMjQwZjFjMjM0ZDQ3MDg2MmRjMDkzOTIzZjRlZCIsIm5iZiI6MTc0NzMxMzkwMy4yNzcsInN1YiI6IjY4MjVlNGVmMjBkNjA4NTBlYzBhODE2MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.e71owoiXHNnTWaOGQWMfXHgJYxtpJKijXPhOxxLfFRI",
    "accept": "application/json"
}


def fetch_poster(movie_id, retries=3, backoff=2):
    """
    Fetch movie poster URL from TMDB API.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    for attempt in range(retries):
        try:
            res = requests.get(url, headers=headers, timeout=5)
            res.raise_for_status()
            data = res.json()
            poster_path = data.get("poster_path")
            print("DEBUG:", movie_id, "poster_path:", poster_path)
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(backoff)
    return "https://via.placeholder.com/500x750?text=No+Image"


def recommend(movie):
    """
    Recommend top 5 similar movies.
    """
    movie_index = movies_df[movies_df["title"] == movie].index[0]
    distances = similarity[movie_index]
    movie_scores = sorted(
        enumerate(distances),
        key=lambda x: x[1],
        reverse=True
    )[1:6]  # Skip the movie itself

    recommended_titles = []
    recommended_posters = []

    for i in movie_scores:
        movie_row = movies_df.iloc[i[0]]
        movie_id = movie_row.movie_id
        recommended_titles.append(movie_row.title)
        poster_url = fetch_poster(movie_id)
        recommended_posters.append(poster_url)
        # Sleep to avoid hitting rate limits
        time.sleep(2)

    return recommended_titles, recommended_posters


# Streamlit App UI
st.title("🎬 Movie Recommendation System")

movie_titles = movies_df["title"].values

selected_movie = st.selectbox(
    "Select a movie you like:",
    movie_titles
)

if st.button("Recommend"):
    recommendations, posters = recommend(selected_movie)
    st.write("## 🎥 Recommended Movies")
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(recommendations[idx])
            st.image(posters[idx])
