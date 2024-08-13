# Doc = "https://query.idleclans.com/api-docs/index.html"
import requests

class APIClient:
    def __init__(self, base_url = "https://query.idleclans.com/api"):
        self.base_url = base_url

    def _get_headers(self):
        return {
            'Content-Type': 'application/json'
        }

    def get(self, endpoint, params=None, headers=None):
        """
        Makes a GET request to the specified URL with optional query parameters and headers.

        Parameters:
            endpoint (str): The URL endpoint to send the GET request to.
            params (dict, optional): Dictionary of query parameters to append to the URL. Default is None.
            headers (dict, optional): Dictionary of headers to include in the request. Default is None.

        Returns:
            response (requests.Response): The response object returned by the GET request.
        """
        try:
            response = requests.get(f'{self.base_url}/{endpoint}', params=params, headers=headers or self._get_headers())
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error occurred: {req_err}")
        return None
