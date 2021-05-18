# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


import googleapiclient.discovery
import googleapiclient.errors
import re

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
api_service_name = "youtube"
api_version = 'v3'


def get_youtube_data(id=None):
    if not id:
        return None
    creds = None

    # token.pickle зберігає необходні дані під час першої авторизації
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # якщо дійсних даних авторизації нема, користувачеві треба пройти авторизацію
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds)

    request = youtube.videos().list(
        part="snippet, contentDetails",
        id=id

    )
    response = request.execute()['items'][0]

    return{'id': response['id'],
            'title': response['snippet']['title'],
            'date': response['snippet']['publishedAt'],
            'tags': ', '.join(response['snippet']['tags']),
            'author': response['snippet']['channelTitle'],
            'duration': response['contentDetails']['duration']}


def get_youtube_by_link(link):
    res = re.findall(r'watch\?v=(\w*)', link)
    return get_youtube_data(id=res[0])


if __name__ == "__main__":
    print(get_youtube_by_link("https://www.youtube.com/watch?v=yNE36O06JSE"))