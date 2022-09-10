import asyncio
from watchfiles import awatch, Change
import pathlib

def filter_specification(change: Change, path: str):
    """Return True if change is to be included, False if ignored

    Args:
        change (Change): The change type
        path (str): The path of changed file
    """
    allowed_file_extensions = ".pdf", ".txt"

    return change == Change.added and path.endswith(allowed_file_extensions)

async def main():
    path = pathlib.Path(".", "app_celery_redis_sqlite","source_folder",)
    print(f"Watching folder {path}")
    async for changes in awatch(path, watch_filter=filter_specification):
        for change in changes:
            if change[0] == Change.added:
                print(f"Processing {change}")
            else:
                print(f"Ignoring {change}")

asyncio.run(main())
