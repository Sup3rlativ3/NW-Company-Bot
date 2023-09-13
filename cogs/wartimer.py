# Import standard libraries
import os
import logging
import json
from datetime import datetime, timedelta
import asyncio

# Import third-party libraries
import discord
from discord.ext import commands, tasks

# Import local libraries
from helpers import *

class wartimer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Load respawn times from JSON file
        with open('respawn.json', 'r') as file:
            self.respawn_times = json.load(file)

            

    # Command to start war
    @discord.app_commands.command(name="start_war", description="Tells the bot to join a voice channel and start calling respawns.")
    @discord.app_commands.check(check_manager_perms)
    async def start_war(self, ctx, channel: discord.VoiceChannel):
        """
        Tells the bot to join a voice channel and start calling respawns.
        """
        try:
            self.voice_channel = await channel.connect()
            await ctx.response.send_message(f"I have successfully connected to {channel}.", ephemeral=True)
            self.bot.loop.create_task(self.play_respawns(self.voice_channel))
        except Exception as e:
            logging.exception("Failed to start war: %s", e)

    # Command to end war
    @discord.app_commands.command(name="end_war", description="Tells the bot to leave the voice channel it is in.")
    @discord.app_commands.check(check_manager_perms)
    async def end_war(self, ctx):
        """
        Tells the bot to leave the voice channel it is in.
        """
        try:
            await self.voice_channel.disconnect()
            await ctx.response.send_message(f"I have successfully disconnected from the channel.", ephemeral=True)
        except:
            print("Failed to disconect")

    async def play_respawns(self, voice_channel):
        """
        Play respawns at designated times.
        """
        while True:
            now = datetime.now().strftime("%M:%S")
            # Add a section here for each respawn timer increase e.g. "respawns now 50 seconds"
            if now in self.respawn_times:
                source = discord.FFmpegPCMAudio("5sec_respawn.mp3", executable='ffmpeg')
                voice_channel.play(source)
                await asyncio.sleep(10)
                pass
            await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(wartimer(bot))