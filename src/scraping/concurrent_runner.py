from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

from src.scraping.page_worker import (
    PageJob,
    PageResult,
    fetch_page,
)


class ConcurrentPageRunner:

    def __init__(
        self,
        http_get,
        max_workers: int = 3,
    ):

        self.http_get = http_get
        self.max_workers = max_workers

    def run(
        self,
        jobs: list[PageJob],
    ) -> list[PageResult]:

        results = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:

            futures = {
                executor.submit(
                    fetch_page,
                    job,
                    self.http_get,
                ): job
                for job in jobs
            }

            for future in as_completed(futures):

                job = futures[future]

                try:

                    result = future.result()

                    results.append(result)

                except Exception as exc:

                    results.append(
                        PageResult(
                            page_number=job.page_number,
                            page_url=job.page_url,
                            error=exc,
                        )
                    )

        return sorted(
            results,
            key=lambda result: result.page_number,
        )