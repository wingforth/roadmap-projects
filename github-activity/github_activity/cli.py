# -*- coding: utf-8 -*-
"""
A simple command line interface (CLI) to interact with GitHub REST API.
"""

from argparse import ArgumentParser, Namespace, SUPPRESS

from github_activity.rest_api import Event, RateLimit, Repository, User, Issue, PullRequest, Commit, Branch
from github_activity.commands import commands
from github_activity.config import CACHE_DIR, GITHUB_TOKEN


class GithubCli:
    """A command line interface to interact with GitHub REST API.

    Handles argument parsing and command dispatching.
    """

    def __init__(self) -> None:
        """Initializes the GitHubCLI instance and parses command-line arguments."""
        self.headers: dict[str, str] = {}
        self.parse_arguments()

    def parse_arguments(self) -> None:
        """Parses command-line arguments and dispatches to the appropriate handler."""
        parser = ArgumentParser(prog="github-activity")
        self.add_subcommands(parser, commands, [])
        args = parser.parse_args()
        handler = getattr(args, "handler", None)
        if handler:
            getattr(self, handler)(args)
        else:
            parser.print_help()

    def add_subcommands(self, parser: ArgumentParser, commands: list[dict], parents: list[str]) -> None:
        """Recursively adds subcommands to the argument parser.

        Args:
            parser (ArgumentParser): The argument parser to add subcommands to.
            commands (list[dict]): List of command definitions.
            parents (list[str]): List of parent command names.
        """
        subparsers = parser.add_subparsers(required=True)
        for command in commands:
            name = command.pop("cmd")
            sub_parser = subparsers.add_parser(name, argument_default=SUPPRESS, help=command.pop("help"))
            parents.append(name)
            if sub_commands := command.pop("subcommands", None):
                self.add_subcommands(sub_parser, sub_commands, parents)
            self.add_arguments(sub_parser, command, parents)
            parents.pop()

    def add_arguments(self, parser: ArgumentParser, command_args: dict, parents: list[str]) -> None:
        """Adds arguments and mutually exclusive groups to a parser for a command.

        Args:
            parser (ArgumentParser): The argument parser to add arguments to.
            command_args (dict): Dictionary of argument definitions.
            parents (list[str]): List of parent command names.
        """
        parser.set_defaults(handler="handle_" + "_".join(parents))
        for arg in command_args.pop("args", []):
            parser.add_argument(arg.pop("name_or_flags"), **arg)
        exclusive_args = command_args.pop("exclusive_group", [])
        if not exclusive_args:
            return
        exclusive_group = parser.add_mutually_exclusive_group()
        for arg in exclusive_args:
            exclusive_group.add_argument(arg.pop("name_or_flags"), **arg)

    def handle_event(self, args: Namespace):
        """Handles the 'event' command to list GitHub events for a user or repository.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        match vars(args):
            case {"user": username, "received": True}:
                endpoint = "list_events_received_by_the_authenticated_user"
                params = {"username": username}
                title = f"User {username} received events by watching repositories and following users:"
            case {"user": username}:
                endpoint = "list_events_for_the_authenticated_user"
                params = {"username": username}
                title = f"Events for user {username}:"
            case {"repo": repo_full_name, "received": True}:
                print("github-activity event: error: argument --received: not allowed with argument --repo")
                return
            case {"repo": repo_full_name}:
                endpoint = "list_repository_events"
                owner, _, repo = repo_full_name.partition("/")
                params = {"owner": owner, "repo": repo}
                title = f"Events in repository {repo_full_name}:"
            case _:
                print("github-activity event: error: either --user or --repo argument is required.")
                return
        Event(
            endpoint,
            path_params=params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_events(title)

    def handle_user(self, args: Namespace):
        """Handles the 'user' command to view user profile information.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        match vars(args):
            case {"name": username}:
                endpoint = "get_a_user"
                params = {"username": username}
            case {"id": id}:
                endpoint = "get_a_user_using_their_ID"
                params = {"account_id": id}
            case _:
                endpoint = "get_the_authenticated_user"
                params = {}
        User(
            endpoint,
            path_params=params,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_user()

    def handle_repo_view(self, args: Namespace):
        """Handles the 'repo view' command to view repository details.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        endpoint = "get_a_repository"
        owner, _, repo = args.repo.partition("/")
        Repository(
            endpoint,
            path_params={"owner": owner, "repo": repo},
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_repo()

    def handle_repo_list(self, args: Namespace):
        """Handles the 'repo list' command to list repositories for a user or the authenticated user.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        params = {}
        match vars(args):
            case {"user": username, "starred": True}:
                endpoint = "list_repositories_starred_by_a_user"
                params = {"username": username}
                title = f"Repositories starred by {username}:"
            case {"user": username, "watched": True}:
                endpoint = "list_repositories_watched_by_a_user"
                params = {"username": username}
                title = f"Repositories watched by {username}:"
            case {"user": username}:
                endpoint = "list_repositories_for_a_user"
                params = {"username": username}
                title = f"{username}'s repositories:"
            case {"starred": True}:
                endpoint = "list_repositories_starred_by_the_authenticated_user"
                title = "Starred Repositories:"
            case {"watched": True}:
                endpoint = "list_repositories_watched_by_the_authenticated_user"
                title = "Watched Repositories:"
            case _:
                endpoint = "list_repositories_for_the_authenticated_user"
                title = "Repositories:"
        Repository(
            endpoint,
            path_params=params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_repos(title)

    def handle_issue_view(self, args: Namespace):
        """Handles the 'issue view' command to view details of a specific issue.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        endpoint = "get_an_issue"
        owner, _, repo = args.repo.partition("/")
        Issue(
            endpoint,
            path_params={"owner": owner, "repo": repo, "issue_number": args.number},
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_issue()

    def handle_issue_list(self, args: Namespace):
        """Handles the 'issue list' command to list issues for a repository, organization, or user.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        params = {}
        match vars(args):
            case {"repo": repo_full_name}:
                endpoint = "list_repository_issues"
                owner, _, repo = repo_full_name.partition("/")
                params = {"owner": owner, "repo": repo}
                title = f"Issues in repository {repo_full_name}:"
            case {"org": org}:
                endpoint = "list_organization_issues_assigned_to_the_authenticated_user"
                params = {"org": org}
                title = f"Assigned issues in organization {org}:"
            case {"account": True}:
                endpoint = "list_user_account_issues_assigned_to_the_authenticated_user"
                title = "Assigned issues across owned and member repositories:"
            case _:
                endpoint = "list_issues_assigned_to_the_authenticated_user"
                title = "Assigned issues:"

        Issue(
            endpoint,
            path_params=params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_issues(title)

    def handle_pr_view(self, args: Namespace):
        """Handles the 'pr view' command to view details of a pull request.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        endpoint = "get_a_pull_request"
        owner, _, repo = args.repo.partition("/")
        PullRequest(
            endpoint,
            path_params={"owner": owner, "repo": repo, "pull_number": args.number},
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_pull_request()

    def handle_pr_list(self, args: Namespace):
        """Handles the 'pr list' command to list pull requests for a repository or associated with a commit.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        owner, _, repo = args.repo.partition("/")
        params = {"owner": owner, "repo": repo}
        match vars(args):
            case {"commit": commit_sha}:
                endpoint = "list_pull_requests_associated_with_a_commit"
                params["commit_sha"] = commit_sha
                title = f"Pull requests associated commit {commit_sha} in repository {args.repo}:"
            case _:
                endpoint = "list_pull_requests"
                title = f"Pull requests in repository {args.repo}:"

        PullRequest(
            endpoint,
            path_params=params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_pull_requests(title)

    def handle_commit_view(self, args: Namespace):
        """Handles the 'commit view' command to view details of a specific commit.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        endpoint = "get_a_commit"
        owner, _, repo = args.repo.partition("/")
        params = {"owner": owner, "repo": repo, "ref": args.ref}
        Commit(
            endpoint,
            path_params=params,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_commit()

    def handle_commit_list(self, args: Namespace):
        """Handles the 'commit list' command to list commits for a repository, pull request, or starting from a SHA.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        owner, _, repo = args.repo.partition("/")
        path_params = {"owner": owner, "repo": repo}
        query_params = {}
        match vars(args):
            case {"pr": pull_number}:
                endpoint = "list_commits_on_a_pull_request"
                path_params["pull_number"] = pull_number
                title = f"Commits on pull request {pull_number} in repository {args.repo}:"
            case {"start": sha}:
                endpoint = "list_commits"
                query_params["sha"] = sha
                title = f"Commits start from {args.start} in repository {args.repo}:"
            case _:
                endpoint = "list_commits"
                title = f"Commits in repository {args.repo}:"
        Commit(
            endpoint,
            path_params=path_params,
            query_params=query_params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_commits(title)

    def handle_branch_view(self, args: Namespace):
        """Handles the 'branch view' command to view details of a specific branch.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        owner, _, repo = args.repo.partition("/")
        endpoint = "get_a_branch"
        Branch(
            endpoint,
            path_params={"owner": owner, "repo": repo, "branch": args.branch},
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_branch()

    def handle_branch_list(self, args: Namespace):
        """Handles the 'branch list' command to list branches for a repository or for a specific commit SHA.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        owner, _, repo = args.repo.partition("/")
        params = {"owner": owner, "repo": repo}
        match vars(args):
            case {"head": commit_sha}:
                endpoint = "list_branches_for_HEAD_commit"
                params["commit_sha"] = commit_sha
                title = f"Branches that {commit_sha} is the HEAD or last commit in repository {args.repo}:"
            case _:
                endpoint = "list_branches"
                title = f"Branches in repository {args.repo}:"
        Branch(
            endpoint,
            path_params=params,
            limit=args.limit,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).list_branches(title)

    def handle_ratelimit(self, args: Namespace):
        """Handles the 'ratelimit' command to display the current rate limit status for the authenticated user.

        Args:
            args (Namespace): Parsed command-line arguments.
        """
        endpoint = "get_rate_limit_status_for_the_authenticated_user"
        RateLimit(
            endpoint,
            auth=GITHUB_TOKEN,
            cache_dir=CACHE_DIR,
        ).view_rate_limit_status()
