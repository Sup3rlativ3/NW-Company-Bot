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
    valid_towns = ['Brightwood', 'Brimstone Sands', 'Cutlass Keys', 'Ebonscale Reach', 
               'Everfall', 'Monarch’s Bluffs', 'Mourningdale', 
               'Reekwater', 'Restless Shore', 'Weaver’s Fen', 'Windsward']

    town_shorthands = {
        'BW': 'Brightwood',
        'BS': 'Brimstone Sands',
        'Brim': 'Brimstone Sands',
        'CK': 'Cutlass Keys',
        'Cutless': 'Cutlass Keys',
        'Ebon': 'Ebonscale Reach',
        'EF': 'Everfall',
        'Mb': 'Monarch’s Bluffs',
        'Monarchs': 'Monarch’s Bluffs',
        'MD': 'Mourningdale',
        'RW': 'Reekwater',
        'Reek': 'Reekwater',
        'RS': 'Restless Shore',
        'Restless': 'Restless Shore',
        'WF': 'Weaver’s Fen',
        'Weavers': 'Weaver’s Fen',
        'WW': 'Windsward',
        'Winny': 'Windsward',
        'Winnie': 'Windsward',
    }

    # if the town name is a known shorthand, replace it with the full town name
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
    if closest_match and closest_match[1] > 80:
        return True
    else:
        return False
    
def get_channel_for_role(role) -> str:
    
    match role:
        case "healer":
            return '1110715300904714272'
        case "VG+IG", "Fire Mage":
            return '1110715332701716490'
        case "dex":
            return '1110715395654025216'
        case "medium bruiser", "heavy bruiser":
            return '1110715395654025216'
        case "assassin":
            return '1110715441900429412'
        case "tank":
            return '1110715527728484405'
        case _:
            return None