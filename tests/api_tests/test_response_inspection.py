from faker import Faker
from utils.requests.get_request import GetRequest

fake = Faker()


class TestCacheEndpoint(GetRequest):

    def test_cache_endpoint_returns_200_without_cache_headers(self, config):
        # given & when
        response = self.send_get_request(
            config,
            endpoint="/cache"
        )

        # then
        assert response.status_code == 200
        assert response.headers["Content-Type"].startswith("application/json")
        assert response.json() is not None