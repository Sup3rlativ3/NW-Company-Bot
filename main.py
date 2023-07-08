# Import libraries
import discord
import os
import logging
from discord.ext import commands
from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

# Azure setup
client = CosmosClient.from_connection_string(AZURE_CONNECTION_STRING)
database = client.get_database_client('your-database-name')
vods_table = database.get_container_client('vods')
channels_table = database.get_container_client('vodchannels')

# List of valid towns and roles
valid_towns = ['Brightwood', 'Brimstone Sands', 'Cutlass Keys', 'Ebonscale Reach', 'Edengrove', 
               'Everfall', 'First Light', 'Great Cleave', 'Monarch’s Bluffs', 'Mourningdale', 
               'Reekwater', 'Restless Shore', 'Shattered Mountain', 'Weaver’s Fen', 'Windsward']
valid_roles = ['healer', 'dex', 'assassin', 'medium bruiser', 'heavy bruiser', 'VG+IG', 'Fire Mage']

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Initialize bot
bot = commands.Bot(command_prefix='/')

def is_valid_link(link):
    """Check if a link is a valid YouTube or Twitch URL."""
    parsed = urlparse(link)
    return all([parsed.scheme, parsed.netloc, parsed.path]) and parsed.netloc in ['www.youtube.com', 'www.twitch.tv']

def get_channel_for_role(role):
    """Get the channel for a role."""
    for item in channels_table.query_items(
        query="SELECT * FROM channels_table c WHERE c.role=@role",
        parameters=[
            dict(name="@role", value=role)
        ],
        enable_cross_partition_query=True
    ):
        return item['channel_id']
    return None

def is_valid_channel(ctx, channel_id):
    """Check if a channel ID is valid."""
    return discord.utils.get(ctx.guild.channels, id=channel_id) is not None

@bot.command()
async def submit(ctx, link: str, town: str, action: str, role: str):
    """Handle the /submit command."""
    logger.info(f'/submit command received from {ctx.author.name}')

    # Validate inputs
    if town not in valid_towns:
        return 'Invalid town.'
    if role not in valid_roles:
        return 'Invalid role.'
    if action not in ['attack', 'defence']:
        return 'Invalid action.'
    if not is_valid_link(link):
        return 'Invalid link.'

    # Get the correct channel to send to
    channel_id = get_channel_for_role(role)
    if channel_id is None:
        return 'No channel assigned for this role.'

    # Create embed
    embed = discord.Embed(title=f'{ctx.author.name} submitted a video')
    embed.add_field(name='Link', value=link)
    embed.add_field(name='Town', value=town)
    embed.add_field(name='Action', value=action)
    embed.add_field(name='Role', value=role)

    # Send embed to channel
    channel = ctx.guild.get_channel(channel_id)
    await channel.send(embed=embed)

    # Store in Azure Table storage
    vods_table.upsert_item({
        'id': str(ctx.message.id),
        'link': link,
        'town': town,
        'action': action,
        'role': role,
        'user': ctx.author.name
    })

    logger.info('Video submitted successfully.')
    return 'Video submitted successfully.'

@bot.command()
async def setup(ctx, role: str, channel_id: int):
    """Handle the /setup command."""
    logger.info(f'/setup command received from {ctx.author.name}')

    # Validate role
    if role not in valid_roles:
        return 'Invalid role.'
    if not is_valid_channel(ctx, channel_id):
        return 'Invalid channel ID.'

    # Store in Azure Table storage
    channels_table.upsert_item({
        'id': str(ctx.guild.id),
        'role': role,
        'channel_id': channel_id
    })

    logger.info('Channel setup successfully.')
    return 'Channel setup successfully.'

@bot.event
async def on_ready():
    logger.info(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logging.exception(e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.error('Invalid command.')
        await ctx.send('Invalid command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        logger.error('Missing required argument.')
        await ctx.send('Missing required argument.')
    elif isinstance(error, commands.BadArgument):
        logger.error('Bad argument.')
        await ctx.send('Bad argument.')
    elif isinstance(error, AzureError):
        logger.error(f'Azure error: {error}')
        await ctx.send('An error occurred while interacting with Azure.')
    else:
        logger.error(f'An error occurred: {error}')
        await ctx.send('An error occurred.')
        raise error

bot.run(TOKEN)