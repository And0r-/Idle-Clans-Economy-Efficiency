from services import APIClient


# This class contains all Player API
# https://query.idleclans.com/api-docs/index.html#tag/Player
class PlayerService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Player"

    def get_clan_logs(self, name: str, skip: int = 0, limit: int = 100):
        """
        Retrieves the logs for a specific player from all clans.

        Args:
            name (str): The name of the player to retrieve logs for.
            skip (int, optional): The number of logs to skip. Defaults to 0.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            list: A list of dictionaries, each containing:
                - 'clanName': string or null
                - 'memberUsername': string or null
                - 'message': string or null
                - 'timestamp': string (date-time)
        """
        endpoint = f"{self.api_class}/clan-logs/{name}"
        params = {"skip": skip, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_profile(self, name: str):
        """
        Retrieves the profile for a specific player.

        Args:
            name (str): The name of the player to retrieve the profile for.

        Returns:
            dict: A dictionary with the following keys and types:
                - 'username': string or null
                - 'gameMode': string or null
                - 'guildName': string or null
                - 'skillExperiences': object or null
                - 'equipment': object or null
                - 'enchantmentBoosts': object or null
                - 'upgrades': object or null
                - 'griffinKills': integer
                - 'devilKills': integer
                - 'hadesKills': integer
                - 'zeusKills': integer
                - 'medusaKills': integer
                - 'chimeraKills': integer
                - 'kronosKills': integer
                - 'reckoningOfTheGodsCompletions': integer
                - 'guardiansOfTheCitadelCompletions': integer
        """
        endpoint = f"{self.api_class}/profile/{name}"
        return self.api_client.get(endpoint)

    def get_profile_simple(self, name):
        """
        Retrieves a simple profile for a specific player.

        Args:
            username (str): The username of the player to retrieve the simple profile for.

        Returns:
            dict: A dictionary with the following keys and types:
                - 'skillExperiences': string or null
                - 'equipment': string or null
                - 'hoursOffline': number (double)
                - 'taskTypeOnLogout': integer
                - 'taskNameOnLogout': string or null
        """
        endpoint = f"{self.api_class}/profile/simple/{name}"
        return self.api_client.get(endpoint)
