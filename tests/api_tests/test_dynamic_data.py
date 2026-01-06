import pytest
from faker import Faker
from utils.requests.get_request import GetRequest

fake = Faker()

class TestResponseFormats(GetRequest):

    @pytest.mark.parametrize("n", [
        fake.random_int(min=1, max=10),
        fake.random_int(min=50, max=100),
        fake.random_int(min=256, max=1024),
    ])
    def test_bytes_endpoint_returns_exact_number_of_bytes(self, config, n):
        # given & when
        response = self.send_get_request(config, endpoint=f"/bytes/{n}")

        # then
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"
        assert len(response.content) == n, f"Expected {n} bytes, got {len(response.content)}"
