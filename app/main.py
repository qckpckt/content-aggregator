#! /usr/bin/env python3

import random
import notification
import keychain
import os
import requests


AUTH_URL = 'https://www.reddit.com/api/v1/access_token'
BASE_URL = 'https://oauth.reddit.com'
BASE_OUTPUT_URL = 'reddit://www.reddit.com'
REDDIT_USERNAME = 'qckpckt'
REDDIT_CLIENT_ID = '34DJnXRByNr8UA'  # client id of script installed on my reddit account.
REDDIT_USER_PASSWORD = keychain.get_password('reddit.com', REDDIT_USERNAME)
REDDIT_CLIENT_PASSWORD = keychain.get_password('reddit.com', REDDIT_CLIENT_ID)
USER_AGENT = 'AlexContentAggregatorAligator'

def get_access_token(url=AUTH_URL):
    auth = (REDDIT_CLIENT_ID, REDDIT_CLIENT_PASSWORD)
    headers = {'User-Agent': USER_AGENT}
    body = {
        'grant_type': 'password',
        'username': REDDIT_USERNAME,
        'password': REDDIT_USER_PASSWORD
    }
    response = requests.post(url, auth=auth, headers=headers, data=body).json()
    return response['access_token']


def get_hot(subreddit, access_token, base_url=BASE_URL):
    formatted_url = f'{base_url}/r/{subreddit}/hot'
    params = {
        'g': 'GLOBAL',
        'limit': 10
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': USER_AGENT
    }
    response = requests.get(
        formatted_url,
        headers=headers,
        params=params).json()
    return response['data']['children']


def parse_post(post):
    if post['stickied']:
        print(f'"{post["title"]}" is a stickied post. Skipping...')
        return
    return {
        'Title': post['title'],
        'Link': f'{BASE_OUTPUT_URL}{post["permalink"]}',
        'Created_At': post['created_utc'],
    }


def transform(posts):
    parsed = [parse_post(post['data']) for post in posts]
    return [post for post in parsed if post]


def create_notification(transformed, subreddit):
    lucky_number = random.randint(0, (len(transformed) - 1))
    post = transformed[lucky_number]
    title = f'Here is a random hot post from /r{subreddit}: {post["Title"]}'
    notification.schedule(
        title,
        0,
        '',
        post['Link'])


def main():
    print('getting access token')
    access_token = get_access_token()
    subreddit = 'guitarpedals'
    print(f'getting hot posts from /r/{subreddit}')
    posts = get_hot(subreddit, access_token)
    transformed = transform(posts)
    create_notification(transformed, subreddit)


if __name__ == '__main__':
    main()
