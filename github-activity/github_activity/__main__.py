import sys

# If the module is run as a script or the __main__ file of the module is directly executed,
# import github_activity module manually.
if not __spec__ or not __spec__.parent:
    from pathlib import Path

    path = Path(__file__).resolve().parent
    if sys.path[0] == str(path):
        sys.path[0] = str(path.parent)
    else:
        sys.path.insert(0, str(path.parent))

    import github_activity

    sys.path.pop(0)
else:
    import github_activity

sys.exit(github_activity.main())
