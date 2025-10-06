"""
Github REST API module
"""

from time import strftime, localtime
from collections import namedtuple
from urllib.parse import quote
from json import load, dump
from typing import Any, Generator
from pathlib import Path

from requests import RequestException, Session, Response, HTTPError

from github_activity.github_event import GithubEvent

# Cache Keys Class
CacheKeys = namedtuple("CacheKeys", ("etag", "last_modified", "next_page"), defaults=(None, None, None))


class GithubCache:
    """Cache of the http request to GitHub REST API.

    Args:
        url (str): The url that request to.
        cache_dir (Path | str): The path of the cache directory.

    Raises:
        TypeError: If cache directory is not an object of str or Path.
        NotADirectoryError: If cache directory is not a directory.

    Attributes:
        cache_dir (Path): The directory where caches are stored.
        __session (str): The session's url removed common prefix that.
        __history (Path): The file storing all request sessions of GitHub REST API.
        __cache (dict[str, CacheKeys]): A dictionary that contains cache keys of request session.
        __updated (bool): Mark whether the cache has been updated after new response has been stored.

    Class Attributes:
        url_common_prefix (str): The base url of GitHub REST API endpoints.
    """

    url_common_prefix = "https://api.github.com"

    def __init__(self, url: str, cache_dir: Path | str) -> None:
        """Initializes the GithubCache object.

        Args:
            url (str): The url to request.
            cache_dir (Path | str): The cache directory.
        """
        if not isinstance(cache_dir, (str, Path)):
            raise TypeError("Argument `cache_dir` should be a str or Path object.")
        self.cache_dir: Path = Path(cache_dir) if isinstance(cache_dir, str) else cache_dir
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        elif not self.cache_dir.is_dir():
            raise NotADirectoryError("Path `cache_dir` is not a directory.")
        self.__session: str = self._shorten_url(url)
        self.__history: Path = self.cache_dir / ".session"
        if not self.__history.exists():
            with open(self.__history, mode="w", encoding="utf-8") as fd:
                dump({}, fd, indent=4)
            cache = {}
        else:
            with open(self.__history, mode="r", encoding="utf-8") as fd:
                cache = load(fd).get(self.__session, {})
        self.__cache: dict[str, CacheKeys] = {url: CacheKeys(**cache_keys) for url, cache_keys in cache.items()}
        self.__updated: bool = True

    @staticmethod
    def _shorten_url(url: str) -> str:
        """Shorten url by removing common prefix.

        Args:
            url (str): Original URL.

        Returns:
            str: URL removed common prefix.
        """
        return url.removeprefix(GithubCache.url_common_prefix)

    def _path(self, url: str) -> Path:
        """Get the cached response json file of the request to url.

        Args:
            url (str): URL of the request.

        Returns:
            Path: The file storing the response.
        """
        return self.cache_dir / (quote(self._shorten_url(url), safe="") + ".json")

    def load_cache(self, url: str) -> Any:
        """Load the cached data of the request to url.

        Args:
            url (str): URL of the request.

        Returns:
            Any: The cached response json data.
        """
        with open(self._path(url), mode="r", encoding="utf-8") as fd:
            return load(fd)

    def store_response(
        self,
        url: str,
        data: Any,
        etag: str | None = None,
        last_modified: str | None = None,
        next_page: str | None = None,
    ) -> None:
        """Store the response of the request to url.

        Args:
            url (str): URL of the request.
            data (Any): The response json data of the request.
            etag (str | None, optional): The response header `ETag`. Defaults to None.
            last_modified (str | None, optional): The response header `last-modified`. Defaults to None.
            next_page (str | None, optional): The url of the next page if the response is paginated. Defaults to None.
        """
        key = self._shorten_url(url)
        # if next page url changed, delete the cache of next page url.
        stale_next_page = self.__cache.get(key, CacheKeys()).next_page
        if stale_next_page and stale_next_page != next_page:
            self.__cache.pop(stale_next_page, None)
            self._path(stale_next_page).unlink(missing_ok=True)
        # update cache keys.
        self.__cache[key] = CacheKeys(etag, last_modified, next_page)
        # store response json data.
        with open(self._path(url), mode="w", encoding="utf-8") as fd:
            dump(data, fd, indent=4)
        # Marking cache needs to be updated by setting self.updated to False.
        self.__updated = False

    def get_cache_keys(self, url: str) -> CacheKeys:
        """Get the cache keys for the response of url.

        Args:
            url (str): URL of the request.

        Returns:
            CacheKeys: Cache keys, a namedtuple contains etag, last-modified, next page url.
        """
        return self.__cache.get(self._shorten_url(url), CacheKeys())

    def update_cache(self) -> None:
        """Update cache keys in .session file."""
        if self.__updated:
            return
        with open(self.__history, mode="r", encoding="utf-8") as fd:
            caches = load(fd)
        caches[self.__session] = {url: cache_keys._asdict() for url, cache_keys in self.__cache.items()}
        with open(self.__history, mode="w", encoding="utf-8") as fd:
            dump(caches, fd, indent=4)
        # Marking cache has been updated.
        self.__updated = True


class RestApi:
    """GitHub REST API.

    Args:
        endpoint (str): Github REST API endpoint name.
        path_params (dict | None, optional): Path parameters of url. Defaults to None.
        query_params (dict | None, optional): Query parameters of url. Defaults to None.
        headers (dict | None, optional): The headers of http request. Defaults to None.
        limit (int | None, optional): The count of the result required. Defaults to None.
        cache_dir (Path | str | None, optional): The cache directory of the http request. Defaults to None.

    Attributes:
        url (str): URL of the http request.
        headers (dict): The headers of the http request.
        limit (int | None): The count of the result required if the response is paginated, otherwise None.
        __cache (GithubCache): The cache of the http request.
        json_data (Any): The response json data.

    Class Attributes:
        base_url (str): The base url of GitHub REST API endpoints.
        endpoints (dict[str, str]): A dict object contains GitHub REST API endpoint urls.
    """

    base_url = "https://api.github.com"
    endpoints = {
        # activity
        "list_repository_events": "/repos/{owner}/{repo}/events",
        "list_events_for_the_authenticated_user": "/users/{username}/events",
        "list_events_received_by_the_authenticated_user": "/users/{username}/received_events",
        # user
        "get_the_authenticated_user": "/user",
        "get_a_user": "/users/{username}",
        "get_a_user_using_their_ID": "/user/{account_id}",
        # repo
        "get_a_repository": "/repos/{owner}/{repo}",
        # "list_organization_repositories": "/orgs/{org}/repos",
        "list_repositories_for_the_authenticated_user": "/user/repos",
        "list_repositories_starred_by_the_authenticated_user": "/user/starred",
        "list_repositories_watched_by_the_authenticated_user": "/user/subscriptions",
        "list_repositories_for_a_user": "/users/{username}/repos",
        "list_repositories_starred_by_a_user": "/users/{username}/starred",
        "list_repositories_watched_by_a_user": "/users/{username}/subscriptions",
        # issue
        "get_an_issue": "/repos/{owner}/{repo}/issues/{issue_number}",
        "list_repository_issues": "/repos/{owner}/{repo}/issues",
        "list_organization_issues_assigned_to_the_authenticated_user": "/orgs/{org}/issues",
        "list_issues_assigned_to_the_authenticated_user": "/issues",
        "list_user_account_issues_assigned_to_the_authenticated_user": "/user/issues",
        # pull request
        "get_a_pull_request": "/repos/{owner}/{repo}/pulls/{pull_number}",
        "list_pull_requests": "/repos/{owner}/{repo}/pulls",
        "list_pull_requests_associated_with_a_commit": "/repos/{owner}/{repo}/commits/{commit_sha}/pulls",
        # commit
        "get_a_commit": "/repos/{owner}/{repo}/commits/{ref}",
        "list_commits": "/repos/{owner}/{repo}/commits",
        "list_commits_on_a_pull_request": "/repos/{owner}/{repo}/pulls/{pull_number}/commits",
        # branch
        "get_a_branch": "/repos/{owner}/{repo}/branches/{branch}",
        "list_branches": "/repos/{owner}/{repo}/branches",
        "list_branches_for_HEAD_commit": "/repos/{owner}/{repo}/commits/{commit_sha}/branches-where-head",
        # ratelimit
        "get_rate_limit_status_for_the_authenticated_user": "/rate_limit",
    }

    def __init__(
        self,
        endpoint: str,
        *,
        path_params: dict | None = None,
        query_params: dict | None = None,
        headers: dict | None = None,
        limit: int | None = None,
        auth: str | None = None,
        cache_dir: Path | str | None = None,
    ) -> None:
        """Initializes the RestApi object.

        Args:
            endpoint (str): Github REST API endpoint name.
            path_params (dict | None, optional): Path parameters of url. Defaults to None.
            query_params (dict | None, optional): Query parameters of url. Defaults to None.
            headers (dict | None, optional): The headers of http request. Defaults to None.
            limit (int | None, optional): The count of the result required. Defaults to None.
            cache_dir (Path | str | None, optional): The cache directory of the http request. Defaults to None.
        """
        if endpoint not in RestApi.endpoints:
            print(f"Unknown endpoint: '{endpoint}'.")
            return

        url_path = RestApi.endpoints[endpoint].format(**path_params) if path_params else RestApi.endpoints[endpoint]
        queries = []
        if query_params:
            for key, val in query_params.items():
                if isinstance(val, list):
                    queries.extend(f"{key}={v}" for v in val)
                else:
                    queries.append(f"{key}={val}")
        self.url: str = (
            f"{RestApi.base_url}{url_path}?{'&'.join(queries)}" if queries else f"{RestApi.base_url}{url_path}"
        )

        self.headers: dict = headers or {}
        if not auth:
            print("Warning: you are not authenticated to the REST API.")
        else:
            self.headers["Authorization"] = f"Bearer {auth}"
        self.limit: int | None = limit
        self.__cache: GithubCache = GithubCache(self.url, cache_dir or Path(__file__).resolve().parent)

    def fetch_data(self) -> Any:
        """Fetch response json data. And cache the response json data.

        Returns:
            Any: Response json data.
        """
        if self.limit:
            data = []
            for page in self.iter_paginated_data():
                data.extend(page)
            return data

        with Session() as session:
            session.headers.update(self.headers)
            self._conditional_request(session, self.__cache.get_cache_keys(self.url))
            resp = self._make_request(session, self.url)
            # 304: Not Modified
            # 200: OK
            if resp is None or resp.status_code not in (200, 304):
                return None
            if resp.status_code == 200:
                data = resp.json()
                self.__cache.store_response(self.url, data, resp.headers.get("etag"), resp.headers.get("last-modified"))
                self.__cache.update_cache()
            else:
                data = self.__cache.load_cache(self.url)
        return data

    def iter_paginated_data(self) -> Generator[list]:
        """Iteratively fetch json data of the paginated response. And cache every page data of the response.

        Yields:
            Generator[list]: Json data of the paginated response.
        """
        if self.limit is None:
            print("Response is not paginated.")
            return
        url, remaining = self.url, self.limit
        with Session() as session:
            session.headers.update(self.headers)
            while url:
                cache_keys = self.__cache.get_cache_keys(url)
                self._conditional_request(session, cache_keys)
                resp = self._make_request(session, url)
                # 304: Not Modified
                # 200: OK
                if resp is None or resp.status_code not in (200, 304):
                    break
                if resp.status_code == 200:
                    data = resp.json()
                    next_page_url = self._get_next_page_url(resp)
                    self.__cache.store_response(
                        url, data, resp.headers.get("etag"), resp.headers.get("last-modified"), next_page_url
                    )
                else:
                    data = self.__cache.load_cache(url)
                    next_page_url = cache_keys.next_page

                remaining -= len(data)
                if remaining <= 0:
                    yield data[: None if remaining == 0 else remaining]
                    break
                yield data
                url = next_page_url
        self.__cache.update_cache()

    def _make_request(self, session: Session, url: str) -> Response | None:
        """Make a request to url.

        Args:
            session (Session): The request session.
            url (str): URL for the request.

        Returns:
            Response | None: The Response object of the http request, or None if an error occurred.
        """
        try:
            resp = session.get(url, timeout=10)
        except RequestException as e:
            print("Request Error:", e)
            return None
        try:
            resp.raise_for_status()
        except HTTPError as e:
            print("Http Error:", e)
            self._check_rate_limit(resp)
        else:
            if resp.is_redirect:
                return self._make_request(session, resp.headers["location"])
        return resp

    @staticmethod
    def _conditional_request(session: Session, cache_keys: CacheKeys) -> None:
        """Set session's headers `Etag` and `Last-Modified` for conditional request.

        Args:
            session (Session): A Requests session.
            cache_keys (CacheKeys): A namedtuple contains etag, last-modified and next page url.
        """
        if cache_keys.etag:
            session.headers["if-none-match"] = cache_keys.etag
        else:
            session.headers.pop("if-none-match", None)
        if cache_keys.last_modified:
            session.headers["if-modified-since"] = cache_keys.last_modified
        else:
            session.headers.pop("if-modified-since", None)

    @staticmethod
    def _get_next_page_url(resp: Response) -> str | None:
        """Get the next page url of the paginated response from the header `Link` of the response.

        Args:
            resp (Response): The Response object of the http request.

        Returns:
            str | None: The next page url if the paginated response has a next page, otherwise None.
        """
        if not (links := resp.headers.get("link")):
            return None
        for page in links.split(", "):
            url, _, rel = page.partition("; ")
            *_, rel = rel.partition("=")
            if rel.strip(" \"'") == "next":
                return url.strip(" <>")
        return None

    @staticmethod
    def _check_rate_limit(resp: Response):
        """Check whether rate limit is exceeded.

        Args:
            resp (Response): The Response object of the http request.
        """
        # 429: Too Many Requests
        # 403: Forbidden
        if resp.status_code not in (429, 403):
            return

        headers = resp.headers
        if headers.get("x-ratelimit-remaining") == "0":
            print(
                f"API primary rate limit for resource '{headers['x-ratelimit-resource']}' exhausted,",
                f"it will reset at {strftime('%H:%M:%S', localtime(int(headers['x-ratelimit-reset'])))}.",
            )
        elif retry_after := headers.get("retry-after"):
            print(
                f"API secondary rate limit for resource '{headers['x-ratelimit-resource']}' exceeded,",
                f"retry after {int(retry_after)} seconds.",
            )


class Event(RestApi):
    """Represents GitHub event activity operations for listing and displaying events."""

    def list_events(self, title: str | None) -> None:
        """Prints a list of GitHub events grouped by date.

        Args:
            title (str | None): Title of the event list.
        """
        if title:
            print(title)
        curr_date = None
        for page in self.iter_paginated_data():
            for event in map(GithubEvent, page):
                if curr_date != event.created_date:
                    curr_date = event.created_date
                    print(f"-- {curr_date} --")
                print(f"{event.created_time}  {event.description}")


class User(RestApi):
    """Represents GitHub user operations for displaying user information."""

    def view_user(self) -> None:
        """Prints details of a GitHub user."""
        if not (user := self.fetch_data()):
            return
        print(user["login"], f"(id: {user['id']})", f"<{user['type']}>")
        print("following", user["following"], "users , followed by", user["followers"], "users")
        print(
            f"public repos: {user['public_repos']}",
            f"private repos: {private_repos}" if (private_repos := user.get("owned_private_repos")) else "",
        )
        for item in ("name", "company", "blog", "location", "email", "bio"):
            if val := user[item]:
                print(f"{item:9}: {val}")
            # print(f"{item:9}: {user[item]}")
        if twitter := user["twitter_username"]:
            print(f"{'twitter':9}: {twitter}")
        print("View this user on GitHub:", user["html_url"])


class Repository(RestApi):
    """Represents GitHub repository operations for listing and displaying repositories."""

    def list_repos(self, title: str | None) -> None:
        """Prints a list of repositories with their descriptions.

        Args:
            title (str | None): Title of the repository list.
        """
        if title:
            print(title)
        fmt = "{:30}    {}".format
        print(fmt("name", "description"))
        print(fmt("----", "-----------"))
        for page in self.iter_paginated_data():
            for repo in page:
                print(fmt(repo["full_name"], repo["description"] or ""))

    def view_repo(self) -> None:
        """Prints details of a GitHub repository."""
        if not (repo := self.fetch_data()):
            return
        print(repo["full_name"], f"(id: {repo['id']})")
        if repo["archived"]:
            print("ARCHIVED")
        print(repo["subscribers_count"], "watching,", repo["forks_count"], "forks,", repo["stargazers_count"], "stars")
        if topics := repo["topics"]:
            print("topics:", *topics)
        print("Description:", repo["description"])
        print("View this repository on GitHub:", repo["html_url"])


class Issue(RestApi):
    """Represents GitHub issue operations for listing and displaying issues."""

    def list_issues(self, title: str | None) -> None:
        """Prints a list of issues with their numbers, titles, and labels.

        Args:
            title (str | None): Title of the issue list.
        """
        if title:
            print(title)
        fmt = "{:7}  {:60}    {}".format
        print(fmt("number", "title", "labels"))
        print(fmt("------", "-----", "------"))
        fmt = "#{:<6}  {:60}    {}".format
        for page in self.iter_paginated_data():
            for issue in page:
                print(fmt(issue["number"], issue["title"], tuple(label["name"] for label in issue["labels"])))

    def view_issue(self) -> None:
        """Prints details of a GitHub issue."""
        if not (issue := self.fetch_data()):
            return
        print(issue["title"])
        print(f"opened by {issue['user']['login']} on {issue['created_at'][:10]}. {issue['comments']} comments.")
        if labels := tuple(label["name"] for label in issue["labels"]):
            print("labels:", *labels)
        if issue["state"] == "closed":
            print(f"closed as {issue['state_reason']} by {issue['closed_by']['login']} on {issue['closed_at'][:10]}")
        reactions = issue["reactions"]
        print(
            *(
                f"{reactions[reaction]} {reaction}"
                for reaction in ("+1", "-1", "laugh", "hooray", "confused", "heart", "rocket", "eyes")
            ),
            sep=", ",
        )
        print("\n", issue["body"], "\n")
        print("View this issue on GitHub:", issue["html_url"])


class PullRequest(RestApi):
    """Represents GitHub pull request operations for listing and displaying pull requests."""

    def list_pull_requests(self, title: str | None) -> None:
        """Prints a list of pull requests with their numbers, titles, and labels.

        Args:
            title (str | None): Title of the pull request list.
        """
        if title:
            print(title)
        fmt = "{:7}  {:60}    {}".format
        print(fmt("number", "title", "labels"))
        print(fmt("------", "-----", "------"))
        fmt = "#{:<6}  {:60}    {}".format
        for page in self.iter_paginated_data():
            for pull_request in page:
                print(
                    fmt(
                        pull_request["number"],
                        pull_request["title"],
                        tuple(label["name"] for label in pull_request["labels"]),
                    )
                )

    def view_pull_request(self) -> None:
        """Prints details of a GitHub pull request."""
        if not (pr := self.fetch_data()):
            return
        print(pr["title"])
        print(f"opened by {pr['user']['login']} on {pr['created_at'][:10]}. {pr['comments']} comments.")

        if labels := tuple(label["name"] for label in pr["labels"]):
            print("labels:", *labels)
        if pr["merged"]:
            print(f"merged by {pr['merged_by']['login']} on {pr['merged_at'][:10]}")
        print(
            pr["commits"],
            "commits,",
            pr["additions"],
            "additions,",
            pr["deletions"],
            "deletions,",
            pr["changed_files"],
            "files changed.",
        )
        print(pr["comments"], "comments,", pr["review_comments"], "review comments.")
        print("\n", pr["body"], "\n")
        print("View this pull request on GitHub:", pr["html_url"])


class Commit(RestApi):
    """Represents GitHub commit operations for listing and displaying commits."""

    def list_commits(self, title: str | None) -> None:
        """Prints a list of commit SHAs.

        Args:
            title (str | None): Title of the commit list.
        """
        if title:
            print(title)
        print("Commit SHA")
        print("----------")
        for page in self.iter_paginated_data():
            for commit in page:
                print(commit["sha"])

    def view_commit(self) -> None:
        """Prints details of a GitHub commit."""
        if not (commit := self.fetch_data()):
            return
        print(commit["sha"])
        print(f"author: {commit['author']['login']}, committer: {commit['committer']['login']}")
        print("total changes:", commit["stats"]["additions"], "additions,", commit["stats"]["deletions"], "deletions")
        print(len(commit["files"]), "files changed:")
        for file in commit["files"]:
            print("-", file["filename"], ":", file["additions"], "additions,", file["deletions"], "deletions")
        print("\n", commit["commit"]["message"], "\n")
        print("View this commit on GitHub:", commit["html_url"])


class Branch(RestApi):
    """Represents GitHub branch operations for listing and displaying branches."""

    def list_branches(self, title: str | None) -> None:
        """Prints a list of branches with their names and SHAs.

        Args:
            title (str | None): Title of the branch list.
        """
        if title:
            print(title)
        fmt = "{:50}    {}".format
        print(fmt("branch", "SHA"))
        print(fmt("------", "---"))
        for page in self.iter_paginated_data():
            for branch in page:
                print(fmt(branch["name"], branch["commit"]["sha"]))

    def view_branch(self) -> None:
        """Prints details of a GitHub branch."""
        if not (branch := self.fetch_data()):
            return
        print(branch["name"])
        print("SHA:", branch["commit"]["sha"])
        print("View this branch on GitHub:", branch["_links"]["html"])


class RateLimit(RestApi):
    """Represents GitHub rate limit operations for displaying rate limit status."""

    def view_rate_limit_status(self):
        """Prints the current rate limit status for the authenticated user."""
        if not (rate_limit := self.fetch_data()):
            return
        print("Rate Limit Overview:")
        fmt = "{:27}  {:<6}  {:<6}  {:<9}  {}".format
        print(fmt("resource", "limit", "used", "remaining", "reset_at"))
        print(fmt("--------", "-----", "----", "---------", "-----"))
        fmt = "{:27}  {:<6,}  {:<6,}  {:<9,}  {}".format
        for resource, ratelimit in rate_limit["resources"].items():
            print(
                fmt(
                    resource,
                    *(int(ratelimit[item]) for item in ("limit", "used", "remaining")),
                    strftime("%H:%M:%S", localtime(int(ratelimit["reset"]))),
                )
            )
