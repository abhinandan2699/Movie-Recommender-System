import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load external CSS file
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply the CSS
load_css("style.css")

# Title and UI
st.title('🍿 Movie Recommender System')
st.markdown("### Get tailored movie recommendations based on your favorites! 🎬")

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

# Function to fetch poster from TMDB API
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6d55c4781af5599db440d30d82ee47f0"
    )
    data = response.json()
    if 'poster_path' in data and data['poster_path']:
        return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
    return "https://via.placeholder.com/500x750?text=No+Image+Available"

# Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_overview = []
    for i in movies_list:
        movie_id = i[0]
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movies.iloc[i[0]].movie_id))
        recommended_movies_overview.append(movies.iloc[i[0]].original_overview)

    return recommended_movies, recommended_movies_posters, recommended_movies_overview

# Button to get recommendations
if st.button('Get Recommendations', key='recommend-btn'):
    # Display spinner during processing
    with st.spinner('Fetching movie recommendations...'):
        names, posters, overview = recommend(selected_movie_name)

    # Display movie recommendations
    cols = st.columns(5, gap="large")
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <p class="movie-title">{names[i]}</p>
                    <div>
                        <a href="#popup-{i}">
                            <button class="view-button">View</button>
                        </a>
                    </div>
                </div>
                <div id="popup-{i}" class="popup">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <p style="font-size: 20px; font-weight: bold; color: black;">{names[i]}</p>
                    <p class="movie-title">Rating: 6/10</p>
                    <p style="font-size:16px; color:gray;">{overview[i]}.</p>
                    <a href="#">
                        <button class="close-btn">Close</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
