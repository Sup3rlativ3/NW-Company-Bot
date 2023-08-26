# Import standard libraries
import uuid
import os
import logging
from datetime import datetime, timezone
import io
import csv

# Import third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from azure.data.tables import TableClient

# Import local libraries
from helpers import *

class timeTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load environment variables
        load_dotenv()
        AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

        # Check if environment variables are set
        if AZURE_CONNECTION_STRING is None:
            logging.error('AZURE_CONNECTION_STRING environment variable not set.')
            exit(1)

        # Azure setup
        self.entries_table = TableClient.from_connection_string(AZURE_CONNECTION_STRING, 'entries')


    @discord.app_commands.command(name="clockin", description="Clock in for an approved event.")
    async def clockin(self, ctx, tag: str = None):
        """
        Clock into time tracking with an optional tag.
        """
        timestamp = datetime.utcnow()  # Keep as datetime object

        logger = logging.getLogger('discord_bot')

        myfilter = f"PartitionKey eq '{str(ctx.user.id)}'"
        entities = self.entries_table.query_entities(myfilter)
        for entity in entities:
            if 'clock_out_time' not in entity:
                await ctx.response.send_message(f"You already have a time entry open. Please clockout before starting a new time entry.")


        try:
            write_time = self.entries_table.create_entity({
                'PartitionKey': str(ctx.user.id),
                'RowKey': str(uuid.uuid4()),
                'tag': tag,
                'username': str(ctx.user.display_name),
                'servername': str(ctx.guild.name),
                'serverid': str(ctx.guild.id),
                'clock_in_time': timestamp  
            })
            logger.debug(write_time)

            if tag:
                await ctx.response.send_message(f"{ctx.user.display_name} has clocked in using the tag {tag}.")
            else:
                await ctx.response.send_message(f"{ctx.user.display_name} has clocked in.")

        except AzureError as e:
            logger.error(f'An error occurred while interacting with Azure: {e}')
            await ctx.response.send_message('An error occurred.')
            return

    @discord.app_commands.command(name="clockout", description="Close your time entry.")
    async def clockout(self, ctx):
        """
        Clock out of time tracking.
        """
        timestamp = datetime.utcnow().astimezone(timezone.utc)
        myfilter = f"PartitionKey eq '{str(ctx.user.id)}'"
        entities = self.entries_table.query_entities(myfilter)
        for entity in entities:
            if 'clock_out_time' not in entity:
                entity['clock_out_time'] = timestamp
                
                starttime = entity['clock_in_time']         
                endtime = timestamp
                print(f"start time {starttime}")
                print(f"end time: {endtime}")

                timediff = endtime - starttime

                hours, remainder = divmod(int(timediff.seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_added = f""
                if hours > 0:
                    time_added += f"{hours} hours, "
                if minutes > 0:
                    time_added += f"{minutes} minutes"
                elif minutes == 0:
                    time_added += f"0 minutes"

                entity['minutes'] = (hours * 60) + minutes
                self.entries_table.update_entity(entity=entity)

                await ctx.response.send_message(f"{ctx.user.display_name} has clocked out adding {time_added}.")

    async def check_manager_perms(ctx):
            role = discord.utils.get(ctx.guild.roles, name="Support Team")
            if role in ctx.user.roles:
                return True
            elif role not in ctx.user.roles:
                await ctx.response.send_message("Sorry you do not have the correct permissions.", ephemeral=True)
            else:
                await ctx.response.send_message("Sorry something went wrong.", ephemeral=True)

    @discord.app_commands.command(name="get_user_time", description="get time entries of a specific user. RESTRICTED")
    @discord.app_commands.check(check_manager_perms)
    async def get_user_time(self, ctx, user: discord.Member, csv_output: bool = False):
        user_id = str(user.id)
        myfilter = f"PartitionKey eq '{user_id}'"
        entities = self.entries_table.query_entities(myfilter)

        if csv_output:
            # Create a CSV in-memory text stream
            csv_output_io = io.StringIO()
            fields = ['PartitionKey', 'RowKey', 'username', 'clock_in_time', 'clock_out_time', 'tag', 'minutes']
            csv_writer = csv.DictWriter(csv_output_io, fields)
            csv_writer.writeheader()

            # Write the filtered entities to the CSV
            for entity in entities:
                csv_writer.writerow({field: entity[field] for field in fields})

            # Reset the in-memory text stream position
            csv_output_io.seek(0)

            # Create a Discord file from the CSV string and send it
            discord_file = discord.File(fp=csv_output_io, filename='user_time.csv')
            await ctx.response.send_message(file=discord_file)
        else:
            # Send the entities as text or embed (customize as needed)
            response = ""
            for data in entities:
                response += f"**Clock-in:** {data['clock_in_time']}, **Clock-out:** {data.get('clock_out_time', 'N/A')}, **Tags:** {data.get('tag', 'No Tag')}, **Minutes:** {data['minutes']}\n"

            await ctx.response.send_message(f"{response}")

    @discord.app_commands.command(name="get_time_range", description="Get all time entries between two dates/times. RESTRICTED")
    @discord.app_commands.check(check_manager_perms)
    async def get_time_range(self, ctx, start_date: str, end_date: str, csv_output: bool = False):

        # Parse input dates
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Validate parsed dates
        if not start_date or not end_date:
            await ctx.response.send_message("The date format is either invalid or not recognised, please try again.")
            return
        if end_date <= start_date:
            await ctx.response.send_message("The end time is before the start time, please try again.")
            return

        myfilter = f"clock_in_time gt datetime'{start_date}' and clock_out_time lt datetime'{end_date}' and serverid eq '{str(ctx.guild.id)}'"
        entities = self.entries_table.query_entities(myfilter)

        if csv_output:
            # Create a CSV in-memory text stream
            csv_output_io = io.StringIO()
            fields = ['PartitionKey', 'RowKey', 'username', 'clock_in_time', 'clock_out_time', 'tag', 'minutes']
            csv_writer = csv.DictWriter(csv_output_io, fields)
            csv_writer.writeheader()

            # Write the filtered entities to the CSV
            for entity in entities:
                entity['tag'] = entity['tag'].replace(',', '')
                csv_writer.writerow({field: entity[field] for field in fields})

            # Reset the in-memory text stream position
            csv_output_io.seek(0)

            # Create a Discord file from the CSV string and send it
            discord_file = discord.File(fp=csv_output_io, filename='time_range.csv')
            await ctx.response.send_message(file=discord_file)
        else:
            # Send the filtered entities as text or embed (customize as needed)
            response = ""
            for data in entities:
                response += f"**Clock-in:** {data['clock_in_time']}, **Clock-out:** {data.get('clock_out_time', 'N/A')}, **Tags:** {data.get('tag', 'No Tag')}, **Minutes:** {data['minutes']}\n"

            chunks = split_into_chunks(response)

            await ctx.response.send_message(f"{chunks[0]}")
            for chunk in chunks[1:]:
                await ctx.followup.send(content=chunk)

    @discord.app_commands.command(name="force_clockout", description="Get all time entries between two dates/times. RESTRICTED")
    @discord.app_commands.check(check_manager_perms)
    async def force_clockout(self, ctx, tag: str = None):
        """
        Force clock out of all entries without a clock_out_time.
        Optionally filter by a specific tag.
        """
        # Get the current time in UTC
        timestamp = datetime.utcnow().astimezone(timezone.utc)

        # Query all entities without applying a filter
        myfilter = f"clock_in_time ne '' and serverid eq '{str(ctx.guild.id)}'"
        entities = self.entries_table.query_entities(myfilter)
        count_updated = 0

        entrieslist = ""
        
        # Iterate through the entities and update them
        for entity in entities:
            # Check if clock_out_time is not set, and if tag is provided, match the tag
            if 'clock_out_time' not in entity and (tag is None or entity['tag'] == str(tag)):
                entity['clock_out_time'] = timestamp

                # Optionally, you can calculate the minutes as done in the clockout command
                starttime = entity['clock_in_time']
                timediff = timestamp - starttime
                hours, remainder = divmod(int(timediff.seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                entity['minutes'] = (hours * 60) + minutes

                time_added = f""
                if hours > 0:
                    time_added += f"{hours} hours, "
                if minutes > 0:
                    time_added += f"{minutes} minutes"
                elif minutes == 0:
                    time_added += f"0 minutes"

                self.entries_table.update_entity(entity=entity)
                count_updated += 1

                user = await self.bot.fetch_user(int(entity['PartitionKey']))

                entrieslist += f"{user.mention} has clocked out adding {time_added}.\n"

        # Send a response with the number of updated entries
        entrieslist += f"Force clocked out {count_updated} entries."
        await ctx.response.send_message(entrieslist)


async def setup(bot):
    await bot.add_cog(timeTracker(bot))