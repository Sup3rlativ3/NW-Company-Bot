import re
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime
import json

# Import third-party libraries
import discord
from discord.ext import commands, tasks

logging.basicConfig(level=logging.INFO)

# config import
f = open('.config')
config = json.load(f)

async def check_manager_perms(ctx):
        # config import
        f = open('.config')
        config = json.load(f)
        admin_role = config["permissions"]["admin"]
        print(F" the admin role is '{admin_role}'")
        role = discord.utils.get(ctx.guild.roles, name=admin_role)
        if role in ctx.user.roles:
            return True
        elif role not in ctx.user.roles:
            await ctx.response.send_message("Sorry you do not have the correct permissions.", ephemeral=True)
        else:
            await ctx.response.send_message("Sorry something went wrong.", ephemeral=True)

def is_valid_link(url) -> bool:
    """
    Verify if a link is valid based on regular expressions.
    
    Parameters:
    link (str): The URL to verify.

    Returns:
    bool: True if the URL is valid, False otherwise.
    """

    patterns = config["patterns"]
    
    # Check if the URL matches any of the patterns
    for platform, pattern in patterns.items():
        if re.fullmatch(pattern, url):
            return True
    
    return False

def is_valid_town(town) -> bool:

    valid_towns = config['valid_towns']
    town_shorthands = config['town_shorthands']

    # if the town name is a known shorthand, replace it with the full town name
    town = town.lower()
    if town in town_shorthands:
        town = town_shorthands[town]

    closest_match = process.extractOne(town, valid_towns, scorer=fuzz.ratio)
    if closest_match and closest_match[1] > 80:
        return True
    else:
        return False

def is_valid_role(role) -> bool:
    roles = config["role_channels"]
    valid_roles = roles.keys()
    #valid_roles = ['healer', 'dex', 'assassin', 'medium bruiser', 'heavy bruiser', 'VG+IG', 'fire mage', 'tank']
    closest_match = process.extractOne(role, valid_roles, scorer=fuzz.ratio)
    if closest_match and closest_match[1] > 60:
        return True
    else:
        return False

async def can_send_message(bot, channel_id):
    channel = bot.get_channel(channel_id)  # Replace 'bot' with your bot's instance

    # Check if the bot can see the channel
    if channel is None:
        print("The bot can't see the channel.")
        return False

    # Get the current permissions for the bot in the channel
    permissions = channel.permissions_for(channel.guild.me)

    if permissions.send_messages:
        print("The bot can send messages in this channel.")
        return True
    else:
        print("The bot cannot send messages in this channel.")
        return False
    
def parse_date(date_input):
    """
    Attempts to parse the input date string using predefined formats.
    Returns a string in the format 'YYYY-MM-DDTHH:MM:SS.Z' if a valid format is found.
    Otherwise, returns the input string as is.
    If a datetime object is provided as input, it's returned in the format 'YYYY-MM-DDTHH:MM:SS.Z'.
    """
    if date_input == None:
        return None
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    formats = [
        '%Y-%m-%d %H:%M',  # '2023-08-16 14:30'
        '%Y/%m/%d %H:%M',  # '2023/08/16 14:30'
        '%d/%m/%Y %H:%M',  # '16/08/2023 14:30'
        '%d-%m-%Y %H:%M',  # '16-08-2023 14:30'
        '%Y-%m-%d',  # '2023-08-16'
        '%Y/%m/%d',  # '2023/08/16'
        '%d/%m/%Y',  # '16/08/2023'
        '%d-%m-%Y',  # '16-08-2023'
    ]
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_input, fmt)
            return parsed_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            continue
    return date_input

def split_into_chunks(s, chunk_size=2000):
    """
    Splits a string into chunks of a given size.

    Parameters:
    - s (str): The string to split.
    - chunk_size (int): The maximum size for each chunk. Default is 2000.

    Returns:
    - list[str]: A list of string chunks.
    """
    return [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]