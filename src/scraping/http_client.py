import logging
import random
import time

import requests
from requests import Response
from requests.exceptions import (
    ConnectionError,
    RequestException,
    Timeout,
)


logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Base exception for scraping-related failures."""


class ScrapingRetryExhausted(ScrapingError):
    """Raised when all retry attempts have been exhausted."""


class ScrapingPermanentError(ScrapingError):
    """Raised when a request fails and should not be retried."""


class HTTPClient:

    RETRYABLE_STATUS_CODES = {
        408,  # Request Timeout
        425,  # Too Early
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }

    def __init__(
        self,
        timeout: float = 20.0,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        min_request_interval: float = 0.5,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.min_request_interval = min_request_interval

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "EnterpriseLeadIntelligence/1.0 "
                    "(Educational Data Acquisition)"
                )
            }
        )

        self._last_request_time = 0.0

    def _wait_for_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_time

        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed

            logger.debug(
                "Rate limiting: sleeping %.2f seconds",
                sleep_time,
            )

            time.sleep(sleep_time)

    def _calculate_backoff(self, attempt: int) -> float:
        exponential_delay = self.base_delay * (2 ** attempt)

        jitter = random.uniform(
            0,
            self.base_delay,
        )

        delay = exponential_delay + jitter

        return min(
            delay,
            self.max_delay,
        )

    def _get_retry_after(
        self,
        response: Response,
    ) -> float | None:

        retry_after = response.headers.get(
            "Retry-After"
        )

        if not retry_after:
            return None

        try:
            return float(retry_after)
        except ValueError:
            return None

    def get(self, url: str) -> str:

        for attempt in range(
            self.max_retries + 1
        ):

            self._wait_for_rate_limit()

            logger.info(
                "GET %s | attempt %d/%d",
                url,
                attempt + 1,
                self.max_retries + 1,
            )

            try:

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                )

                self._last_request_time = (
                    time.monotonic()
                )

                status_code = response.status_code

                if status_code == 200:

                    logger.info(
                        "GET %s | success",
                        url,
                    )

                    return response.text

                if (
                    status_code
                    in self.RETRYABLE_STATUS_CODES
                ):

                    if attempt >= self.max_retries:
                        raise ScrapingRetryExhausted(
                            f"Retry limit reached for "
                            f"{url}. "
                            f"Last status: "
                            f"{status_code}"
                        )

                    retry_after = (
                        self._get_retry_after(
                            response
                        )
                    )

                    delay = (
                        retry_after
                        if retry_after is not None
                        else self._calculate_backoff(
                            attempt
                        )
                    )

                    logger.warning(
                        "GET %s | status %d | "
                        "retrying in %.2f seconds",
                        url,
                        status_code,
                        delay,
                    )

                    time.sleep(delay)

                    continue

                response.raise_for_status()

                raise ScrapingPermanentError(
                    f"Unexpected response for "
                    f"{url}: {status_code}"
                )

            except Timeout as exc:

                if attempt >= self.max_retries:

                    raise ScrapingRetryExhausted(
                        f"Timeout retry limit "
                        f"reached for {url}"
                    ) from exc

                delay = self._calculate_backoff(
                    attempt
                )

                logger.warning(
                    "GET %s | timeout | "
                    "retrying in %.2f seconds",
                    url,
                    delay,
                )

                time.sleep(delay)

            except ConnectionError as exc:

                if attempt >= self.max_retries:

                    raise ScrapingRetryExhausted(
                        f"Connection retry limit "
                        f"reached for {url}"
                    ) from exc

                delay = self._calculate_backoff(
                    attempt
                )

                logger.warning(
                    "GET %s | connection error | "
                    "retrying in %.2f seconds",
                    url,
                    delay,
                )

                time.sleep(delay)

            except RequestException as exc:

                raise ScrapingPermanentError(
                    f"Request failed for {url}: {exc}"
                ) from exc

        raise ScrapingRetryExhausted(
            f"Unable to retrieve {url}"
        )


def fetch_page(url: str) -> str:
    """
    Backward-compatible helper.

    Existing scraper code can continue calling
    fetch_page(url).
    """

    client = HTTPClient()

    return client.get(url)