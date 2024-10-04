# JobSpotBot

JobSpotBot is a Discord bot that regularly checks job boards for open jobs and notifies users of new postings! 

## Features

- Get postings from job boards in a variety of different formats thanks to user-defined scraper code!
- Broadcast job postings to multiple channels from multiple servers!
- Define keywords that must be present in a job title for it to be included in the notification!
- Customize embed accent colour!

## Requirements

| Software                                           | Purpose                             |
|----------------------------------------------------|-------------------------------------|
| Python >=3.8                                       | Core programming language.          |
| [Disnake](https://pypi.org/project/disnake/)       | Hosts Discord bot.                  |
| [jsonpickle](https://pypi.org/project/jsonpickle/) | Encodes/decodes persistent storage. |
| [schedule](https://pypi.org/project/schedule/)     | Runs new job checks periodically.   |

## Configuration

| Key                       | Purpose                                                                              |
|---------------------------|--------------------------------------------------------------------------------------|
| `bot_token`               | The token of the Discord bot that the program will send messages through.            |
| `active_guilds`           | A list containing the ID for every Discord server the bot will be active in.         |
| `active_channels`         | A list containing the ID for every channel the bot should post new jobs to.          |
| `check_interval_in_s`     | How often the bot should automatically check for jobs.                               |
| `colour`                  | The accent colour used in all Discord embeds. Must be hexadecimal (ex. `"0x357844"`) |
| `keywords` & `known_jobs` | These sets are managed by the bot. **Do not modify manually.**                       |