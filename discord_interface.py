"""
Discord Interface | Written by Joshua Sheldon

This file provides the DiscordInterface class,
which starts the Discord bot, defines its commands,
and provides functionality for notifying Discord
users that new jobs have been found.
"""

# ---------- IMPORTS ----------

# Python Default Imports
import datetime

# Pip Sourced Imports
import disnake
from disnake.ext import commands

# Local Imports
from abstract_scraper import AbstractScraper
from jobs_check import new_jobs_check
from persistent_storage import Storage

# ---------- CONSTANTS ----------

check_emote = ":white_check_mark:"

# ---------- CLASSES ----------


class DiscordInterface:
    """
    Starts the Discord bot, defines its commands,
    and provides functionality for notifying Discord
    users that new jobs have been found.
    """

    bot: commands.InteractionBot
    _scrapers: set[AbstractScraper]
    _storage: Storage

    def __init__(self, scrapers: set[AbstractScraper], storage: Storage):
        self.bot = commands.InteractionBot(test_guilds=storage.get_active_guilds())
        self._scrapers = scrapers
        self._storage = storage

    async def start_bot(self):
        # /check
        @self.bot.slash_command(
            description="Manually starts a check for new jobs."
        )
        async def check(inter: disnake.ApplicationCommandInteraction):
            new_jobs = new_jobs_check(self._scrapers, self._storage)

            # If new jobs exist, notify everyone on Discord
            if len(new_jobs) > 0:
                await self.do_new_jobs_notif(new_jobs)

            await inter.send(f"{check_emote} Successfully checked for new jobs!")

        @self.bot.slash_command()
        async def keywords(inter: disnake.ApplicationCommandInteraction):
            """
            Blank, the /keywords command itself does nothing,
            only its subcommands do anything.
            """
            pass

        # /keywords add
        @keywords.sub_command(
            description="Add keyword of interest for job titles."
        )
        async def add(inter: disnake.ApplicationCommandInteraction, keyword: str):

            was_added = self._storage.add_keyword(keyword)

            if was_added:
                response = f"Added keyword: `{keyword}`"
            else:
                response = f"Keyword (`{keyword}`) is already active!"

            await inter.send(response)

        # /keywords delete
        @keywords.sub_command(
            description="Deletes a keyword of interest for job titles."
        )
        async def delete(inter: disnake.ApplicationCommandInteraction, keyword: str):

            was_deleted = self._storage.del_keyword(keyword)

            if was_deleted:
                response = f"Deleted keyword: `{keyword}`"
            else:
                response = f"Keyword (`{keyword}`) not found!"

            await inter.send(response)

        # /keywords list
        @keywords.sub_command(
            description="Lists all keywords of interest for job titles."
        )
        async def list(inter: disnake.ApplicationCommandInteraction):
            keywords = self._storage.get_keywords()

            if len(keywords) > 0:
                keywords_as_text = []

                for keyword in keywords:
                    keywords_as_text.append(f"- {keyword}")

                description = "\n".join(keywords_as_text)
            else:
                description = "No active keywords!"

            embed = disnake.Embed(
                title="Active Keywords",
                description=description,
                colour=self._storage.get_colour(),
                timestamp=datetime.datetime.now()
            )

            await inter.send(embed=embed)

        await self.bot.start(self._storage.get_bot_token())

    async def do_new_jobs_notif(self, new_jobs: set[tuple[str, str]]):
        """
        Given a set of new jobs, sends a message to each active
        channel that new jobs have been posted, with the list
        of new jobs.

        :param new_jobs: A set of jobs represented by tuples. The first
                         element of each tuple is the job's name, and
                         the second element of each tuple is the job's
                         link.
        """

        jobs_as_text = []

        for job in new_jobs:
            jobs_as_text.append(f"- [{job[0]}]({job[1]})")

        description = "\n".join(jobs_as_text)

        embed = disnake.Embed(
            title="NEW JOBS FOUND",
            description=description,
            colour=self._storage.get_colour(),
            timestamp=datetime.datetime.now()
        )

        # Send the embed to all channels
        for channel_id in self._storage.get_active_channels():
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            await channel.send(embed=embed)

        print("Pushed notification that new jobs have been found!")
