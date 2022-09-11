import asyncio
from watchfiles import awatch, Change
from typing import List
import argparse
from poc_worker1 import process_pdf, process_other, process_retry, process_timelimited, process_in_future


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
            _, path = change
            if path.endswith(".pdf"):
                process_pdf.delay(path)
            else:
                process_other.delay(path)
            # This task has 50:50 chance of failng,and will be retried
            # see the code
            process_retry.delay()

            # This task has a 40% chance of failing due to timeout
            process_timelimited.delay()

            # This task will be queued for processing in 15 seconds
            process_in_future.apply_async((), countdown=15)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch folders for new files")
    parser.add_argument('-p', '--paths', nargs="+", help="Required list of paths", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.paths))

# python poc_filewatcher.py -p ./source_folder
# celery --broker "redis://redis:6379/0" --result-backend "redis://redis:6379/0" flower
