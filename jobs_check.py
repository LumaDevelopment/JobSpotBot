"""
Jobs Check | Written by Joshua Sheldon

Contains the logic for checking for new jobs.
jobs_check() runs all scrapers, determines which
open jobs are new, filters new jobs by keywords
(if they exist), and returns the filtered set.
"""

# ---------- IMPORTS ----------

# Local Imports
from abstract_scraper import AbstractScraper
from persistent_storage import Storage

# ---------- METHODS ----------


def filter_jobs_with_keywords(new_jobs: set[tuple[str, str]], keywords: set) -> set[tuple[str, str]]:
    """
    Given a set of new jobs and keywords, returns a
    set of new jobs, where each job's title includes
    at least one of the given keywords.
    """

    filtered_new_jobs = set()

    for job in new_jobs:
        # Make job name lowercase, as keywords
        # are case-insensitive (for simplicity)
        job_name = job[0].lower()
        match = False

        # Assume all keywords are lowercase,
        # because they are
        for keyword in keywords:
            if keyword in job_name:
                match = True
                break

        if match:
            filtered_new_jobs.add(job)

    return filtered_new_jobs


def new_jobs_check(scrapers: set[AbstractScraper], storage: Storage) -> set[tuple[str, str]]:
    """
    Given a set of scrapers, use all of them to check for
    open jobs. Then, compare all open jobs with all known
    jobs. If any open jobs are new, then filter them based
    on keywords if any keywords are defined, and return
    the filtered set of new jobs.

    This method also updates the list of known jobs once
    the new ones are identified.
    """

    # For each scraper, scrape the open jobs and add them
    # to cumulative list of open jobs
    open_jobs = set()

    for scraper in scrapers:
        # Arbitrary code execution, wrap in try/catch
        try:
            scraper_open_jobs = scraper.scrape_open_jobs()
            for job in scraper_open_jobs:
                open_jobs.add(job)
        except Exception as e:
            print(f"Exception in scraper: {e}")

    # Make sure we got at least one open job
    if len(open_jobs) < 1:
        return open_jobs

    # Now we know we have at least one open job,
    # let's see if any of them are new
    known_jobs = storage.get_known_jobs()
    new_jobs = set()

    # Collect all new jobs by iterating through
    # all currently open jobs and adding all
    # which are not already known to the set
    for job in open_jobs:
        if job not in known_jobs:
            new_jobs.add(job)

    # Update list of known jobs
    storage.set_known_jobs(open_jobs)

    num_of_new_jobs = len(new_jobs)
    print(f"Detected {num_of_new_jobs} new job(s).")

    if num_of_new_jobs == 0:
        # Nothing more to do if there are no new jobs
        return new_jobs

    # If we have set keywords, we only want
    # to notify the user of new jobs that
    # contain one of the keywords
    keywords = storage.get_keywords()

    if len(keywords) > 0:
        filtered_new_jobs = filter_jobs_with_keywords(new_jobs, keywords)
    else:
        filtered_new_jobs = new_jobs

    # Return new jobs, filtered or not
    return filtered_new_jobs
