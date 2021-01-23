# GA Capstone: Sortify

Aziz Maredia | DSIR-1019 | 01.27.2021

## Problem Statement

Nothing beats the feeliing of disovering a new artist, album, or song you love. Music streaming services such as Spotify offer featured playlist such as 'Discover Weekly', where users can find new songs they might like based. While playlists like these help to make discovering new music easier, one feature Spotify lacks is the ability to tell users how likely they will like a song. For example, when new albums are released, many times we might not have the time or patience to listen to the full album, rather, we would simply like to know which songs we will like. This is were Sortify comes in. Sortify uses data science to rank of an album’s songs based on a users listening history, helping them find the music they love faster.

## Data Collection and Dictionary

The data for the alpha version of this project was pulled using the [Spotify Web API](https://developer.spotify.com/documentation/web-api/). More specifically, the [Spotipy Python library](https://spotipy.readthedocs.io/en/2.16.1/) was used to access user and music data from specific API endpoints.

First, a [User Authentication with OAuth 2.0](https://developer.spotify.com/documentation/general/guides/authorization-guide/) workflow is setup so the end user can grant permission to access and/or modify the user’s own data. To get that authorization, a call is generated to the Spotify Accounts Service / authorize endpoint, passing along a list of the scopes for which access permission is sought.

Once the authorization workflow is setup, the users enters an album they would like to search and sort. 5 different API endpoints are used to pull the information needed:

1. [Search for an Item](https://developer.spotify.com/console/get-search-item/): Returns Spotify ID of album searched
2. [Get an Album's Tracks](https://developer.spotify.com/console/get-album-tracks/): Using the ID, returns the album's tracks, track IDs, artist ID, and more
3. [Get Several Tracks](https://developer.spotify.com/console/get-several-tracks/): Using the track IDs, returns the track's popularity scores
4. [Get Audio Features for Several Tracks](https://developer.spotify.com/console/get-audio-features-several-tracks/): Using the track IDs, returns audio features of tracks (e.g. acousticness, tempo)
5. [Get Several Artists](https://developer.spotify.com/console/get-several-artists/): Using the artist ID, returns artist's genres and popularity scores

From there, 3 different endpoints are used to pull a user's saved tracks and various information related to tracks:

1. [Get Current User's Saved Tracks](https://developer.spotify.com/console/get-current-user-saved-tracks/): Returns the user's entire saved library of tracks (10,000 max) including track IDs, artist IDs, and more
2. [Get Audio Features for Several Tracks](https://developer.spotify.com/console/get-audio-features-several-tracks/): Using the track IDs, returns audio features of tracks (e.g. acousticness, tempo)
3. [Get Several Artists](https://developer.spotify.com/console/get-several-artists/): Using the artist IDs, returns artist's genres and popularity scores

## Data Cleaning and Preprocessing

Alot of the numeric audio features collected are on a 0-1 scale with the exception of Loudness and Tempo. Because Loudness is on a scale of -60 to 0, this feature is divided by 60 then multiplied by -1 to be brought down to a 0-1 scale. For tempo, a MinMax Scaler was used to bring this variable down to scale as the variable. Song and artist Popularity Scores were on a 0-100 scale so these variables were divided by 100 to be brought down to scale.

Track release dates come in the format of YYYY-MM-DD. These dates are cleaned to only show the year so that they can be transformed into a categorial values depending on the decade the track was released (e.g. 1976 --> '70s'). After, this new categorical variable along with Key and Time Signature are converted to dummy/binary variables.  

For artist Genre variable, there is alot of variation in the name of genres. For example, one rap artist might be labeled as 'Rap', and another rap artist might be labeled as 'New York City Rap'. If we were to dummify the variable, this would mean 2 different columns are created even though they are technically the same genre. To fix this, a function was created to clean the variable so that genre names were simplified. For example, 'Rap' 

## Principal Component Analysis

After the data is cleaned, appropriatley scaled, and categorial variables converted into dummy variable, the data could comprise of 40-80 features (maybe more). This depends on the variety of music the user listens to too and how many dummy columns were created for the genre, time signature, and key variables. For my personal library, the data consisted of 66 features after the cleaning and preprocessing.

Due to the high number of features, there is a good chance that many of our features when combined together are acutally unimportant. Because of this we use Principal Component Analysis (PCA) to perform dimensionality reduction on our data. This allows us to still reduce the number of features in our model but keep the most important pieces of the original features.

The number of components/features needed with PCA depends on the user. This is determined by fitting PCA with 0 zero components as the parameter on our data, then looking at the cumulative sum of the explained variance of the components. Because of diminishing returns, the rate at which our cumulative sum increases decreases as the number of components gets larger. The number of components choosen is determined by finding the first number where the cumulative sum increases by less then 0.025.

## K-Means Clustering Modeling and Recommender System

To build a user profile, a KMeans unsupervised learning model is built using our PCA data to cluster/group together similar songs in a user's library together. The number of clusters is determined by testing values of k (n_clusters) between 3 and 12 and finding which number produces the highest silhouette_score.

After finding our optimal model/value of k, we calculate the cosine similarity between each of the songs in the album the user searched and the coordinates of the cluster centers. From there we calculate the average cosine similartiy of the songs and choose the cluster with the highest average. This means we are using the cluster/songs most similar to our album to sort our songs.

Our album is then sorted is descending order by cosine similarity to the chosen cluster. At the top are songs on the album the recommender system believes the users will like, and at the bottom are the songs which are believed to not be liked.

## Future Developments

There are many parts of this project I would like to continue working on to improve it:

1. Add Lyrics: I think it would be interesting to collect song lyrics which could be vectorized to add words/phrases as features. One limitation my current model has is that it is basing recommendations mostly off of audio/sound features, however, for many music lovers lyrics play an important role of determine whether they like a song or not. Furthermore, a sentiment analysis could also be performed on the lyrics and the scores could be added as features, helping us determine a users perferences for emotions displayed in songs.

2. Conduct User Surveys: First off, I'd like to see how good the application is at predicting songs on album that the user would like. I'd have them listen to an album on a platform other than Spotify, rank the songs on the album, then compare the ranking to the ouput of the application. From there, I'd want to test out different values for the number of PCA components and number of clusters (k) and see if tuning those paramaters is able to better match the applications song ranking to the users song ranking.

3. Sort Other Things: It would be great to add other capabilites to this application such as allowing the user to search an artist and have 20-30 of their songs sorted based off of the users saved tracks, or maybe have the user search for playlists and have the songs within sorted.  

## Final Conclusions and Summary

This has been a very fun project as I was able apply my data science knowledge to my passion for music, while also working to solve a personal problem I have when trying to discover new music. Using this application, a Spotify user can input an album and see the ranking of an album’s songs based on their listening history, helping users find the music they love faster. Any album, sorted to match their taste.