"""Import local service settings directly from a source checkout."""
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from deal_survey.settings import main

    main()
