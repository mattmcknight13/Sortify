# GA Capstone: Sortify

Aziz Maredia | DSIR-1019 | 01.27.2021

## Problem Statement

Nothing beats discovering a new artist or song you love. To make this discovery process easier, Spotify offers personalized playlists such as discover weekly and release radar which make recommendations based on what similar users are listening to, songs of related artists to a user's favorites, or songs that are hot/anticipated new releases.

While these playlists are great, one feature Spotify lacks is the ability to predict and share how likely a user will love or hate an album they naturally come across. Many users like myself don’t have the patience to listen to a full album because we know we aren’t going to love every song. We would rather know and listen to the 4-5 songs we will like and save ourselves 30 minutes.

Here is where Sortify comes. We analyze the audio features and characteristics of songs in your Saved/‘Liked’ library to rank the songs in any album you search, helping you find the music you love, faster.

Any album, sorted to match your taste.

## Executive Summary

Built for Spotify users and powered by the Spotify API, Sority works by first pulling a users saved tracks and the tracks for an album the user inputs. Using track and artist IDs, additional audio features and characterics related to the tracks and their artists are pulled.

Once the data is cleaned, scaled, and dummified wherever appropriate, Princpal Component Analysis is applied to the data to reduce demensionality. After a K-Means Clustering Model is then used to group similar songs together, with different values of k (n-clusters) between 3-12 tested. The k value with the highest silhouette score is used in the final model to sort the album searched.

The cosine similarity between the the album's tracks and the cluster centers are then calculated, with the cluster with the highest average cosine similarity being chosen to the sort the album by in decsending order of cosine similarity scores.

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

|Feature|Type|Description|
|---|---|---|
|**acousticness**|*float*|A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.|
|**danceability**|*float*|Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.|
|**energy**|*float*|Represents a perceptual measure of intensity and activity on a scale from 0.0 to 1.0. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.|
|**instrumentalness**|*float*|Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.|
|**liveness**|*float*|Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.|
|**loudness**|*float*|The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values range between -60 and 0 db.|
|**speechiness**|*float*|Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.|
|**valence**|*float*|A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).|
|**tempo**|*float*|The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.|
|**key**|*object*|The estimated overall key of the track. Integers map to pitches using standard Pitch Class notation . E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.|
|**mode**|*object*|Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.|
|**time_signature**|*object*|An estimated overall time signature of a track. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure).|
|**genre**|*object*|A conventional category that identifies an artist's music as belonging to a shared tradition or set of conventions. E.g. Rap, Indie, House|
|**popularity_artist**|*float*|Score between 0-100 calculated by Spotify that is based, in the most part, on the total number of plays an artist has had and how recent those plays are.|
|**popularity_song**|*float*|Score between 0-100 calculated by Spotify that is based, in the most part, on the total number of plays the track has had and how recent those plays are.|

## Data Cleaning and Preprocessing

Alot of the numeric audio features collected are on a 0-1 scale with the exception of Loudness and Tempo. Because Loudness is on a scale of -60 to 0, this feature is divided by 60 then multiplied by -1 to be brought down to a 0-1 scale. For tempo, a MinMax Scaler was used to bring this variable down to scale as the variable was not orignally on any specific scale. Song and artist Popularity Scores were on a 0-100 scale so these variables were divided by 100 to be brought down to scale.

Track release dates come in the format of YYYY-MM-DD. These dates are cleaned to only show the year so that they can be transformed into a categorial values depending on the decade the track was released (e.g. 1976 --> '70s'). After, this new categorical variable along with Key and Time Signature are converted to dummy/binary variables.  

For artist Genre variable, there is alot of variation in the name of genres. For example, one rap artist might be labeled as 'Rap', and another rap artist might be labeled as 'New York City Rap'. If we were to dummify the variable, this would mean 2 different columns are created even though they are technically the same genre. To fix this, a function was created to clean the variable so that genre names were simplified. In the example just mentioned, 'New York City Rap' would become 'Rap'. Additionally, very unique genres most likely not shared by many other artists were removed from the data. Example of this include "New Wave" and "Big Room".

## Principal Component Analysis

After the data is cleaned, appropriatley scaled, and categorial variables converted into dummy variable, the data could comprise of 40-80 features (maybe more). This depends on the variety of music the user listens to too and how many dummy columns were created for the genre, time signature, and key variables. For my personal library, the data consisted of 66 features after the cleaning and preprocessing.

Due to the high number of features, there is a good chance that many of our features when combined together are acutally unimportant. Because of this we use Principal Component Analysis (PCA) to perform dimensionality reduction on our data. This allows us to still reduce the number of features in our model but keep the most important pieces of the original features.

The number of components/features needed with PCA depends on the user. This is determined by fitting PCA with 0 zero components as the parameter on our data, then looking at the cumulative sum of the explained variance of the components. Because of diminishing returns, the rate at which our cumulative sum increases decreases as the number of components gets larger. The number of components choosen is determined by finding the first number where the cumulative sum increases by less then 0.025.

## K-Means Clustering Modeling and Recommender System

To build a user profile, a KMeans unsupervised learning model is built using our PCA data to cluster/group together similar songs in a user's library together. The number of clusters is determined by testing values of k (n_clusters) between 3 and 12 and finding which number produces the highest silhouette score. The max possible value for k in the test range was selected using roughly the number of music genres repesented on [Musicmap](https://musicmap.info/).

After finding our optimal model/value of k, we calculate the cosine similarity between each of the songs in the album the user searched and the coordinates of the cluster centers. From there we calculate the average cosine similartiy of the songs and choose the cluster with the highest average. This means we are using the cluster/songs most similar to our album to sort our songs.

Our album is then sorted is descending order by cosine similarity to the chosen cluster. At the top are songs on the album the recommender system believes the users will like, and at the bottom are the songs which are believed to not be liked.

## Future Developments

There are many parts of this project I would like to continue working on to improve it:

1. Add Lyrics: I think it would be interesting to collect song lyrics which could be vectorized to add words/phrases as features. One limitation my current model has is that it is basing recommendations mostly off of audio/sound features, however, for many music lovers lyrics play an important role of determine whether they like a song or not. Furthermore, a sentiment analysis could also be performed on the lyrics and the scores could be added as features, helping us determine a users perferences for emotions displayed in songs.

2. Conduct User Surveys: First off, I'd like to see how good the application is at predicting songs on album that the user would like. I'd have them listen to an album on a platform other than Spotify, rank the songs on the album, then compare the ranking to the ouput of the application. From there, I'd want to test out different values for the number of PCA components and number of clusters (k) and see if tuning those paramaters is able to better match the applications song ranking to the users song ranking.

3. Sort Other Things: It would be great to add other capabilites to this application such as allowing the user to search an artist and have 20-30 of their songs sorted based off of the users saved tracks, or maybe have the user search for playlists and have the songs within sorted.

4. Disliked Songs: Currently, we are making the assumption that because a song is saved to a user library, then the user likes the song. It would be helpful to find ways to track songs that users dislike to help build a more robust user profile.

## Final Conclusions and Summary

This has been a very fun project as I was able apply my data science knowledge to my passion for music, while also working to solve a personal problem I have when trying to discover new music. Using this application, a Spotify user can input an album and see the ranking of an album’s songs based on their listening history, helping users find the music they love faster. Any album, sorted to match their taste.