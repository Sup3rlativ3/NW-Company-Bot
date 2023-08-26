# Import standard libraries
import os
import logging

# Import third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv
from azure.data.tables import TableClient

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=discord.Intents.all())
        self.cogsFolder = "./cogs"

        # Initialize logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('discord_bot')

    async def setup_hook(self):
        
        try:
            logging.info("Loading the cogs")
            for cog in os.listdir(self.cogsFolder):
                if cog.endswith('.py'):
                    logging.info(f"loading the cog file {cog}")
                    await self.load_extension(f"cogs.{cog[:-3]}")

        except FileNotFoundError:
            print(f"The directory {self.cogsFolder} does not exist")
        except PermissionError:
            print(f"Permission denied to access the directory {cog}")
        except OSError as e:
            print(f"An OS error occurred: {e}")        
        
    async def on_ready(self):
        """
        This method is called when the bot is ready and provides some basic diagnostic information.
        """
        self.logger.info(f'We have logged in as {bot.user}')
        try:
            synced = await bot.tree.sync()
            self.logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logging.exception(e)


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

bot = Client()
bot.run(TOKEN)