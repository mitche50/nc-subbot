from dotenv import load_dotenv
load_dotenv()
from datetime import datetime

import discord
import os
import requests
import json

from db.redis import RedisDB

client = discord.Client()

async def get_subscription_id(user: discord.User, redis: RedisDB):
    """
    Retrieve the user's subscription ID from Redis
    If one does not exist, return None.
    """
    return await redis.get(user.id)


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


async def manage_roles(user_id: int, subscription_json: dict):
    """
    Add or remove the subscription role based on the status of the subscription
    """
    guild = client.get_guild(int(os.getenv('GUILD_ID')))
    member = guild.get_member(user_id)
    role = discord.utils.get(guild.roles, name=os.getenv("ROLE_NAME"))
    if 'active' in subscription_json and subscription_json['active']:
        await member.add_roles(role)
    else:
        await member.remove_roles(role, reason="Subscription no longer active.")


@client.event
async def on_ready():
    redis = await RedisDB.create()
    guild = client.get_guild(int(os.getenv('GUILD_ID')))
    member_list = guild.members
    print(f"{datetime.now()}: {member_list}")
    for member in member_list:
        subscription_id = await get_subscription_id(member, redis)
        if subscription_id is not None:
            subscription_json = verify_subscription(subscription_id)
            print(f"{datetime.now()}: {subscription_json}")
            await manage_roles(member.id, subscription_json)
    await redis.close()
    await client.close()


client.run(os.getenv("TOKEN"))