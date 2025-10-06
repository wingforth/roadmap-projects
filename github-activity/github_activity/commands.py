"""
GitHub Activity CLI commands.

1. event

- list_repository_events = "/repos/{owner}/{repo}/events"
    github-activity event --repo REPO

- list_events_for_the_authenticated_user = "/users/{username}/events"
    github-activity event --user USER

- list_events_received_by_the_authenticated_user ="/users/{username}/received_events"
    github-activity event --user USER --received

2. user

- get_the_authenticated_user = "/user"
    github-activity user

- get_a_user_using_their_ID = "/user/{account_id}"
    github-activity user --id ID

- get_a_user = "/users/{username}"
    github-activity user --name NAME

3. repository

- get_a_repository = "/repos/{owner}/{repo}"
    github-activity repo view REPO

- list_repositories_for_the_authenticated_user = "/user/repos"
    github-activity repo list
- list_repositories_starred_by_the_authenticated_user = "/user/starred"
    github-activity repo list --starred
- list_repositories_watched_by_the_authenticated_user = "/user/subscriptions"
    github-activity repo list --watched

- list_repositories_for_a_user = "/users/{username}/repos"
    github-activity repo list --user USER
- list_repositories_starred_by_a_user = "/users/{username}/starred"
    github-activity repo list --user USER --starred
- list_repositories_watched_by_a_user = "/users/{username}/subscriptions"
    github-activity repo list --user USER --watched

4. issue

- get_an_issue = "/repos/{owner}/{repo}/issues/{issue_number}"
    github-activity issue view REPO ISSUE

- list_issues_assigned_to_the_authenticated_user = "/issues"
    github-activity issue list

- list_organization_issues_assigned_to_the_authenticated_user = "/orgs/{org}/issues"
    github-activity issue list --org ORG

- list_user_account_issues_assigned_to_the_authenticated_user = "/user/issues"
    github-activity issue list --account

- list_repository_issues = "/repos/{owner}/{repo}/issues"
    github-activity issue list --repo REPO

5. pull request

- get_a_pull_request = "/repos/{owner}/{repo}/pulls/{pull_number}"
    github-activity pr view REPO PULL

- list_pull_requests = "/repos/{owner}/{repo}/pulls"
    github-activity pr list REPO

- list_pull_requests_associated_with_a_commit = "/repos/{owner}/{repo}/commits/{commit_sha}/pulls"
    github-activity pr list REPO --commit SHA

6. commit

- get_a_commit = "/repos/{owner}/{repo}/commits/{ref}"
    github-activity commit view REPO REF

- list_commits_on_a_pull_request = "/repos/{owner}/{repo}/pulls/{pull_number}/commit"
    github-activity commit list REPO --pull PULL

- list_commits = "/repos/{owner}/{repo}/commits?sha={sha}"-->
    github-activity commit list REPO --start SHA

7. branch

- get_a_branch = "/repos/{owner}/{repo}/branches/{branch}"
    github-activity branch view REPO BRANCH

- list_branches_for_HEAD_commit = "/repos/{owner}/{repo}/commits/{commit_sha}/branches-where-head"
    github-activity branch list REPO --head SHA

- list_branches = "/repos/{owner}/{repo}/branches"
    github-activity branch list REPO

8. rate limit

- get_rate_limit_status_for_the_authenticated_user = "/rate_limit"
    github-activity ratelimit

"""

from argparse import ArgumentTypeError


def _positive_integer(s: str) -> int:
    """
    Convert a string to a positive integer.

    Args:
        s (str): The string to convert.

    Returns:
        int: The converted positive integer.

    Raises:
        ArgumentTypeError: If the value is not a positive integer.
    """
    try:
        assert (n := int(s)) > 0
    except (ValueError, AssertionError):
        raise ArgumentTypeError(f"invalid positive integer value: '{s}'")
    return n


# List of command definitions for the GitHub Activity CLI.
commands = [
    {
        "cmd": "event",
        "args": [
            {
                "name_or_flags": "--received",
                "action": "store_true",
                "help": "Events that received by watching repositories and following users.",
            },
            {
                "name_or_flags": "--limit",
                "type": int,
                "default": 30,
                "help": "Maximum number of events to fetch. Default 30.",
            },
        ],
        "exclusive_group": [
            {"name_or_flags": "--user", "help": "User login name"},
            {"name_or_flags": "--repo", "help": "The full name of the repository."},
        ],
        "help": "List events triggered by activity on GitHub.",
    },
    {
        "cmd": "user",
        "args": [],
        "exclusive_group": [
            {"name_or_flags": "--name", "help": "User login name"},
            {"name_or_flags": "--id", "type": int, "help": "User ID"},
        ],
        "help": "View profile information of a user.",
    },
    {
        "cmd": "repo",
        "subcommands": [
            {
                "cmd": "view",
                "args": [{"name_or_flags": "repo", "help": "Repository full name"}],
                "exclusive_group": [],
                "help": "View the content of a repository.",
            },
            {
                "cmd": "list",
                "args": [
                    {
                        "name_or_flags": "--user",
                        "help": "Login name of a user that owns the repository.",
                    },
                    {
                        "name_or_flags": "--limit",
                        "type": _positive_integer,
                        "default": 30,
                        "help": "Maximum number of repositories to fetch. Default 30.",
                    },
                ],
                "exclusive_group": [
                    {
                        "name_or_flags": "--starred",
                        "action": "store_true",
                        "help": "Only repositories starred",
                    },
                    {
                        "name_or_flags": "--watched",
                        "action": "store_true",
                        "help": "Only repositories watched",
                    },
                ],
                "help": "List repositories.",
            },
        ],
        "help": "List repositories or view details of a repository.",
    },
    {
        "cmd": "issue",
        "subcommands": [
            {
                "cmd": "view",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository.",
                    },
                    {
                        "name_or_flags": "number",
                        "type": int,
                        "help": "The number that identifies the issue.",
                    },
                ],
                "exclusive_group": [],
                "help": "View details of an issue.",
            },
            {
                "cmd": "list",
                "args": [
                    {
                        "name_or_flags": "--limit",
                        "type": int,
                        "default": 30,
                        "help": "Maximum number of issues to fetch. Default 30.",
                    }
                ],
                "exclusive_group": [
                    {
                        "name_or_flags": "--org",
                        "help": "Name of the organization that issues in.",
                    },
                    {
                        "name_or_flags": "--account",
                        "action": "store_true",
                        "help": "Only issues across owned and member repositories assigned to the authenticated user.",
                    },
                    {
                        "name_or_flags": "--repo",
                        "help": "Full name of the repository that issues in.",
                    },
                ],
                "help": "List issues that in a repository or assigned to the authenticated user.",
            },
        ],
        "help": "List issues or view details of an issue.",
    },
    {
        "cmd": "pr",
        "subcommands": [
            {
                "cmd": "view",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository.",
                    },
                    {
                        "name_or_flags": "number",
                        "type": int,
                        "help": "The number that identifies the pull request.",
                    },
                ],
                "exclusive_group": [],
                "help": "View details of a pull requests.",
            },
            {
                "cmd": "list",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "Full name of the repository that pull requests in.",
                    },
                    {
                        "name_or_flags": "--commit",
                        "help": "A commit or branch that pull requests associated with.",
                        "metavar": "SHA",
                    },
                    {
                        "name_or_flags": "--limit",
                        "type": int,
                        "default": 30,
                        "help": "Maximum number of pull requests to fetch. Default 30.",
                    },
                ],
                "exclusive_group": [],
                "help": "List pull requests in a repository.",
            },
        ],
        "help": "List pull requests or view details of a pull request.",
    },
    {
        "cmd": "commit",
        "subcommands": [
            {
                "cmd": "view",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository.",
                    },
                    {
                        "name_or_flags": "ref",
                        "help": "The commit reference. Can be a commit SHA, branch name (heads/), or tag name (tags/TAG_NAME).",
                    },
                ],
                "exclusive_group": [],
                "help": "View details of a commit.",
            },
            {
                "cmd": "list",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository.",
                    },
                    {
                        "name_or_flags": "--limit",
                        "type": int,
                        "default": 30,
                        "help": "Maximum number of commits to fetch. Default 30.",
                    },
                ],
                "exclusive_group": [
                    {
                        "name_or_flags": "--pr",
                        "help": "Filter commit by pull request, the option number uniquely identifying the pull request within its repository",
                    },
                    {
                        "name_or_flags": "--start",
                        "help": "SHA or branch to start listing commits from. Default: the repository's default branch (usually main).",
                        "metavar": "SHA",
                    },
                ],
                "help": "List commits in a repository.",
            },
        ],
        "help": "List commits or view details of a commit.",
    },
    {
        "cmd": "branch",
        "subcommands": [
            {
                "cmd": "view",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository.",
                    },
                    {"name_or_flags": "branch", "help": "Branch name."},
                ],
                "exclusive_group": [],
                "help": "View details of a branch.",
            },
            {
                "cmd": "list",
                "args": [
                    {
                        "name_or_flags": "repo",
                        "help": "The full name of the repository that branch in.",
                    },
                    {
                        "name_or_flags": "--head",
                        "help": "The SHA of the commit that is the HEAD, or latest commit for the branch.",
                        "metavar": "SHA",
                    },
                    {
                        "name_or_flags": "--limit",
                        "type": int,
                        "default": 30,
                        "help": "Maximum number of branches to fetch. Default 30.",
                    },
                ],
                "exclusive_group": [],
                "help": "List branches.",
            },
        ],
        "help": "List branches or view details of a branch.",
    },
    {
        "cmd": "ratelimit",
        "args": [],
        "exclusive_group": [],
        "help": "Check rate limit status.",
    },
]
