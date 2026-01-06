from ipaddress import ip_address



class ResponseFormatValidation:
    def validate_brotli_response(self, response):
        assert response.status_code == 200, (
            f"Expected status code '200', got '{response.status_code}'"
        )

        try:
            payload = response.json()
        except ValueError:
            assert False, "Expected response body to be valid JSON"

        assert isinstance(payload, dict), (
            f"Expected payload to be 'dict', got '{type(payload).__name__}'"
        )

        assert payload.get("brotli") is True, (
            f"Expected 'brotli' == 'True', got '{payload.get('brotli')}'"
        )

        assert payload.get("method") == "GET", (
            f"Expected 'method' == 'GET', got '{payload.get('method')}'"
        )

        headers = payload.get("headers")
        assert isinstance(headers, dict), (
            f"Expected 'headers' to be 'dict', got '{type(headers).__name__}'"
        )

        assert headers.get("Accept") == "*/*", (
            f"Expected 'Accept' == '*/*', got '{headers.get('Accept')}'"
        )

        accept_encoding = headers.get("Accept-Encoding", "")
        assert isinstance(accept_encoding, str), (
            f"Expected 'Accept-Encoding' to be 'str', got '{type(accept_encoding).__name__}'"
        )
        assert "gzip" in accept_encoding, (
            f"Expected 'Accept-Encoding' to contain 'gzip', got '{accept_encoding}'"
        )

        user_agent = headers.get("User-Agent", "")
        assert user_agent.startswith("python-requests/"), (
            f"Expected 'User-Agent' to start with 'python-requests/', got '{user_agent}'"
        )

        origin = payload.get("origin")
        assert isinstance(origin, str), (
            f"Expected 'origin' to be 'str', got '{type(origin).__name__}'"
        )
        for part in origin.split(","):
            ip_address(part.strip())

