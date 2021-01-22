# GA Capstone: Sortify

Aziz Maredia | DSIR-1019 | 01.27.2021

## Problem Statement

Nothing beats the feeliing of disovering a new artist, album, or song you love. Music streaming services such as Spotify offer featured playlist such as 'Discover Weekly', where users can find new songs they might like based. While playlists like these help to make discovering new music easier, one feature Spotify lacks is the ability to tell users how likely they will like a song. For example, when new albums are released, many times we might not have the time or patience to listen to the full album, rather, we would simply like to know which songs we will like.  


This is were, Sortify comes in. 

## Project Directory

## Executive Summary

## Data Collection and Dictionary

The data for the alpha version of this project was pulled using the [Spotify Web API](https://developer.spotify.com/documentation/web-api/). More specifically, the [Spotipy Python library](https://spotipy.readthedocs.io/en/2.16.1/) was used to access user and music data from specific API endpoints.

First, a [User Authentication with OAuth 2.0](https://developer.spotify.com/documentation/general/guides/authorization-guide/) workflow is setup so the end user can grant permission to access and/or modify the user’s own data. To get that authorization, a call is generated to the Spotify Accounts Service / authorize endpoint, passing along a list of the scopes for which access permission is sought.

Once the authorization workflow is setup, the users enters an album they would like to search and sort. 5 different API endpoints are used to pull the information needed.

1. [Search for an Item](https://developer.spotify.com/console/get-search-item/): Returns Spotify ID of album searched
2. [Get an Album's Tracks](https://developer.spotify.com/console/get-album-tracks/): Using the ID, returns the album's tracks, track IDs, artist ID, and more
3. [Get Several Tracks](https://developer.spotify.com/console/get-several-tracks/): Using the track IDs, returns the track's popularity scores
4. [Get Audio Features for Several Tracks](https://developer.spotify.com/console/get-audio-features-several-tracks/): Using the track IDs, returns audio features of tracks (e.g. acousticness, tempo)
5. [Get Several Artists](https://developer.spotify.com/console/get-several-artists/): Using the artist ID, returns artist's genres and popularity scores

From there, 3 different endpoints are used to pull a user's saved tracks and various information related to tracks:

1. [Get Current User's Saved Tracks](https://developer.spotify.com/console/get-current-user-saved-tracks/): Returns the user's entire saved library of tracks (10,000 max) including track IDs, artist IDs, and more
2. [Get Audio Features for Several Tracks](https://developer.spotify.com/console/get-audio-features-several-tracks/): Using the track IDs, returns audio features of tracks (e.g. acousticness, tempo)
3. [Get Several Artists](https://developer.spotify.com/console/get-several-artists/): Using the artist IDs, returns artist's genres and popularity scores


### Data Cleaning

Most data

Popularity Scores
Loudness

Min max scaler: tempo

Release Date --> show only year

Dummys --> 'key', 'release_date', 'time_signature'

Genre's 

## Data Processing and PCA


### K-Means Clustering Modeling

## Recommender System



## Future Developments


## Final Conclusions and Summary
