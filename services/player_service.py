from api_client.api_client import APIClient

# This class contains all Player API
# https://query.idleclans.com/api-docs/index.html#tag/Player
class PlayerService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Player"

    def get_clan_logs(self, name):
        endpoint = f'{self.api_class}/clan-logs/{name}'
        return self.api_client.get(endpoint)

    def get_profile(self, name):
        endpoint = f'{self.api_class}/profile/{name}'
        return self.api_client.get(endpoint)

    def get_profile_simple(self, name):
        endpoint = f'{self.api_class}/profile/simple/{name}'
        return self.api_client.get(endpoint)