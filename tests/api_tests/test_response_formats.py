from utils.requests.get_request import GetRequest
from utils.validation.response_format_validation import ResponseFormatValidation


class TestResponseFormats(GetRequest, ResponseFormatValidation):

    def test_brotli_returns_valid_response(self, config):
        # given & when
        response = self.send_get_request(config, endpoint="/brotli")

        # then
        self.validate_brotli_response(response=response)
