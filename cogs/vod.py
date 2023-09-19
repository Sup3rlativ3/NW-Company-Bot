# Import standard libraries
import os
import uuid
import logging
from urllib.parse import urlparse
import json

# Import third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from azure.data.tables import TableClient

# Import local libraries
from helpers import *

class vod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load environment variables
        AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

        # Check if environment variables are set
        if AZURE_CONNECTION_STRING is None:
            logging.error('AZURE_CONNECTION_STRING environment variable not set.')
            exit(1)

        # Azure setup
        self.vods_table = TableClient.from_connection_string(AZURE_CONNECTION_STRING, 'vods')

        # config import
        f = open('.config')
        self.config = json.load(f)

        

    @discord.app_commands.command(name="submit", description="Submit a vod for a clappin cheeks war.")
    async def submit(self, ctx, link: str, ign: str, town: str, war_type: str, role: str, comments: str, public: bool = False):
        """
        Please fill out the information as requested to submit your VOD to Clappin.
        """
        try:
            server_id = int(self.config.get("server"))
            print(F"Server ID is {server_id}")
            self.server = self.bot.get_guild(server_id)
            if not self.server:
                    logger.warning("I'm not in a server with that ID.")
        except Exception as e:
            logging.exception(e)

        logger = logging.getLogger('discord_bot')
        logger.info(f'/submit command received from {ctx.user.name} with arguments: {link}, {town}, {war_type}, {role}')
            
        logger.info(f"The user ID is {ctx.user.id}")
        user_id = int(ctx.user.id)
        user = self.bot.get_user(user_id)
        logger.info(f"url is {user.display_avatar.url}")

        # Validate inputs
        if not is_valid_town(town):
            logging.info(f" {ctx.user.name} provided an invalid town")
            await ctx.channel.send("Invalid town.")
            return
        if war_type.lower() not in ['attack', 'offence', 'defence']:
            logging.info(f" {ctx.user.name} provided an invalid war type")
            await ctx.channel.send("Invalid type of war. Please choose attack or defence.")
            return
        if not is_valid_link(link):
            logging.info(f" {ctx.user.name} provided an invalid link")
            await ctx.channel.send("The link you provided isn't valid.")
            return
        if not is_valid_role(role.lower()):
            logging.info(f"{ctx.user.name} provided an invalid role.")
            await ctx.channel.send(f"The role you provided is invalid. Valid choices are {(config['role_channels']).keys()}.")
            return
        
        else:
            roles = config["role_channels"]
            channel_id = int(roles[role.lower()])
            channel = self.server.get_channel(int(channel_id))
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

        try:
            if public == False:
                server_id = int(self.config.get("server"))
                print(F"Server ID is {server_id}")
                self.server = self.bot.get_guild(server_id)
                thread = await channel.create_thread(name=f"{ign}'s {town} {war_type} VOD", type=discord.ChannelType.private_thread,invitable=True)
                admin_role = self.config["permissions"]["admin"]
                guild = self.server
                for arole in guild.roles:
                    if arole.name.lower() == admin_role.lower():
                        print(f"The ID for the role '{admin_role}' is: {arole.id}")
                        admin_role = guild.get_role(arole.id)
                        break
                    
                print(f"@{admin_role.id}")

                for user in admin_role.members:
                    print(f"{user}")
                    print(f"Adding {user} with id {user.id}")
                    await thread.add_user(user)
            else:
                thread = await channel.create_thread(name=f"{ign}'s {town} {war_type} VOD", type=discord.ChannelType.public_thread)
            
            # Send embed to channel
            print(f"sending the embed")
            await thread.send(embed=embed)
        except discord.Forbidden:
            logging.error("Bot does not have the required permissions.")
        except discord.HTTPException as e:
            logging.error(f"Failed to create thread: {e}")

        # Store in Azure Table storage
        try:
            write_vod = self.vods_table.create_entity({
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

async def setup(bot):
    await bot.add_cog(vod(bot))