def main():
    from expense_tracker.cli import CLI

    rc = 0
    try:
        CLI().run()
    except KeyboardInterrupt:
        print("\nApplication is canceled by user.")
        rc = 1
    except Exception as e:
        print("\nError:", e)
        rc = 1
    return rc
