import streamlit as st
import pickle
import pandas as pd
import requests


# Function to load data from files
def load_data():
    """
    Load movies data and similarity matrix from pickled files.
    """
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    return movies, similarity


# Function to apply external CSS for styling
def load_css(file_path):
    """
    Load and apply external CSS from a file.
    """
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Function to fetch movie poster using TMDB API
def fetch_poster(movie_id):
    """
    Fetch movie poster using TMDB API.
    """
    api_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6d55c4781af5599db440d30d82ee47f0"
    response = requests.get(api_url)
    data = response.json()
    return (
        f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        if 'poster_path' in data and data['poster_path']
        else "https://via.placeholder.com/500x750?text=No+Image+Available"
    )


# Function to generate movie recommendations
def recommend(movie, movies, similarity):
    """
    Generate top 5 movie recommendations based on similarity matrix.
    """
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommendations = []
    posters = []
    overviews = []
    ratings = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommendations.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        overviews.append(movies.iloc[i[0]].original_overview)
        ratings.append(movies.iloc[i[0]].vote_average)

    return recommendations, posters, overviews, ratings


# Function to display movie recommendations
def display_recommendations(names, posters, overviews, ratings):
    """
    Display recommended movies with details in a styled format.
    """
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
                <div id="popup-{i}" class="popup" id="movie-popup">
                    <a href="#">
                        <button class="close-btn-top-right" onclick="document.getElementById('movie-popup').style.display='none'">&times;</button>
                    </a>
                    <img src="{posters[i]}" alt="{names[i]}">
                    <p style="font-size: 20px; font-weight: bold; color: black;">{names[i]}</p>
                    <p class="movie-title">Rating: {ratings[i]}/10</p>
                    <p style="font-size:16px; color:gray;">{overviews[i]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


# Main app logic
def main():
    """
    Main function to orchestrate the Movie Recommender System.
    """
    # Load data and apply styles
    movies, similarity = load_data()
    load_css("style.css")

    # Display app title and description
    st.markdown('<h1 class="custom-title">Find Your Next Favorite Film</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="custom-title">Let us suggest movies you will absolutely love!</h3>', unsafe_allow_html=True)

    # Input: Select movie
    selected_movie_name = st.selectbox(
        'Start by selecting a film you like:', movies['title'].values
    )

    # Button to get recommendations
    if st.button('See Related Films', key='recommend-btn'):
        # Show spinner while processing
        with st.spinner('Hang tight! Your next favorite movies are on the way...'):
            names, posters, overviews, ratings = recommend(selected_movie_name, movies, similarity)

        # Display recommendations
        display_recommendations(names, posters, overviews, ratings)


# Run the app
if __name__ == "__main__":
    main()
