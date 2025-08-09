import logging
import os
from pathlib import Path


def _init_file_logging() -> None:
    try:
        # Try app install directory logs; fall back to /var/log/leadershipbutton
        base = Path(os.environ.get("LB_LOG_DIR", Path.cwd() / "logs"))
        base.mkdir(parents=True, exist_ok=True)
        logfile = base / "leadershipbutton.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(logfile, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        logging.getLogger(__name__).info(f"File logging initialized at {logfile}")
    except Exception as exc:
        # Fallback to console only
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning(f"File logging setup failed: {exc}")


def main():
    _init_file_logging()
    # Import here so that logging is configured before any imports with side effects
    from leadership_button.main_loop import MainLoop

    app = MainLoop()
    app.start()


if __name__ == "__main__":
    main()
