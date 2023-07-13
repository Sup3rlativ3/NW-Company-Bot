import re
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

logging.basicConfig(level=logging.INFO)

def is_valid_link(link):
    """
    Verify if a link is valid based on a regular expression.
    
    Parameters:
    link (str): The URL to verify.

    Returns:
    bool: True if the URL is valid, False otherwise.
    """
    regex = r"(http:|https:)?(\/\/)?(www\.)?(youtube.com|youtu.be|twitch.tv)\/(watch|embed|live|videos)?(\?v=|\/)?(\S+)?"
    pattern = re.compile(regex)
    return bool(pattern.match(link))

def is_valid_town(town) -> bool:
    valid_towns = ['brightwood', 'brimstone sands', 'cutlass keys', 'ebonscale reach', 
               'everfall', 'monarch’s bluffs', 'mourningdale', 
               'reekwater', 'restless shore', 'weaver’s fen', 'windsward']

    town_shorthands = {
        'bw': 'brightwood',
        'bs': 'brimstone sands',
        'brim': 'brimstone sands',
        'ck': 'cutlass keys',
        'cutless': 'cutlass keys',
        'ebon': 'ebonscale reach',
        'ef': 'everfall',
        'mb': 'monarch’s bluffs',
        'monarchs': 'monarch’s bluffs',
        'md': 'mourningdale',
        'rw': 'reekwater',
        'reek': 'reekwater',
        'rs': 'restless shore',
        'restless': 'restless shore',
        'wf': 'weaver’s fen',
        'weavers': 'weaver’s fen',
        'ww': 'windsward',
        'winny': 'windsward',
        'winnie': 'windsward',
    }

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
    valid_roles = ['healer', 'dex', 'assassin', 'medium bruiser', 'heavy bruiser', 'VG+IG', 'fire mage', 'tank']
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