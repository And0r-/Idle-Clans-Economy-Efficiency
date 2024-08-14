from services import APIClient

# This class contains all PlayerMarket API
# https://query.idleclans.com/api-docs/index.html#tag/PlayerMarket
class PlayerMarketService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_class = "PlayerMarket"

    def get_items_prices_latest(self, item_id, include_average_price=False):
        """
        Retrieves the latest prices for a specific item, including the lowest price, highest price, 
        and optionally the average price from the past 24 hours.

        Args:
            item_id (int): The ID of the item to get the latest prices for.
            includeAveragePrice (bool, optional): If True, include the average price of the item 
                from the past 24 hours. Defaults to False.

        Returns:
            dict: A dictionary containing:
                - 'lowest_price' (float): The lowest price of the item.
                - 'highest_price' (float): The highest price of the item.
                - 'average_price' (float, optional): The average price of the item over the past 24 hours,
                only present if includeAveragePrice is set to True.
        """
        endpoint = f'{self.api_class}/items/prices/latest/{item_id}'
        params = {'includeAveragePrice': True} if include_average_price else None
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_latest_comprehensive(self, item_id):
        """
        Retrieves detailed price information for a specific item, including price distribution, 
        average prices, and recent trade activity.

        This function provides:
        - The top 10 lowest prices with corresponding volumes.
        - The top 10 highest prices with corresponding volumes.
        - The average price of the item over the past 1 day, 7 days, and 30 days.
        - The trade volume of the item over the past 1 day.

        Prices and volumes are based on the current state of the market, while average prices and trade 
        volumes are calculated using historical trade records.

        Args:
            item_id (int): The ID of the item to retrieve price details for.

        Returns:
            dict: A dictionary containing:
                - 'lowest_prices' (list of dict): The top 10 lowest prices and corresponding volumes.
                - 'highest_prices' (list of dict): The top 10 highest prices and corresponding volumes.
                - 'average_prices' (dict): The average prices over the past 1 day, 7 days, and 30 days.
                - 'trade_volume_1_day' (int): The total trade volume over the past 1 day.
        """
        endpoint = f'{self.api_class}/items/prices/latest/comprehensive/{item_id}'
        return self.api_client.get(endpoint)

    def get_items_prices_latest(self, include_average_price=False):
        """
        Retrieves the latest prices for all items, including the lowest price, highest price, 
        and optionally the average price from the past 24 hours.

        Args:
            includeAveragePrice (bool, optional): If True, include the average price of each item 
                from the past 24 hours. Defaults to False.

        Returns:
            dict: A dictionary where each key is an item ID, and each value is a dictionary 
            containing:
                - 'lowest_price' (float): The lowest price of the item.
                - 'highest_price' (float): The highest price of the item.
                - 'average_price' (float, optional): The average price over the past 24 hours, 
                present only if includeAveragePrice is True.
        """
        endpoint = f'{self.api_class}/items/prices/latest'
        params = {'includeAveragePrice': True} if include_average_price else None
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history(self, item_id, period=''):
        """
        Retrieves the price history of a specific item over a given period.

        Args:
            item_id (int): The ID of the item to get price history for.
            period (str, optional): The period for which to retrieve the price history. Supported values 
                are '1d' (1 day), '7d' (7 days), '30d' (30 days), and '1y' (1 year). Defaults to '1d'.

        Returns:
            dict: A dictionary containing the price history for the specified item over the given period. 
            The dictionary includes:
                - 'timestamps' (list of str): The timestamps for each data point.
                - 'prices' (list of float): The prices corresponding to each timestamp.
        """
        endpoint = f'{self.api_class}/items/prices/history/{item_id}'
        params = {'period': period} if period else None
        return self.api_client.get(endpoint, params=params)

    def get_items_prices_history_value(self, period='', limit=None):
        """
        Retrieves the trades with the highest item prices within a specified period.

        Args:
            period (str, optional): The period for which to retrieve the most valuable trades. Supported 
                values are '1d' (1 day), '7d' (7 days), '30d' (30 days), and '1y' (1 year). Defaults to '1d'.
            limit (int, optional): The maximum number of records to retrieve, between 1 and 10. Defaults to 10.

        Returns:
            list: A list of dictionaries, each representing a trade with the highest item prices. Each dictionary 
            includes:
                - 'trade_id' (int): The unique identifier of the trade.
                - 'item_id' (int): The ID of the item traded.
                - 'price' (float): The price at which the item was traded.
                - 'volume' (int): The volume of items traded.
                - 'timestamp' (str): The timestamp when the trade occurred.
        """
        endpoint = f'{self.api_class}/items/prices/history/value'
        params = {}
        if period:
            params.period = period
        if limit:
            params.limit = limit
        return self.api_client.get(endpoint, params=params)

    def get_items_volume_history(self, item_id=None, volume=None, timestamp=None):
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
        endpoint = f'{self.api_class}/items/volume/history'
        params = {}
        if item_id:
            params.item_id = item_id
        if volume:
            params.volume = volume
        if timestamp:
            params.timestamp = timestamp
        return self.api_client.get(endpoint, params=params)
