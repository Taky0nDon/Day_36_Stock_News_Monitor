import dotenv
import time
import os
import requests
import json
import datetime as dt
from twilio.rest import Client


def get_percent_change(symbol: str, params: dict) -> float:
    """Returns the percent change in the price of a stock at closing yesterday and the previous day, with respect
    to the previous day. Takes a list of strings as an argument, where every string is a stock symbol, as well
    as a dictionary of parameters to pass to the API call."""
    params["symbol"] = symbol
    alpha_response_symbol = requests.get("https://www.alphavantage.co/query", params)
    alpha_response_symbol.raise_for_status()
    symbol_data = alpha_response_symbol.json()
    symbol_close_yday = float(symbol_data["Time Series (Daily)"][yesterday]["4. close"])
    symbol_close_day_before_yday = float(symbol_data["Time Series (Daily)"][day_before_yesterday]["4. close"])

    price_difference = symbol_close_yday - symbol_close_day_before_yday
    percent_change = (price_difference / symbol_close_day_before_yday) * 100
    percent_change_two_decimals = round(percent_change, 2)
    return percent_change_two_decimals


def get_news(term: str, params: dict[str]) -> dict:
    """Pass in the relevant term to search for, and the dictionary containing the desired the parameters.
    Returns a dictionary from the JSON data in the response."""
    params["q"] = term
    news_response = requests.get("https://newsapi.org/v2/everything", params)
    news_response.raise_for_status()
    news_data = news_response.json()
    return news_data


def send_text(message_text: str) -> None:
    """utilizing the twilio api,  Send a separate message with the percentage change and each article's title and
description to your phone number"""
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages\
        .create(body=message_text,
                from_=f"{TWILIO_NUMBER}",
                to=f"{MY_NUMBER}")
    status = message.status
    time.sleep(10)
    print(status)


dotenv.load_dotenv("../environment.env")

AV_KEY = os.getenv("ALPHA_KEY")
NEWS_KEY = os.environ.get("NEWS_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_KEY")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
MY_NUMBER = os.environ.get("MY_NUMBER")


STOCKS = ["TSLA", "IBM", "AMD", "SQM", "NVDA"]
COMPANY_NAME = ["Tesla Inc", "IBM", "AMD", "SQM", "NVIDIA"]

alpha_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": "TSLA",
    "outputsize": "compact",
    "datatype": "json",
    "apikey": AV_KEY
}

news_params = {
    "apiKey": NEWS_KEY,
    "q": str,  # term to search for
    "searchIn": "title",  # can be title, description, content
    "sortBy": "publishedAt",
    "language": "en"
}

now = dt.datetime.now()
yesterday = f"{now.year}-{now.month:02d}-{now.day - 1:02d}"
day_before_yesterday = f"{now.year}-{now.month:02d}-{now.day - 2:02d}"


def main() -> None:
    """When STOCK price increase/decreases by 5% between yesterday and the day before yesterday, send text formatted
    like the template below containg the stock symbol, the price change, the article headline and description."""
    final_final_message = ""
    # for stock, name in zip(STOCKS, COMPANY_NAME):
    stock = "AMD"
    name = "AMD"
    delta_price = get_percent_change(stock, alpha_params)
    if delta_price > 0:
        movement_symbol = "🔺"
    elif delta_price < 0:
        movement_symbol = "🔻"
    else:
        movement_symbol = ""
    articles = get_news(name, news_params)
    first_three_articles = articles["articles"][:2]
    message_header = f"{stock}: {movement_symbol}{delta_price}%\n"
    for article in first_three_articles:
        article = first_three_articles[1]
        final_body = ""
        headline = article["title"]
        brief = article["description"]
        message_body = f"Headline: {headline}\n" \
                       f"Brief: {brief}\n"
        final_body += message_body
    final_final_message = message_header + final_body
    print(final_final_message)
    send_text(final_final_message)



main()
# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the
coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the
coronavirus market crash.
"""
