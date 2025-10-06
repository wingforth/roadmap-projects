# Github Activity

A simple and extensible command-line interface (CLI) for interacting with the GitHub REST API. Supports viewing user, repository, issue, pull request, commit, branch, and rate limit information directly from your terminal.

## Features

- List and view GitHub events, users, repositories, issues, pull requests, commits, and branches
- Check API rate limits
- Supports authentication via personal access token

## Requirements

- Python 3.10+
- requests
- Recommended: uv

## Installation

1. Clone this repository with git:

   ```sh
   git clone https://github.com/wingforth/roadmap-projects
   cd roadmap-projects/github-activity
   ```

2. Create a virtual environment and install dependencies (uv required):

   ```sh
   uv sync
   ```

## Authentication

Create a `.env` file in the root directory of project to store environment variables.  
Store your GitHub personal access token in `.env` file like this:

```sh
GITHUB_ACCESS_TOKEN=your-github-access-token
```

Load the environment variables from the `.env` file using **python-dotenv** package.

## Usage

Run the CLI:

```sh
python github_activity.py <command> [options]
```

### Example Commands

- List your events:

  ```sh
  python github_activity.py event --user <username>
  ```

- View a repository:

  ```sh
  python github_activity.py repo view <owner>/<repo>
  ```

- List issues in a repository:

  ```sh
  python github_activity.py issue list --repo <owner>/<repo>
  ```

- View your rate limit:

  ```sh
  python github_activity.py ratelimit
  ```

For more options, use `-h` or `--help` after any command.

## Cache folder

The request caches store in the `data/cache/` directory in the root of module of github_activity.

## FAQ

**Q: How do I get a GitHub personal access token?**  
A: Go to <https://github.com/settings/tokens> and generate a new token with the required scopes.

**Q: How do I clear the cache?**  
A: Delete the `data/cache/` directory in the project root.
