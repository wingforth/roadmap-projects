def main():
    from number_guessing_game.game import play_game

    rc = 0
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nGame is cancelled by user.")
        rc = 1
    except Exception as e:
        print("\nError:", e)
        rc = 1
    return rc
