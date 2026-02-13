import sys

from crawler.cli import main


if __name__ == "__main__":
    sys.argv = ["crawler", "ingest-all"]
    main()
