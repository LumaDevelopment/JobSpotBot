"""
Persistent Storage | Written by Joshua Sheldon

Maintains an object and class that maintain the
file-based storage that JobSpotBot uses.
"""

# ---------- IMPORTS ----------

# Python Default Imports
import json
import os

# Pip Sourced Imports
import jsonpickle

# ---------- CONSTANTS ----------

file_name = "storage.json"

# ---------- CLASSES & METHODS ----------


class StorageObject:
    """
    Data structure which holds all information that is
    persistently stored between runs of the bot.
    """

    # Instance Variables
    bot_token: str
    active_guilds: list
    active_channels: list
    check_interval_in_s: int
    color: str
    keywords: set
    known_jobs: set

    def __init__(self, bot_token, active_guilds, active_channels, check_interval_in_s, color, keywords, known_jobs):
        self.bot_token = bot_token
        self.active_guilds = active_guilds
        self.active_channels = active_channels
        self.check_interval_in_s = check_interval_in_s
        self.color = color
        self.keywords = keywords
        self.known_jobs = known_jobs


def get_default_storage_object() -> StorageObject:
    """Defines default values of the storage file."""

    # Create a blank Integer list
    int_list = list()
    int_list.append(0)

    return StorageObject(
        "",
        int_list.copy(),
        int_list.copy(),
        3600,
        "0xFFFFFF",
        set(),
        set()
    )


class Storage:
    """
    Controller class that creates the storage file if it doesn't
    exist, loads the StorageObject from the storage file if it
    does exist, distributes information from persistent storage,
    accepts modifications to persistent storage, and writes the
    StorageObject to a file whenever modifications are made.
    """

    _storage: StorageObject

    def __init__(self):
        try:
            # Retrieve encoded storage object from file
            file = open(file_name, "r")
            text = file.read()
            file.close()

            # Decode the object and set the
            # corresponding instance variable
            self._storage = jsonpickle.decode(text)

        except FileNotFoundError:
            print("No storage file, creating default...")

            # Create a new storage object and encode it as JSON
            self._storage = get_default_storage_object()
            self.update_storage_file()
            raise Exception("Created new storage file, please set bot token and relaunch!")

    def add_keyword(self, new_keyword) -> bool:
        """
        Adds the given keyword to the list of keywords.

        :return: True if the keyword was added, False if
                 the keyword was already in the list of
                 keywords and therefore was not added.
        """

        lowered_keyword = new_keyword.lower()

        if lowered_keyword in self._storage.keywords:
            return False

        self._storage.keywords.add(lowered_keyword)
        self.update_storage_file()

        return True

    def del_keyword(self, keyword) -> bool:
        """
        Removes the given keyword from the list of keywords.

        :return: True if the keyword was in the list and was
                 removed, False if they keyword was not in
                 the list and therefore was not removed.
        """

        try:
            self._storage.keywords.remove(keyword.lower())
            self.update_storage_file()
            return True
        except KeyError:
            # Not a problem.
            return False

    def get_active_channels(self) -> list[int]:
        return self._storage.active_channels

    def get_active_guilds(self) -> list[int]:
        return self._storage.active_guilds

    def get_bot_token(self) -> str:
        return self._storage.bot_token

    def get_check_interval_in_s(self) -> int:
        return self._storage.check_interval_in_s

    def get_colour(self) -> int:
        """
        Attempts to convert the stored embed accent
        color to an integer, otherwise returns
        pure white.
        """

        try:
            return int(self._storage.color, 16)
        except ValueError:
            # Invalid color. Return all-white
            print(f"Invalid color: \"{self._storage.color}\"")
            return 0xFFFFFF

    def get_keywords(self) -> set:
        return self._storage.keywords

    def get_known_jobs(self) -> set:
        return self._storage.known_jobs

    def set_known_jobs(self, new_known_jobs: set):
        self._storage.known_jobs = new_known_jobs
        self.update_storage_file()

    def update_storage_file(self):
        # Convert instance variable to JSON
        unformatted_json = jsonpickle.encode(self._storage)
        json_object = json.loads(unformatted_json)
        formatted_json_string = json.dumps(json_object, indent=2)

        # Delete the existing file
        try:
            os.remove(file_name)
        except Exception:
            # Really doesn't matter if this works or not
            pass

        # Write new storage object
        file = open(file_name, "x")
        file.write(formatted_json_string)
        file.close()
