from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta

import asyncio
import os
import requests
import json

from db.redis import RedisDB


async def get_subscription_id(id: str, redis: RedisDB):
    """
    Retrieve the user's subscription ID from Redis
    If one does not exist, return None.
    """
    return await redis.get(id)


def verify_subscription(subscription_id: str):
    """
    Verify the subscription using Nano Repeat
    """
    verify_data = {
        "subscription_id": subscription_id
    }
    json_data = json.dumps(verify_data)
    r = requests.post(f"{os.getenv('API_ENDPOINT')}verify?token={os.getenv('NR_TOKEN')}", json_data)
    return r.json()


async def send_alert(user_id: str, content: str):
    """
    Alert the user that their subscription is expiring tomorrow.
    """
    message_content = {'content': f'{content}'}
    m = requests.post(
        f"https://discord.com/api/users/@me/channels",
        headers={'Authorization': f'Bot {os.getenv("TOKEN")}'},
        json={'recipient_id': f'{user_id}'}
    )
    channel_response = json.loads(m.text)
    m = requests.post (
        f"https://discord.com/api/channels/{channel_response['id']}/messages",
        headers={'Authorization': f'Bot {os.getenv("TOKEN")}'},
        json=message_content
    )


async def manage_roles(user_id: int, username: str, roles: list, subscription_json: dict):
    """
    Add or remove the subscription role based on the status of the subscription
    """
    
    if 'active' in subscription_json and subscription_json['active']:
        expiration_date = subscription_json['expiration_date']
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.now()
        comp = timedelta(days=1)
        if (expiration_date - now) < comp:
            print(f"{datetime.now()}: User {username}'s subscription is expiring tomorrow - sending reminder.")
            content = 'Oh no, your subscription for The Nano Center is going to expire tomorrow!  Send a !renew command to get information on how to renew.'
            await send_alert(user_id, content)
        if not os.getenv('ROLE_ID') in roles:
            r = requests.put(
                f'https://discord.com/api/guilds/{os.getenv("GUILD_ID")}/members/{user_id}/roles/{os.getenv("ROLE_ID")}',
                headers={'Authorization': f'Bot {os.getenv("TOKEN")}'}
            )
    elif os.getenv('ROLE_ID') in roles:
        print(f"{datetime.now()}: Removing role from {username}")
        r = requests.delete(
            f'https://discord.com/api/guilds/{os.getenv("GUILD_ID")}/members/{user_id}/roles/{os.getenv("ROLE_ID")}',
            headers={'Authorization': f'Bot {os.getenv("TOKEN")}'}
        )


def get_members_list():
    """
    Pull the full list of members to the guild
    """
    member_list = []
    while len(member_list) % 1000 == 0:
        after = f'&after={member_list[len(member_list) - 1]}' if len(member_list) > 0 else ''
        print(after)
        r = requests.get(
            f'https://discord.com/api/guilds/{os.getenv("GUILD_ID")}/members?limit=1000{after}',
            headers={'Authorization': f'Bot {os.getenv("TOKEN")}'}
        )
        for member in r.json():
            member_list.append(member)
    return member_list



async def main():
    redis = await RedisDB.create()
    members = get_members_list()
    for member in members:
        if 'user' in member:
            subscription_id = await get_subscription_id(member['user']['id'], redis)
            print(subscription_id)
            if subscription_id is not None:
                subscription_json = verify_subscription(subscription_id)
                await manage_roles(member['user']['id'], member['user']['username'], member['roles'], subscription_json)

    await redis.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()