from file import api_key

key = api_key

def is_valid_currency(currency):
    """This will determine if the currency being pulled is valid and in the database. For this project I am specifically pulling BitCoin so this likely would not be an issue. The call sign should be 3 letters"""
    return len(currency) == 3

def is_valid_amount(amount):
    """This will attempt to check that the amount from the api call is 0=<"""
    try:
        return float (amount)
    except ValueError:
        return False