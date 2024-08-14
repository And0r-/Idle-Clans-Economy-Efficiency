from services import APIClient


# This class contains all Leaderboard API
# https://query.idleclans.com/api-docs/index.html#tag/Leaderboard
class LeaderboardService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Leaderboard"

    def get_clan_logs(self, leader_board_name: str, name: str):
        """
        Fetches the profile of an entity (player or clan) by their name.

        Args:
            leaderboardName (str): Name of the leaderboard, e.g., "players:default" for default game mode or
                                   "players:ironman" for ironman mode.
            name (str): Name of the entity (player or clan) to retrieve the profile for.

        Returns:
            dict: A dictionary containing the profile information of the specified entity.
        """
        endpoint = f"{self.api_class}/profile/{leader_board_name}/{name}"
        return self.api_client.get(endpoint)

    def get_clan_logs(self, leader_board_name: str, name: str):
        """
        Fetches the profile of an entity (player or clan) by their name.

        Args:
            leaderboardName (str): Name of the leaderboard, e.g., "players:default" for default game mode or
                                   "players:ironman" for ironman mode.
            name (str): Name of the entity (player or clan) to retrieve the profile for.

        Returns:
            dict: A dictionary containing the profile information of the specified entity.
        """
        endpoint = f"{self.api_class}/top/{leader_board_name}/{name}"
        return self.api_client.get(endpoint)
