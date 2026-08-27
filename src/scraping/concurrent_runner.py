from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

from src.scraping.page_worker import (
    PageJob,
    PageResult,
)


class ConcurrentPageRunner:

    def __init__(
        self,
        max_workers: int = 5,
    ):

        self.max_workers = max_workers

    def run(
        self,
        jobs: list[PageJob],
        worker_function,
    ) -> list[PageResult]:

        results = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:

            futures = {
                executor.submit(
                    worker_function,
                    job,
                ): job
                for job in jobs
            }

            for future in as_completed(
                futures
            ):

                job = futures[future]

                try:

                    result = future.result()

                    results.append(result)

                except Exception as exc:

                    print(
                        f"[WORKER ERROR] "
                        f"Page {job.page_number}: "
                        f"{exc}"
                    )

        return results