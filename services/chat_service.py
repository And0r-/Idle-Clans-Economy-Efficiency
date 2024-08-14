from services import APIClient


# This class contains all Chat API
# https://query.idleclans.com/api-docs/index.html#tag/Chat
class ChatService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "Chat"

    def get_chat_recent(
        self,
        name: str,
        generalDisabled: bool = False,
        tradeDisabled: bool = False,
        helpDisabled: bool = False,
        clanHubDisabled: bool = False,
        combatLFGDisabled: bool = False,
        raidLFGDisabled: bool = False,
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
        params = {}
        if generalDisabled:
            params.generalDisabled = generalDisabled
        if tradeDisabled:
            params.tradeDisabled = tradeDisabled
        if helpDisabled:
            params.helpDisabled = helpDisabled
        if clanHubDisabled:
            params.clanHubDisabled = clanHubDisabled
        if combatLFGDisabled:
            params.combatLFGDisabled = combatLFGDisabled
        if raidLFGDisabled:
            params.raidLFGDisabled = raidLFGDisabled
        return self.api_client.get(endpoint, params=params)
