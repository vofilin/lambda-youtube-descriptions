import os
import logging
import boto3
from apiclient.discovery import build

# Youtube API parameters
API_KEY = os.environ.get('API_KEY')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CHANNEL_ID = os.environ.get('CHANNEL_ID')
DYNAMO_URL = os.environ.get('DYNAMO_URL')
DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Get video descriptions from the channel
def get_video_descriptions(api_key, channel_id):

    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # creating Youtube Resource Object
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=api_key)

    ch_request = youtube.channels().list(
        part='contentDetails', id=channel_id)

    # Channel Information
    ch_response = ch_request.execute()
    playlist_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    nextPageToken = ""
    video_ids = []
    while nextPageToken is not None:
        ch_request = youtube.playlistItems().list(part='id, snippet', playlistId=playlist_id,
                                                  maxResults=50, pageToken=nextPageToken)
        ch_response = ch_request.execute()
        for item in ch_response['items']:
            video_ids.append({'id': item['id'], 'title': item['snippet']
                             ['title'], 'description': item['snippet']['description']})
        nextPageToken = ch_response['nextPageToken'] if 'nextPageToken' in ch_response else None

    return video_ids


# Put descriptions into dynamo table
def load_descriptions(videos, dynamo_url, dynamo_table):
    dynamodb = boto3.resource(
        'dynamodb', endpoint_url=dynamo_url)

    table = dynamodb.Table(dynamo_table)
    for video in videos:
        table.put_item(Item=video)


def lambda_handler(event, context):
    logger.info(f'Event: {event}')
    videos = get_video_descriptions(API_KEY, CHANNEL_ID)
    load_descriptions(videos[50:75], DYNAMO_URL, DYNAMO_TABLE)
    return videos
