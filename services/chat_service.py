from services import APIClient


# This class contains all Chat API
# https://query.idleclans.com/api-docs/index.html#tag/Chat
class ChatService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Chat"

    def get_chat_recent(
        self,
        general_disabled: bool = False,
        trade_disabled: bool = False,
        help_disabled: bool = False,
        clan_hub_disabled: bool = False,
        combat_lfg_disabled: bool = False,
        raid_lfg_disabled: bool = False,
    ):
        """
        Retrieves the public chat history for various channels.

        Args:
            generalDisabled (bool, optional): If true, excludes the General channel from the result. Defaults to False.
            tradeDisabled (bool, optional): If true, excludes the Trade channel from the result. Defaults to False.
            helpDisabled (bool, optional): If true, excludes the Help channel from the result. Defaults to False.
            clanHubDisabled (bool, optional): If true, excludes the ClanHub channel from the result. Defaults to False.
            combatLFGDisabled (bool, optional): If true, excludes the CombatLFG channel from the result. Defaults to False.
            raidLFGDisabled (bool, optional): If true, excludes the RaidLFG channel from the result. Defaults to False.

        Returns:
            list: A list of chat messages from the selected channels.
        """
        endpoint = f"{self.api_class}/recent"
        params = {
            "generalDisabled": general_disabled,
            "tradeDisabled": trade_disabled,
            "helpDisabled": help_disabled,
            "clanHubDisabled": clan_hub_disabled,
            "combatLFGDisabled": combat_lfg_disabled,
            "raidLFGDisabled": raid_lfg_disabled,
        }
        return self.api_client.get(endpoint, params=params)
