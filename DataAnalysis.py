import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly_express as px

cid = 'Your credentials here.'
secret = 'Your credentials here.'
redirect_uri = 'http://localhost:7777/callback.'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def makeTable(playlist):
    track_ids = [track['track']['id'] for track in playlist['items'] if track['track'] is not None]     # Extract track IDs
    
    # Initialize lists to store track features
    track_names = []
    artists = []
    popularity = []
    audio_features = []

    # Extract track information
    for track in playlist['items']:
        if track['track'] is not None:
            track_names.append(track['track']['name'])
            artists.append(track['track']['artists'][0]['name'])
            popularity.append(track['track']['popularity'])
            track_id = track['track']['id']
            audio_features.append(sp.audio_features([track_id])[0])

    # Create DataFrame
    df = pd.DataFrame({
        'Track Name': track_names,
        'Artist': artists,
        'Popularity': popularity,
        'Acousticness': [af['acousticness'] for af in audio_features],
        'Danceability': [af['danceability'] for af in audio_features],
        'Energy': [af['energy'] for af in audio_features],
        'Instrumentalness': [af['instrumentalness'] for af in audio_features],
        'Liveness': [af['liveness'] for af in audio_features],
        'Speechiness': [af['speechiness'] for af in audio_features],
        'Valence': [af['valence'] for af in audio_features],
        'Tempo': [af['tempo'] for af in audio_features]
    })
    
    df.index = df.index + 1

    return df


def makeHeatMap(df):
    # Make heatmap from provided df
    heatmap_data = df[['Acousticness', 'Danceability', 'Energy', 'Instrumentalness', 'Speechiness', 'Valence', 'Tempo']]

    # Create heatmap
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(heatmap_data.corr(), dtype=bool))
    sns.heatmap(heatmap_data.corr(), annot=True, fmt=".2f", cmap="PiYG", linewidths=0.5, mask=mask)


def makeHistDict(df):
    # Make dictionary of audio features with separate histograms
    features = ['Acousticness', 'Danceability', 'Energy', 'Instrumentalness', 'Speechiness', 'Valence', 'Tempo']
    hists = {}

    for feature in features:
        fig = px.histogram(df, x=feature, title=f'Distribution of {feature.capitalize()} in Top 50 Songs', hover_data={'Track Name': True},\
            labels={'x': feature.capitalize()}, color_discrete_sequence=['#2B9A45'], nbins=20)
        fig.update_layout(
            font=dict(family='Monospace', size=12),      # Set font style and size
            margin=dict(l=80, r=80, t=80, b=80),     # Add margins
        )
        hists[feature] = fig
    
    return hists


# **********************************
# STREAMLIT PAGE 
st.set_page_config(page_title="Emily's Spotify Playlist Analysis", layout="wide")

# SIDEBAR KEY
with st.sidebar:
    st.header("Key for Audio Features")
    st.write("**Acousticness**: describes how acoustic a song is. A score of 1.0 means the song is most likely to be an acoustic one")
    st.write("**Danceability**: describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity")
    st.write("**Energy**: represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy")
    st.write("**Instrumentalness**: predicts whether a track contains no vocals. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content")
    st.write("**Speechiness**: detects the presence of spoken words in a track. Values between 0.33 and 0.66 may contain both music and speech including such cases as rap music. Values below 0.33 most likely represent music")
    st.write("**Valence**: describes the musical positiveness conveyed by a track. High valence tracks sound more positive (e.g. happy, cheerful, euphoric) while tracks with low valence sound more negative (e.g. sad, depressed, angry)")
    st.write("**Tempo**: the overall estimated tempo of a track in beats per minute (BPM)")


# HEADER SECTION AND DASHBOARD
with st.container():
    st.subheader("Spotify Data Analysis")
    st.write("""For my data analysis project, I used the Spotify API to measure different types of musical features present 
            in different songs and compare these elements across different ("Top 50") playlists. I was interested in seeing how
            the prevalence/levels of these features varied across different cultures, countries, and decades""")

    # map playlists to their spotify IDs
    playlist_dict = {
        "Billboard Hot 100": sp.playlist_tracks('spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'),
        "RapCaviar": sp.playlist_tracks('spotify:playlist:37i9dQZF1DX0XUsuxWHRQd'),
        "Top 50 Japan": sp.playlist_tracks('spotify:playlist:37i9dQZEVXbKXQ4mDTEBXq'),
        "Top 50 Brazil": sp.playlist_tracks('spotify:playlist:37i9dQZEVXbMXbN3EUUhlg'),
        "All out 70s": sp.playlist_tracks('spotify:playlist:37i9dQZF1DWTJ7xPn4vNaz')
    }

    playlist_selection = ["Billboard Hot 100", "RapCaviar", "Top 50 Japan", "Top 50 Brazil", "All out 70s"]
    selected_playlist = st.selectbox("Select a Playlist", list(playlist_dict.keys()), key="playlist_selectbox")

    df = makeTable(playlist_dict[selected_playlist])


# GRAPHS
with st.container():
    # create two columns for charts
    left_graph, right_graph = st.columns(2)

    # density heatmap of audio features
    with left_graph:
        st.write("Density Heatmap")
        ax = makeHeatMap(df)
        st.pyplot(ax)
        st.set_option('deprecation.showPyplotGlobalUse', False)

    # histogram of audio features
    with right_graph:
        st.write("Audio Feature Trends")
        feature_selection = ['Acousticness', 'Danceability', 'Energy', 'Instrumentalness', 'Speechiness', 'Valence', 'Tempo']
        feature_select = st.selectbox("Select an Audio Feature", feature_selection, key="audio_feature_selectbox")
        histDict = makeHistDict(df)
        if feature_select in histDict:
            # Display the selected histogram from the dictionary
            st.plotly_chart(histDict[feature_select])
        else:
            st.write(f"No histogram available for the selected feature: {feature_select}")


# DETAILED DATA VIEW
with st.container():
    st.dataframe(df, use_container_width=True)
