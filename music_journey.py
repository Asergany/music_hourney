#!/usr/bin/env python
# coding: utf-8
# __author__ = "Abla Elsergany"

import pandas as pd
import spotipy
import spotipy.util as util
import random
import urllib


SPOTIFY_CLIENT_ID='#'
SPOTIFY_CLIENT_SECRET='#'
SPOTIFY_REDIRECT_URI='http://localhost:8888/callback/'

# the two users add their usernames here. smedjan and wizzler are sample users from the Spotify API
# if you left these sample users, smedjan takes a while to process.
usernames=['smedjan', 'wizzler']


# Spotify authorization
scope = 'playlist-read-private playlist-read-collaborative'


playlists=[]
df_list = []

# setting up the API calls to bring the playlists and artists 
# of each track in the playlist for each user in the loop
for username in usernames:
    print('getting tracks for user ' + username)
    token = util.prompt_for_user_token(username, \
                                        scope, \
                                        SPOTIFY_CLIENT_ID, \
                                        SPOTIFY_CLIENT_SECRET, \
                                        SPOTIFY_REDIRECT_URI)
    df = None # new dataframe for each user
    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            # get tracks of each playlist
            results = sp.playlist(playlist['id'], fields="tracks,next")
            tracks = results['tracks']
            # tracks will be none when there are no more pages to pull
            while tracks is not None:
                for i, item in enumerate(tracks['items']):
                    track = item['track']
                    # because some tracks are null or have no artist 
                    if track is None or track['artists'] is None:
                        continue
                    if df is None:
                        df = pd.DataFrame(track['artists'])
                    else:
                        # add additional row of artist(s) to the dataframe
                        df=df.append(pd.DataFrame(track['artists']))
                tracks = sp.next(tracks)
        # appending this dataframe to the list of dataframes
        df_list.append(df) 
    else:
        print("Can't get token for", username)


top_artists = []

# for loop to loop on the list of dataframes and get the highest 5 occurring artist for each user
for df in df_list:
    artists = df.groupby('name').count()[['id']].sort_values(['id'], ascending=False).head(5)
    artist_names = artists.index.tolist()
    # shuffling those 5 with every run for the sake of variety each time we run the script
    random.shuffle(artist_names)
    fixed_names = []
    for name in artist_names:
        # removing the spaces in the artist names to be safe for use in url
        fixed_names.append(urllib.parse.quote(name))
    top_artists.append(fixed_names)
    print(fixed_names)
    

# looping on the names of top 5 artists for the two users and plugging them into the url 
# from Boil The Frog. When cliked, it will take you to the page where you can see the 
# linking artists path between the two picked artists.
# repeated 5 times for the sake of variety and additional music
for i in range(5):
    url='http://static.echonest.com/BoilTheFrog/?src=' + top_artists[0][i] + '&dest=' + top_artists[1][i]
    print(url)

