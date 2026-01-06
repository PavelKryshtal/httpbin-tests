from urllib.parse import urljoin
import logging
import requests

from utils.retry import retry, RetryConfig

logger = logging.getLogger(__name__)


class GetRequest:
    @retry(
        config=RetryConfig(
            attempts=3,
            delay=0.5,
            backoff=2.0,
            retry_on=(requests.RequestException,),
        ),
        logger=logger,
    )
    def send_get_request(self, config, endpoint):
        url = urljoin(config.base_url, endpoint)
        return requests.get(url, timeout=10)
