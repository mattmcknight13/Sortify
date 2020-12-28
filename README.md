# GA Capstone Project Outline

What is your problem statement? What will you actually be doing?
- I plan to build some sort of music recommender app using the Spotify API

- Problem: Building a recommender system which tells you which songs on an album you will like based on your top tracks, recently played music, and last 50 songs saved. Will help people identiy which songs on an album to listen to, rather then listening to the whole album to figure out which songs they like.

- User inputs an album or playlist and the app would return which songs on the album the user would like in order based on the audio features of there most recently played songs/top played songs.

Who is your audience? Why will they care?
- Either anyone with a Spotify account or anyone for loves music!

What is your success metric? How will you know if you are actually solving the problem in a useful way?
- It seems like recommender systems and unsuperviseds models don't actually have real success metrics.
- Need to discuss this more with instructors

What is your data source? What format is your data in? How much cleaning and munging will be required?
- Spotify API
- API endpoints return JSON metadata

- Will need to pull data from 4-5 different endpoints

    - Get a users top tracks: https://developer.spotify.com/documentation/web-api/reference/personalization/get-users-top-artists-and-tracks/
    - Get a users recently played tracks: https://developer.spotify.com/documentation/web-api/reference/player/get-recently-played/
    - Get a User's Saved Tracks: https://developer.spotify.com/documentation/web-api/reference/library/get-users-saved-tracks/
    - Get an albums tracks: https://developer.spotify.com/console/get-album-tracks/
    - Get audio features for a track: https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/

- Fair amount of cleaning will be needed to get only the columns needed

What are potential challenges or obstacles and how will you mitigate them?
- Figuring out how a user will be able to connect their Spotify account to the app. Need to figure out how the authorizations work
- Figuring out how I will pull data in real-time because every user is different and has different liked songs
- Still need to learn about recommender systems.
- Not sure if I will have enough data to effectively make recommendations.

Is this a reasonable project given the time constraints that you have?
- I believe this is reason project given the time contraints, but will need to discuss more with instructors.

