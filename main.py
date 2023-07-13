# Import standard libraries
import uuid
import os
import logging
from urllib.parse import urlparse

# Import third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from azure.data.tables import TableClient

# Import local libraries
from helpers import *

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

# Check if environment variables are set
if TOKEN is None:
    logging.error('DISCORD_TOKEN environment variable not set.')
    exit(1)
if AZURE_CONNECTION_STRING is None:
    logging.error('AZURE_CONNECTION_STRING environment variable not set.')
    exit(1)

# Azure setup
vods_table = TableClient.from_connection_string(AZURE_CONNECTION_STRING, 'vods')


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Initialize bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
        
@bot.event
async def on_ready():
    """
    This method is called when the bot is ready and provides some basic diagnostic information.
    """
    logger.info(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logging.exception(e)
    try:
        #salty_id = int('620952967566196776') #sup3r
        salty_id = int('869924385916592179') #salty
        global server 
        server = bot.get_guild(salty_id)
        if not server:
                logger.info("I'm not in a server with that ID.")
    except Exception as e:
        logging.exception(e)

@bot.tree.command()
async def submit(ctx, link: str, ign: str, town: str, war_type: str, role: str, comments: str):
    """
    Please fill out the information as requested to submit your VOD to salty.
    """
    logger.info(f'/submit command received from {ctx.user.name} with arguments: {link}, {town}, {war_type}, {role}')
        
    logger.info(f"The user ID is {ctx.user.id}")
    user_id = int(ctx.user.id)
    user = bot.get_user(user_id)
    logger.info(f"url is {user.display_avatar.url}")

    # Validate inputs
    if not is_valid_town(town):
        logging.info(f" {ctx.user.name} provided an invalid town")
        await ctx.channel.send("Invalid town.")
    if war_type.lower() not in ['attack', 'offence', 'defence']:
        logging.info(f" {ctx.user.name} provided an invalid war type")
        await ctx.channel.send("Invalid type of war. Please choose attack or defence.")
    if not is_valid_link(link):
        logging.info(f" {ctx.user.name} provided an invalid link")
        await ctx.channel.send("The link you provided isn't valid.")


    channel_id = int('1128945668023660654') #salty
    #channel_id= int('620952967566196778') #sup3r
    channel = server.get_channel(int(channel_id))
    logging.info(f"the channel is {channel}")
    
    logger.info("Creating the embed")
    # Create embed
    embed = discord.Embed(title=f'{ign} ({ctx.user.name}) submitted a video', colour=discord.Color.green())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name='VOD link', value=link, inline=False)
    embed.add_field(name='Town', value=town, inline=False)
    embed.add_field(name='War Type', value=war_type, inline=False)
    embed.add_field(name='Role', value=role, inline=False)
    embed.add_field(name='Comments', value=comments, inline=False)

    # Send embed to channel
    #channel = server.get_channel(int(channel_id))
    print(f"sending the embed")
    await channel.send(embed=embed)

    # Store in Azure Table storage
    try:
        write_vod = vods_table.create_entity({
        'PartitionKey': ctx.user.name,
        'RowKey': str(uuid.uuid4()),
        'link': link,
        'town': town,
        'action': war_type,
        'role': role
    })
        logger.debug(write_vod)
    except AzureError as e:
        logger.error(f'An error occurred while interacting with Azure: {e}')
        await ctx.send('An error occurred.')
        return
    

    logger.info('Video submitted successfully.')
    await ctx.response.send_message("Thank you for successfully submitting your vod for the war.")
    return

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