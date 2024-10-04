"""JobSpotBot | Written by Joshua Sheldon"""

# ---------- IMPORTS ----------

# Python Default Imports
import asyncio
import importlib
from pathlib import Path
import time
from threading import Thread

# Pip Sourced Imports
import schedule

# Local Imports
from abstract_scraper import AbstractScraper
from discord_interface import DiscordInterface
from jobs_check import new_jobs_check
from persistent_storage import Storage

# ---------- CONSTANTS ----------

scrapers_dir_name = "scrapers"
scraper_class_name = "Scraper"

# ---------- METHODS ----------

def check_and_notify(discord_interface: DiscordInterface, scrapers: set[AbstractScraper], storage: Storage):
    """
    Retrieves all new (and potentially filtered) jobs, and
    fires a Discord notification with all new jobs if there
    are any.
    """
    new_jobs = new_jobs_check(scrapers, storage)

    # If new jobs exist, notify everyone on Discord
    if len(new_jobs) > 0:
        asyncio.run_coroutine_threadsafe(
            discord_interface.do_new_jobs_notif(new_jobs),
            discord_interface.bot.loop
        )


def schedule_jobs_check(discord_interface: DiscordInterface, scrapers: set[AbstractScraper], storage: Storage):
    """
    Schedules a check for new jobs at the interval
    defined in the storage file.
    """
    schedule.every(
        storage.get_check_interval_in_s()
    ).seconds.do(
        check_and_notify, discord_interface, scrapers, storage
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


def load_scrapers_from_path(scrapers_path: Path) -> set[AbstractScraper]:
    """
    Iterates through all Python files in the "scrapers/" directory and
    attempts to create new instances of the Scraper classes defined
    within. These instances are collected into a set and returned by
    this method.

    :param scrapers_path: The location of all defined scrapers.
    :return: A list of scrapers used to get open jobs.
    """

    scrapers = set()
    for file in scrapers_path.glob("*.py"):
        module_name = file.stem
        try:
            # Import file containing implemented scraper
            module = importlib.import_module(f"{scrapers_dir_name}.{module_name}")

            # Get implemented scraper class and create
            # a new instance of the scraper
            scraper_class = getattr(module, scraper_class_name)
            scraper_instance = scraper_class()

            # Add it to list of scrapers
            scrapers.add(scraper_instance)

        except:
            print(f"Failed to load scraper: {module_name}")

    return scrapers


async def main():
    # Create the scrapers directory if it
    # doesn't already exist.
    scrapers_path = Path(scrapers_dir_name)
    scrapers_path.mkdir(parents=True, exist_ok=True)

    # Load scrapers
    scrapers = load_scrapers_from_path(scrapers_path)

    if len(scrapers) > 0:
        print(f"Successfully loaded {len(scrapers)} scrapers!")
    else:
        raise Exception("No scrapers successfully loaded!")

    # This raises an exception if a storage
    # file doesn't already exist.
    storage = Storage()

    print("Successfully read in storage from file!")

    # Check if there are no currently known jobs.
    # If so, initialize the list.
    initial_known_jobs = storage.get_known_jobs()
    if len(initial_known_jobs) == 0:
        # Run a new jobs check to attempt to fill out
        # the known jobs list
        print("No known jobs. Initializing list...")
        new_jobs_check(scrapers, storage)

    # Initialize the Discord Interface early,
    # so it can be passed into the jobs update
    # thread
    discord_interface = DiscordInterface(scrapers, storage)

    # Schedule repeating task in a new thread
    # because it has an infinite while loop
    # in it, and we don't want to block the main
    # thread (discord bot needs to run on it)
    thread = Thread(
        target=schedule_jobs_check,
        args=(discord_interface, scrapers, storage)
    )
    thread.start()

    # Run the bot
    await discord_interface.start_bot()


asyncio.run(main())
