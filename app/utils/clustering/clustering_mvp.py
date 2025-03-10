import json

import pandas as pd

MATCHING_MINIMUM = 8


def cluster(cohort_submissions: dict) -> list:
    """
    Naming structure for variables:
    team = 2 players (1 submission each)
    squad = 2 Teams
    cohort = group of players, either grouped into squads or not

    Splits given dict into groups of 4 based on their ranked complexity

    Input: dictionary of a single cohort containing nested dictionary
    with 'submission_id' as first level key,
    and 'complexity' as one of the inner keys
    Output: Nested list of clusters:
    [[list of unmatched - promoted submission_ids],[list of submission_ids], [list of submission_ids]]
    Highest to lowest complexity score
    """

    # Initial variables
    num_submissions = len(cohort_submissions)
    remainder = num_submissions % 4
    squads = []
    squad = []
    promoted = []

    # if there are insufficient submissions to meet the minimum
    if num_submissions < MATCHING_MINIMUM:
        return squads

    # identify players to be promoted without matching to ensure squads have 4 players each.
    for submission in sorted(cohort_submissions.items(), key=lambda x:x[1]["Skipped"]):
        promoted.append(submission[0])

    promoted = promoted[:remainder]
    squads.append(promoted)

    # sort the cohort by complexity and build squads to return.
    for submission in sorted(cohort_submissions.items(), key=lambda x:x[1]["Complexity"], reverse=True):
        if submission[0] not in promoted:
            squad.append(submission[0])
        if len(squad) == 4:
            squads.append(squad)
            squad = []
    return squads


async def batch_cluster(submissions: dict) -> json:
    """
    Generates a return JSON object of clusters for all provided cohorts.

    Input: dictionary of all cohort submissions
    Output: JSON object of nested lists of submission IDs by cluster, by cohort

    To test locally in isolation as an async function, run the following code:
    import asyncio
    asyncio.run(batch_cluster(submissions_json))
    """

    # Initiate cluster dictionary
    cluster_dict = {}

    # Iterate through cohorts to get clusters, and
    # add each to cluster_dict
    for cohort_id in submissions:
        clusters = cluster(submissions[cohort_id])
        cluster_dict[cohort_id] = clusters

    # Convert dict back to JSON
    cluster_json = json.dumps(cluster_dict)

    return cluster_json
