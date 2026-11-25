"""Start the reader directly from a source checkout."""
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from deal_survey.server import main

    main()
