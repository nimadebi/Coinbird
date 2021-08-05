import ast
import sys
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_ticker_id(ticker):
    """
    :param ticker: String - ex: "btc", "ETH". Capitalization sensitive, but handled by get_price() function.
    :return: Symbol name of ticker. Ex. "Bitcoin", "Ethereum".
    """
    # Open file with all ticker-name combinations
    coinsfile = open("coins_markets.txt", "r")
    # Convert file (String) to a list.
    coinslist = ast.literal_eval(coinsfile.read())

    for coin in coinslist:
        if coin['symbol'].lower() == ticker:
            return coin['id']

    coinsfile.close()

def get_price(ticker):
    """
    :param ticker: String - this is the ticker. Ex. "btc", "ETH". Capitalization doesn't matter,
    since we use the lower() function on the ticker.
    :return: Coingecko API price in usd. If ticker can not be found, it returns None object.
    """
    id = get_ticker_id(ticker.lower())

    if id is None:
        return None

    return cg.get_price(id.lower(), "usd")[id.lower()]['usd']

def update_coins_markets_file():
    """
    Updates the coins_markets.txt file with current top market capitalization coins.
    get_coins_markets() returns one page at a time, so we have to call this function twice
    and append it to the complete list each time. We want the top 500 coins, and this function
    only returns us 250 max.
    """
    list_500 = []

    for i in range(1, 3):
        list_250 = cg.get_coins_markets(vs_currency="usd", per_page=250, page=i)
        for j in list_250:
            list_500.append(j)

    # Write to file
    sys.stdout = open('coins_markets.txt', 'w')
    print(list_500)
    sys.stdout.close()

def is_top_500_coin(ticker):
    """
    :param ticker: String - this is the ticker. Ex. "btc", "ETH". Capitalization doesn't matter,
    since we use the lower() function on the ticker.
    :return: Boolean - coin in top 500?
    """
    file = open("coins_markets.txt", "r")
    list_500 = ast.literal_eval(file.read())  # Makes it a list object

    for i in list_500:
        if i['symbol'] == ticker.lower():
            return True

    return False

def get_hourly_and_daily_change(ticker):
    """
    :param ticker: String
    :return: List - hourly and daily change in percentage [hourly, daily]
    """
    l = []

    id = get_ticker_id(ticker.lower())

    if id is None:
        return None

    historical_data = cg.get_coin_market_chart_by_id(id=id, vs_currency='usd', days=1, interval='hourly')
    historical_data_prices = historical_data.get('prices')

    new_price = historical_data_prices[24][1]
    old_price_hourly = historical_data_prices[23][1]
    old_price_daily = historical_data_prices[0][1]

    l.append(percentage_change(new_price, old_price_hourly))
    l.append(percentage_change(new_price, old_price_daily))

    return l


def percentage_change(new, old):
    return round(((new - old)/old)*100, 1)
