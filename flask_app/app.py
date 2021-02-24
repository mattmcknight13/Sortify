# imports
# import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, request, session, make_response

from math import floor

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
import time

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# initialize the flask app
app = Flask('sortify')
app.secret_key = os.urandom(24)

cid = '01e5c3c39a334ae78bf5becf053ad2d5'
secret = '3c481468946e43dc9da43ed6b5c16bc8'
uri = 'http://127.0.0.1:5000/api_callback'
cache = '.spotipyoauthcache'
scope = 'user-library-read user-read-private'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/submit')
def verify():
    auth = SpotifyOAuth(client_id=cid,
                        client_secret=secret,
                        redirect_uri=uri,
                        cache_path=cache,
                        scope=scope)

    auth_url = auth.get_authorize_url()

    return redirect(auth_url)


@app.route('/api_callback')
def form():
    auth = SpotifyOAuth(client_id=cid,
                        client_secret=secret,
                        redirect_uri=uri,
                        cache_path=cache,
                        scope=scope)

    session.clear()
    code = request.args.get('code')
    token_info = auth.get_access_token(code)

    session["token_info"] = token_info

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    name = sp.current_user()['display_name'].split()[0]

    return render_template("form.html", name=name)


@app.route('/results')
def album_sort():
    user_input = request.args

    sp = access_spotify()

    sorted_album, album_dict = model(user_input['UserInput'], sp)

    sorted_album['duration_ms'] = [f'{str(int(time//60))}:0{str(floor(time % 60))}' if len(str(floor(time % 60)))
                                   == 1 else f'{str(int(time//60))}:{str(floor(time % 60))}' for time in (sorted_album['duration_ms'] * 0.001)]
    sorted_album['index'] = sorted_album['index'] + 1

    sorted_album.rename(columns={
                        'index': 'Index', 'track': 'Track', 'duration_ms': 'Duration'}, inplace=True)

    return render_template("results.html",
                           album_cover=album_dict['album_image'],
                           album_title=album_dict['album_name'],
                           artist_name=album_dict['artist_name'],
                           release_year=album_dict['release_year'],
                           total_tracks=album_dict['total_tracks'],
                           total_time=album_dict['album_duration'],
                           tables=[sorted_album.to_html(index=False)],
                           titles=sorted_album.columns.values)


def model(album, sp):

    # if 'user_tracks' in session:
    #     user_tracks = pd.DataFrame(session['user_tracks'])
    # else:
    #     user_tracks = get_user_tracks_w_audio_features(sp)
    #     session['user_tracks'] = user_tracks.to_dict('dict')

    user_tracks = get_user_tracks_w_audio_features(sp)

    album_tracks, album_final_model, album_info_dict = get_album_tracks(
        album, sp)

    combined_tracks = pd.concat([user_tracks, album_tracks], axis=0)
    combined_tracks.reset_index(drop=True, inplace=True)
    combined_tracks = clean_genres(combined_tracks)
    combined_tracks = clean_data(combined_tracks)

    user_tracks_pca, album_tracks_pca = pca(combined_tracks)
    user_tracks_pca.drop(
        columns=['track', 'artist', 'data_type'], inplace=True)
    album_tracks_pca.drop(
        columns=['track', 'artist', 'data_type'], inplace=True)

    sorted_album = sort_album(
        user_tracks_pca, album_tracks_pca, album_final_model)

    return sorted_album, album_info_dict


def access_spotify():
    auth = SpotifyOAuth(client_id=cid,
                        client_secret=secret,
                        redirect_uri=uri,
                        cache_path=cache,
                        scope=scope)

    session.clear()
    code = request.args.get('code')
    token_info = auth.get_access_token(code)

    session["token_info"] = token_info

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    return spotipy.Spotify(auth=session.get('token_info').get('access_token'))


def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = SpotifyOAuth(client_id=cid,
                                client_secret=secret,
                                redirect_uri=uri,
                                cache_path=cache,
                                scope=scope)

        token_info = sp_oauth.refresh_access_token(
            session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def get_current_saved(sp):

    # set empty variable for dataframe to be assigned to
    df = None

    # set variable to check number of rows in dataframe
    num_rows = 0

    # api can pull max of 20 tracks at a time and a spotify user can have a max of 10,000 songs saved
    for i in range(0, 10000, 20):

        # call api endpoint to collect saved tracks. offset equals index of first song being pull and increases by 20 each interation
        results = sp.current_user_saved_tracks(offset=i)

        # set empty dict for track variables and values collected to be stored in
        current_saved_dict = {}
        current_saved_dict['track'] = [i['track']['name']
                                       for i in results['items']]
        current_saved_dict['artist'] = [
            i['track']['artists'][0]['name'] for i in results['items']]
        current_saved_dict['track_id'] = [i['track']['id']
                                          for i in results['items']]
        current_saved_dict['artist_id'] = [
            i['track']['artists'][0]['id'] for i in results['items']]
        current_saved_dict['release_date'] = [
            i['track']['album']['release_date'] for i in results['items']]
#         current_saved_dict['popularity_song'] = [i['track']['popularity'] for i in results['items']]

        # if first iteration, convert dict to dataframe and save to empty df variable
        # if not, convert dict to dataframe and concat it with dataframe contatining tracks from previous pulls
        if i == 0:
            df = pd.DataFrame(current_saved_dict)
        else:
            df = pd.concat([df, pd.DataFrame(current_saved_dict)])
            df.reset_index(drop=True, inplace=True)

        # if length of dataframe index equals the num_rows variable set above, this means that we have pulled all songs in a user's library
        # if not, update num_rows to current index length
        if len(df.index) == num_rows:
            return df
        else:
            num_rows = len(df.index)

    return df


def get_audio_features(all_tracks_df, sp):

    df = None
    start = 0
    end = 100

    # api can only pull audio features for 100 tracks max
    # calculting how many pulls will be need based on number of tracks in user's saved library
    for i in range((len(all_tracks_df['track_id']) // 100) + 1):

        # XXX
        if i == (len(all_tracks_df['track_id']) // 100):
            results = sp.audio_features(tracks=list(all_tracks_df['track_id'])[
                                        start:len(all_tracks_df['track_id'])])
        else:
            results = sp.audio_features(tracks=list(
                all_tracks_df['track_id'])[start:end])

        # XXX
        audio_dict = {}
        keep_features = ['danceability', 'energy', 'key', 'loudness', 'mode',
                         'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                         'valence', 'tempo', 'id', 'duration_ms', 'time_signature']

        for i in keep_features:
            audio_dict[i] = [x[i] for x in results]

        # if first iteration, convert dict to dataframe and save to empty df variable
        # if not, convert dict to dataframe and concat it with dataframe contatining tracks from previous pulls
        if i == 0:
            df = pd.DataFrame(audio_dict)
        else:
            df = pd.concat([df, pd.DataFrame(audio_dict)])
            df.reset_index(drop=True, inplace=True)

        start += 100
        end += 100

    return df


def get_genres(all_tracks_df, sp):

    df = None
    start = 0
    end = 50

    artists = list((set(list(all_tracks_df['artist_id']))))

    for i in range((len(artists) // 50) + 1):

        if i == (len(artists) // 50):
            results = sp.artists(artists=artists[start:len(artists)])
        else:
            results = sp.artists(artists=artists[start:end])

        audio_dict = {}
        keep_features = ['id', 'genres']  # 'popularity',

        for i in keep_features:
            audio_dict[i] = [x[i] for x in results['artists']]

        if i == 0:
            df = pd.DataFrame(audio_dict)
        else:
            df = pd.concat([df, pd.DataFrame(audio_dict)])
            df.reset_index(drop=True, inplace=True)

        start += 50
        end += 50

    return df


def get_user_tracks_w_audio_features(sp):

    all_tracks_df = get_current_saved(sp)

    audio_features_df = get_audio_features(all_tracks_df, sp)

    df = pd.merge(all_tracks_df, audio_features_df.rename(
        columns={'id': 'track_id'}), on='track_id', how='inner')

    genres_df = get_genres(all_tracks_df, sp)

    df = pd.merge(df, genres_df.rename(
        columns={'id': 'artist_id'}), on='artist_id', how='left')

    df['data_type'] = 'user_library'

    df = df[['track', 'artist', 'track_id', 'data_type',
             'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
             'liveness', 'valence', 'tempo', 'mode', 'key', 'time_signature', 'release_date', 'genres']]  # 'popularity_artist', 'popularity_song'

    return df


def get_album_tracks(album_to_search, sp):

    results = sp.search(album_to_search, 1, 0, 'album', None)
    album_id = results['albums']['items'][0]['id']

    df = None

    results2 = sp.album(album_id)

    album_tracks_dict = {}

    album_tracks_dict['track'] = [i['name']
                                  for i in results2['tracks']['items']]
    album_tracks_dict['track_id'] = [i['id']
                                     for i in results2['tracks']['items']]
    album_tracks_dict['artist'] = [i['artists'][0]['name']
                                   for i in results2['tracks']['items']]
    album_tracks_dict['artist_id'] = [i['artists'][0]['id']
                                      for i in results2['tracks']['items']]
    album_tracks_dict['spotify_link'] = [i['external_urls']
                                         ['spotify'] for i in results2['tracks']['items']]
    album_tracks_dict['preview'] = [i['preview_url']
                                    for i in results2['tracks']['items']]

    df = pd.DataFrame(album_tracks_dict)
    album_dict = {}

    album_dict['album_name'] = results2['name']  # album title
    album_dict['album_image'] = results2['images'][1]['url']  # album coveer
    album_dict['artist_name'] = results2['artists'][0]['name']  # artist name
    album_dict['release_year'] = results2['release_date'][:4]  # release_year
    album_dict['total_tracks'] = results2['total_tracks']  # total tracks
    album_dict['album_link'] = results2['external_urls']['spotify']
    album_dict['artist_link'] = results2['artists'][0]['external_urls']['spotify']

    minutes = sum([i['duration_ms']
                   for i in results2['tracks']['items']]) / 60000

    if minutes > 60:
        album_dict['album_duration'] = f'{int(minutes // 60)} hr {floor(minutes % 60)} min'
    else:
        album_dict['album_duration'] = f'{floor(minutes)} min {floor((minutes - floor(minutes)) * 60)} sec'

    df['release_date'] = results2['release_date']

    df_audio = get_audio_features(df, sp)
    df = pd.merge(df, df_audio.rename(
        columns={'id': 'track_id'}), on='track_id', how='inner')

    df_genres = get_genres(df, sp)
    df = pd.merge(df, df_genres.rename(
        columns={'id': 'artist_id'}), on='artist_id', how='left')

    df['data_type'] = 'album'

    album_final = df[['track', 'track_id',
                      'duration_ms', 'spotify_link', 'preview']]

    df = df[['track', 'track_id', 'artist', 'data_type',
             'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
             'liveness', 'valence', 'tempo', 'mode', 'key', 'time_signature', 'release_date', 'genres']]  # 'popularity_artist', 'popularity_song'

    return df, album_final, album_dict


def clean_genres(df):

    genres = ['folk', 'gothic', 'emo', 'metal', 'rock', 'punk', 'alternative', 'grunge', 'pop', 'hip hop',
              'country', 'bluegrass', 'swing', 'blues', 'jazz', 'gospel', 'soul', 'piano', 'rythm', 'reggae',
              'rap', 'r&b', 'edm', 'dupstep', 'techno', 'house', 'trance', 'electro', 'dance', 'disco',
              'classical', 'singer songwriter', 'musical', 'african', 'hawaiian', 'jam band', 'psychedelic']

    languages = {'asian': ['chinese', 'japanese', 'korean', 'korean pop', 'taiwanese', 'vietnamese', 'malaysian', 'indonesian', 'thai', 'tibetan'],
                 'baltic_slavic': ['croatian', 'czech', 'latvian', 'polish', 'serbian', 'russian', 'lithuanian', 'ukrainian', 'slovenian', 'bulgarian'],
                 'celtic': ['irish', 'scottish', 'celtic'],
                 'english': ['australian', 'uk', 'british', 'canadian'],
                 'germanic': ['german', 'norwegian', 'swedish', 'dutch', 'icelandic', 'austrian', 'danish', 'belgian'],
                 'indian_pakistani': ['indian', 'pakistani', 'punjabi', 'hindustani'],
                 'middle_eastern': ['israeli', 'kurdish', 'hebrew', 'arab', 'turkish'],
                 'romance': ['spanish', 'french', 'italian', 'romanian', 'latin', 'portuguese'],
                 'south_american': ['brazilian', 'venezuelan', 'argentine', 'peruvian', 'chilean'],
                 'uralic': ['finnish', 'estonian', 'hungarian']}

    genres_list = []

    for i in df['genres']:

        temp = []

        for g in genres:
            if g in ' '.join(i):
                temp.append(g)

        for group in languages.keys():
            for l in languages[group]:
                if l in ' '.join(i):
                    temp.append(group)

        if len(temp) == 0:
            temp.append('other')

        genres_list.append(temp)

    df['genres'] = genres_list

    df = pd.concat([df, pd.get_dummies(df['genres'].apply(pd.Series).stack()).sum(
        level=0)], axis=1).drop(columns=['genres'])

    return df


def clean_data(df):

    # bringing the following variables down to a 0-1 scale
    df['loudness'] = (df['loudness'] / 60) * -1  # currently on -60-0 scale

    # tempo is not on a scale so using a minmax scalar to bring it down to a 0-1 scale
    mms = MinMaxScaler()
    df[['tempo']] = mms.fit_transform(df[['tempo']])

    # only need year so removing day and month from release date, then turning it into a
    # categorical variable with values corresponding with the decade the track was released

    df['release_date'] = [int(i[:4]) for i in df['release_date']]
    new_dates = []

    for date in df['release_date']:
        if date < 1950:
            new_dates.append('Pre_50s')
        elif date >= 1950 and date < 1960:
            new_dates.append('50s')
        elif date >= 1960 and date < 1970:
            new_dates.append('60s')
        elif date >= 1970 and date < 1980:
            new_dates.append('70s')
        elif date >= 1980 and date < 1990:
            new_dates.append('80s')
        elif date >= 1990 and date < 2000:
            new_dates.append('90s')
        elif date >= 2000 and date < 2010:
            new_dates.append('2000s')
        elif date >= 2010:
            new_dates.append('Post_2010')
        else:
            new_dates.append('Date not available')

    df['release_date'] = new_dates

    # converting categorical columns into dummy variables
    df = pd.get_dummies(df, columns=['key', 'release_date', 'time_signature'])

    return df


def find_optimal_components(array):

    for i in enumerate(array[:len(array)-1]):
        diff = array[i[0] + 1] - i[1]
        if diff < 0.025:
            return i[0]

    return 8


def pca(df):

    X = df.drop(columns=['track', 'artist', 'track_id', 'data_type'])

    test_pca = PCA().fit(X)
    cumsum_array = np.cumsum(test_pca.explained_variance_ratio_)

    pca = PCA(n_components=find_optimal_components(
        cumsum_array), random_state=42)

    combined_pca = pd.DataFrame(pca.fit_transform(X))
    combined_pca = pd.concat(
        [df[['track', 'artist', 'data_type']], combined_pca], axis=1)

    user_tracks_pca = combined_pca.loc[combined_pca['data_type']
                                       == 'user_library', :].reset_index(drop=True)
    album_tracks_pca = combined_pca.loc[combined_pca['data_type'] == 'album', :].reset_index(
        drop=True)

    return user_tracks_pca, album_tracks_pca


def cluster_user_tracks(df):

    results = {'n_clusters': [], 'silhouette_score': []}

    X = df

    for k in range(3, 17):

        km = KMeans(n_clusters=k, random_state=42)
        km.fit(X)
        ss = silhouette_score(X, km.labels_)

        results['n_clusters'] = results['n_clusters'] + [k]
        results['silhouette_score'] = results['silhouette_score'] + [ss]

    optimal_k = results['n_clusters'][results['silhouette_score'].index(
        max(results['silhouette_score']))]

    km = KMeans(n_clusters=optimal_k, random_state=42)
    best_model = km.fit(X)

    return best_model


def sort_album(user_tracks_pca, album_tracks_pca, album_final_model):

    model = cluster_user_tracks(user_tracks_pca)

    similarity_df = pd.DataFrame(cosine_similarity(
        np.array(album_tracks_pca), model.cluster_centers_))

    song_scores = pd.DataFrame(
        similarity_df[similarity_df.mean().sort_values(ascending=False).index[0]])
    column_name = list(song_scores.columns)[0]

    sorted_album = pd.concat([album_final_model, song_scores], axis=1).sort_values(
        by=column_name, ascending=False)

    return sorted_album[['track', 'duration_ms']].reset_index()


# run the app
if __name__ == '__main__':
    app.run(debug=True)
