from services import APIClient


# This class contains all Clan API
# https://query.idleclans.com/api-docs/index.html#tag/Clan
class ClanService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Clan"

    def get_items_prices_history(self, name, skip: int = 0, limit: int = 100):
        """
        Retrieves the logs for a specific clan.

        Args:
            name (str): The name of the clan whose logs are to be retrieved.
            skip (int, optional): The number of logs to skip. Defaults to 0.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            list: A list of logs related to the specified clan.
        """
        endpoint = f"{self.api_class}/logs/clan/{name}"
        params = {"skip": skip, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history(
        self, clan_name: str, player_name: str, skip: int = 0, limit: int = 100
    ):
        """
        Retrieves the logs for a specific player within a clan.

        Args:
            clanName (str): The name of the clan.
            playerName (str): The name of the player.
            skip (int, optional): The number of logs to skip. Defaults to 0.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            list: A list of logs related to the specified player within the clan.
        """
        endpoint = f"{self.api_class}/logs/clan/{clan_name}/{player_name}"
        params = {"skip": skip, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history(self, clan_name: str):
        """
        Retrieves the recruitment information for a specific clan.

        Args:
            clanName (str): The name of the clan.

        Returns:
            dict: A dictionary containing the recruitment information of the specified clan.
        """

        endpoint = f"{self.api_class}/recruitment/{clan_name}"
        return self.api_client.get(endpoint)

    def get_items_prices_history(self, clan_query_info_json: str = "{}"):
        """
        Retrieves the most active guilds based on the provided query parameters.

        Args:
            clanQueryInfoJson (str, optional): JSON string containing query parameters. Defaults to "{}".

        Returns:
            list: A list of the most active guilds based on the provided query parameters.
        """

        endpoint = f"{self.api_class}/most-active"
        params = {"clanQueryInfoJson": clan_query_info_json}
        return self.api_client.get(endpoint, params=params)
