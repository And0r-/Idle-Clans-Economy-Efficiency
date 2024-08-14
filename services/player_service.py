from services import APIClient

# This class contains all Player API
# https://query.idleclans.com/api-docs/index.html#tag/Player
class PlayerService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Player"

    def get_clan_logs(self, name, skip=None, limit=None):
        """
        Retrieves logs for a specific player across all clans.

        Args:
            name (str): The name of the player whose logs are to be retrieved.
            skip (int, optional): The number of logs to skip. Defaults to 0.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            list: A list of logs for the specified player, with each log containing relevant information 
            about the player's activity across clans.
        """
        endpoint = f'{self.api_class}/clan-logs/{name}'
        params = {}
        if skip:
            params.skip = skip
        if limit:
            params.limit = limit
        return self.api_client.get(endpoint, params=params)

    def get_profile(self, name):
        """
        Retrieves the profile information for a specific player.

        Args:
            name (str): The name of the player whose profile is to be retrieved.

        Returns:
            dict: A dictionary containing the profile information of the specified player.
        """
        endpoint = f'{self.api_class}/profile/{name}'
        return self.api_client.get(endpoint)

    def get_profile_simple(self, name):
        """
        Retrieves a simplified profile for a specific player.

        Args:
            username (str): The username of the player whose simple profile is to be retrieved.

        Returns:
            dict: A dictionary containing basic profile information of the specified player.
        """
        endpoint = f'{self.api_class}/profile/simple/{name}'
        return self.api_client.get(endpoint)