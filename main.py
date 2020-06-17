from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import io
import discord
import json
import pyqrcode
import requests
from discord.ext.commands import Bot
from db.redis import RedisDB
from decimal import Decimal

client = Bot(command_prefix=os.getenv("PREFIX"))
client.remove_command("help")

async def get_subscription_id(user: discord.User, redis: RedisDB):
    """
    Retrieve the user's subscription ID from Redis
    If one does not exist, return None.
    """
    return await redis.get(user.id)


async def create_subscription(user: int, redis: RedisDB):
    """
    Create a new subscription using Nano Repeat
    """
    subscription_data = {
        "subscriber_id": user.id,
        "cost": str(os.getenv("AMOUNT")),
        "currency": "NANO",
        "period": int(os.getenv("PERIOD"))
    }
    json_data = json.dumps(subscription_data)
    r = requests.post(f"{os.getenv('API_ENDPOINT')}create_subscription?token={os.getenv('NR_TOKEN')}", json_data)
    rx = r.json()
    await redis.set(user.id, rx['subscription_id'])
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


async def send_status_message(user: discord.User, subscription_json: dict):
    """
    Generate a QR and send the status of your subscription via DM.
    """
    qr_amount = str(int(Decimal(os.getenv('AMOUNT')) * Decimal(1000000000000000000000000000000)))
    uri_string = f"nano:{subscription_json['payment_address']}?amount={qr_amount}"
    qr = pyqrcode.create(uri_string)
    qr.png(f'qr/{user}.png', scale=4, background='#23272A', module_color="#ffffff")

    await manage_roles(user.id, subscription_json)
    embed = discord.Embed(title="Subscription Information", color=0x4169dd)
    embed.add_field(name="Subscription Status: ", value="**Active**" if subscription_json['active'] else '**Inactive**')
    embed.add_field(name="Expiration Date", value=subscription_json['expiration_date'][:10], inline=False)
    embed.add_field(name="Subscription Cost", value=(os.getenv('AMOUNT') + ' NANO'), inline=False)
    await user.send(
        embed=embed
    )
    if not subscription_json['active']:
        await user.send(
            file=discord.File(f'qr/{user}.png')
        )
        await user.send(
            f"Send {os.getenv('AMOUNT')} NANO to:"
        )
        await user.send(
            f"{subscription_json['payment_address']}"
        )


@client.command(aliases=["h"], pass_context=True)
async def help(ctx):
    """
    Send a help message with the commands and what they do to the user.
    """
    await ctx.message.author.send(
        "The Nano Center Subscription Bot is a discord bot that allows you to "
        "receive recognition for contributing to The Nano Center initiatives!\n"
        f"For {os.getenv('AMOUNT')} NANO, you will receive the {os.getenv('ROLE_NAME')} role for {os.getenv('PERIOD')} days, "
        "a special color reserved for donors to show your support and the unending gratitude of your Nano friends.\n\n"
        "Commands:\n"
        "- !help - This command!  A description of the bot and a list of commands\n"
        "- !status (also !renew / !subscribe) - Gives a status of your subscription along with payment address and subscription cost."
    )


@client.command(aliases=["renew", "subscribe"], pass_context=True)
async def status(ctx):
    """
    Check the status of the user's subscription
    """
    redis = await RedisDB.create()
    user = ctx.message.author
    try:
        subscription_id = await get_subscription_id(user, redis)

        if subscription_id is None:
            subscription_json = await create_subscription(user, redis)
        else:
            subscription_json = verify_subscription(subscription_id)

        await send_status_message(user, subscription_json)

    except Exception as e:
        await user.send(
            "There was an unexpected error during checking the status of your subscription.\n"
            "Please contact the Nano Center Ambassadors for more information."
        )
        raise e
    finally:
        await redis.close()

client.run(os.getenv("TOKEN"))