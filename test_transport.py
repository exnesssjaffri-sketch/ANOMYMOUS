import unittest
from unittest.mock import patch, MagicMock
import requests
import json
from transport import RealHTTPTransport, MockTransport

class TestTransportLayer(unittest.TestCase):
    def setUp(self):
        self.endpoint = "https://api.example.com/v1"
        self.api_key = "test_api_key"
        self.payload = {"model": "gpt-3.5", "messages": [{"role": "user", "content": "Hello"}]}

    def test_mock_transport(self):
        transport = MockTransport()
        result = transport.send_request(self.payload, timeout=30)
        self.assertIn("choices", result)
        self.assertEqual(result["id"], "mock-req-123")

    def test_real_transport_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello, world!"}}]}

        with patch("requests.post", return_value=mock_response):
            transport = RealHTTPTransport(self.endpoint, self.api_key)
            result = transport.send_request(self.payload, timeout=30)
            self.assertEqual(result["choices"][0]["message"]["content"], "Hello, world!")

    def test_real_transport_http_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        
        def raise_http_error(*args, **kwargs):
            raise requests.exceptions.HTTPError("Bad Request", response=mock_response)
        
        with patch("requests.post", side_effect=raise_http_error):
            with self.assertRaises(Exception) as context:
                transport = RealHTTPTransport(self.endpoint, self.api_key)
                transport.send_request(self.payload, timeout=30)
            self.assertIn("HTTP Error 400", str(context.exception))
            self.assertIn("Bad Request", str(context.exception))

    def test_real_transport_timeout(self):
        with patch("requests.post", side_effect=requests.exceptions.Timeout):
            transport = RealHTTPTransport(self.endpoint, self.api_key)
            with self.assertRaises(Exception) as context:
                transport.send_request(self.payload, timeout=1)
            self.assertIn("Transport Error", str(context.exception))

if __name__ == "__main__":
    unittest.main()