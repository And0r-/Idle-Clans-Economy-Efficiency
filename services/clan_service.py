from services import APIClient


# This class contains all Clan API
# https://query.idleclans.com/api-docs/index.html#tag/Clan
class ClanService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Clan"

    def get_logs_clan(self, name, skip: int = 0, limit: int = 100):
        """
        Retrieves the logs for a specific clan.

        Args:
            name (str): The name of the clan whose logs are to be retrieved.
            skip (int, optional): The number of logs to skip. Defaults to 0.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            list: A list of dictionaries, where each dictionary contains:
                - 'clanName': string or null
                - 'memberUsername': string or null
                - 'message': string or null
                - 'timestamp': string (date-time)
        """
        endpoint = f"{self.api_class}/logs/clan/{name}"
        params = {"skip": skip, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_player_logs_within_clan(
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
            list: A list of dictionaries where each dictionary contains:
                - 'clanName': string or null
                - 'memberUsername': string or null
                - 'message': string or null
                - 'timestamp': string (date-time)
        """
        endpoint = f"{self.api_class}/logs/clan/{clan_name}/{player_name}"
        params = {"skip": skip, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_recruitment(self, clan_name: str):
        """
        Retrieves the recruitment information for a specific clan.

        Args:
            clanName (str): The name of the clan.

        Returns:
            dict: A dictionary containing:
                - 'clanName': string or null
                - 'activityScore': float
                - 'minimumTotalLevelRequired': integer
                - 'memberlist': list of objects or null
                - 'memberCount': integer
                - 'isRecruiting': boolean
                - 'language': string or null
                - 'category': string or null
                - 'serializedSkills': string or null
                - 'serializedUpgrades': string or null
                - 'recruitmentMessage': string or null
                - 'houseId': integer

        """

        endpoint = f"{self.api_class}/recruitment/{clan_name}"
        return self.api_client.get(endpoint)

    def get_most_active(self, clan_query_info_json: str = "{}"):
        """
        Retrieves the most active guilds based on the provided query parameters.

        Args:
            clanQueryInfoJson (str, optional): JSON string containing query parameters. Defaults to "{}".

        Returns:
            dict: A dictionary with the following keys and types:
                - 'clanName': string or null
                - 'activityScore': number (float)
                - 'minimumTotalLevelRequired': integer
                - 'memberlist': array of objects or null
                - 'memberCount': integer
                - 'isRecruiting': boolean
                - 'language': string or null
                - 'category': string or null
                - 'serializedSkills': string or null
                - 'serializedUpgrades': string or null
                - 'recruitmentMessage': string or null
                - 'houseId': integer
        """

        endpoint = f"{self.api_class}/most-active"
        params = {"clanQueryInfoJson": clan_query_info_json}
        return self.api_client.get(endpoint, params=params)
