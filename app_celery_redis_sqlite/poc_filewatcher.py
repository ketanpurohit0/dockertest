import asyncio
from watchfiles import awatch, Change
from typing import List
import argparse


def filter_specification(change: Change, path: str):
    """Return True if change is to be included, False if ignored

    Args:
        change (Change): The change type
        path (str): The path of changed file
    """
    allowed_file_extensions = ".pdf", ".txt"

    return change == Change.added and path.endswith(allowed_file_extensions)


async def main(paths: List[str]):
    print(f"Watching folder {paths}")
    async for changes in awatch(*paths, watch_filter=filter_specification):
        for change in changes:
            if change[0] == Change.added:
                print(f"Processing {change}")
            else:
                print(f"Ignoring {change}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch folders for new files")
    parser.add_argument('-p', '--paths', nargs="+", help="Required list of paths", required=True)
    args = parser.parse_args()
    print(args)
    asyncio.run(main(args.paths))
