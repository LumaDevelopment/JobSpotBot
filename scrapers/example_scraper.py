"""
Example Scraper | Written by Joshua Sheldon

Used to scrape 'jobs' (read: 'a' elements) from
example.com
"""

# ---------- IMPORTS ----------

# Pip Sourced Imports

# For most real applications, you'll probably need to
# use something like Selenium to parse page JavaScript
import requests

from bs4 import BeautifulSoup

# Local Imports
from abstract_scraper import AbstractScraper

# ---------- CONSTANTS ----------

jobs_page_domain = "example.com"
jobs_page_url = "https://" + jobs_page_domain + "/"
job_link_prefix = "https://www.iana.org/domains/"

# ---------- SCRAPER CONTENT ----------


def log(msg: str):
    """
    Adds the site we're scraping from to the beginning
    of every printed message.
    """
    print(f"[{jobs_page_domain}] {msg}")


def get_jobs_page_source() -> str | None:
    """
    Get the source of the page pointed to by the
    jobs_page_url constant.

    :return: The source of the jobs page, or None
             if the status code of the response != 200
    """

    response = requests.get(jobs_page_url)

    if response.status_code != requests.codes.ok:
        print(f"Failed to get source of jobs page ({response.status_code})")
        return None

    return response.text


class Scraper(AbstractScraper):
    """
    The name of this class MUST be Scraper, otherwise
    the JobSpotBot cannot load it.
    """

    def scrape_open_jobs(self) -> set[tuple[str, str]]:
        # Attempt to pull jobs page source
        page_source = get_jobs_page_source()

        if page_source is None:
            # Logging done in method
            return set()

        # Parse page source as HTML and attempt
        # to grab all links from it
        soup = BeautifulSoup(page_source, "html.parser")
        link_elements = soup.find_all('a')

        if link_elements is None:
            log("Successfully retrieved jobs page, but failed to retrieve link elemenets!")
            return set()

        # Loop through all potential jobs, and if
        # it is a job, add it to the set.
        open_jobs = set()

        for link_element in link_elements:
            # Get what the link element is actually pointing to
            # (hopefully a job page)
            link = link_element.get('href')

            if link is None:
                # Link element doesn't have a link, somehow
                continue

            # Check if this is valid job
            if link.startswith(job_link_prefix):
                open_jobs.add((link_element.text, link))

        log(f"Found {len(open_jobs)} open jobs.")
        return open_jobs
