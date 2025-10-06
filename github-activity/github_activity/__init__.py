def main():
    from github_activity.cli import GithubCli

    rc = 0
    try:
        GithubCli()
    except KeyboardInterrupt:
        print("\nApplication is canceled by user.")
        rc = 1
    except Exception as e:
        print("\nError:", e)
        rc = 1
    return rc
