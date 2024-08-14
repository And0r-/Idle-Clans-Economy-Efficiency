from services import APIClient


# This class contains all PlayerMarket API
# https://query.idleclans.com/api-docs/index.html#tag/PlayerMarket
class PlayerMarketService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "PlayerMarket"

    def get_items_prices_latest(
        self, item_id: int, include_average_price: bool = False
    ):
        """
        Gets the latest prices for a specific item, including the lowest price, highest price,
        and optionally the average price.

        Args:
            itemId (int): The ID of the item to retrieve the latest prices for.
            includeAveragePrice (bool, optional): If true, include the average price of the item from the past 24 hours.
                                                  Defaults to False.

        Returns:
            dict: A dictionary containing the latest price information for the specified item.
        """
        endpoint = f"{self.api_class}/items/prices/latest/{item_id}"
        params = {"includeAveragePrice": include_average_price}
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_latest_comprehensive(self, item_id: int):
        """
        Retrieves detailed price information for a specific item.

        This function provides comprehensive price details for a given item, including:
        - The top 10 lowest prices with their corresponding volumes.
        - The top 10 highest prices with their corresponding volumes.
        - The average price of the item over the past 1 day, 7 days, and 30 days.
        - The trade volume of the item over the past 1 day.

        The prices and volumes are based on the current state of the market, with averages
        and trade volume calculated from historical trade records.

        Args:
            itemId (int): The ID of the item to retrieve price details for.

        Returns:
            dict: A dictionary containing detailed price information for the specified item.
        """
        endpoint = f"{self.api_class}/items/prices/latest/comprehensive/{item_id}"
        return self.api_client.get(endpoint)

    def get_items_prices_latest(self, include_average_price: bool = False):
        """
        Gets the latest prices for all items, including the lowest price, highest price,
        and optionally the average price.

        Args:
            includeAveragePrice (bool, optional): If true, include the average price of each item from the past 24 hours.
                                                  Defaults to False.

        Returns:
            dict: A dictionary containing the latest prices for all items.
        """
        endpoint = f"{self.api_class}/items/prices/latest"
        params = {"includeAveragePrice": include_average_price}
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history(self, item_id: int, period: str = "1d"):
        """
        Retrieves the price history of a specific item over a given period.

        Args:
            itemId (int): The ID of the item to retrieve the price history for.
            period (str, optional): The period for which to retrieve the price history.
                                    Supported values are '1d', '7d', '30d', and '1y'. Defaults to '1d'.

        Returns:
            dict: A dictionary containing the price history of the specified item for the given period.
        """
        endpoint = f"{self.api_class}/items/prices/history/{item_id}"
        params = {"period": period}
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history_value(self, period: str = "1d", limit: int = 10):
        """
        Retrieves the trades with the highest item prices within a specified period.

        Args:
            period (str, optional): The period for which to retrieve the most valuable trades.
                                    Supported values are '1d', '7d', '30d', and '1y'. Defaults to '1d'.
            limit (int, optional): The maximum number of records to retrieve, between 1 and 10. Defaults to 10.

        Returns:
            list: A list of trades with the highest item prices for the specified period.
        """
        endpoint = f"{self.api_class}/items/prices/history/value"
        params = {"period": period, "limit": limit}
        return self.api_client.get(endpoint, params=params)

    def get_items_volume_history(self, period: str = "1d", limit: int = 10):
        """
        Retrieves the top items by trade volume within a specified period.

        Args:
            period (str, optional): The period for which to retrieve the top items by volume. Supported values
                are '1d' (1 day), '7d' (7 days), '30d' (30 days), and '1y' (1 year). Defaults to '1d'.
            limit (int, optional): The maximum number of records to retrieve, between 1 and 10. Defaults to 10.

        Returns:
            list: A list of dictionaries, each representing an item with high trade volume. Each dictionary
            includes:
                - 'item_id' (int): The ID of the item.
                - 'volume' (int): The total trade volume of the item.
                - 'timestamp' (str): The timestamp representing the end of the period for the volume calculation.
        """
        endpoint = f"{self.api_class}/items/volume/history"
        params = {"period": period, "limit": limit}
        return self.api_client.get(endpoint, params=params)
