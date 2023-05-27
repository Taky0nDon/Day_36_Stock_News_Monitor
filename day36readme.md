D A Y T H I R T Y S I X

# Stock News Monitor 

## Overview

This app uses three APIs in order to send an SMS containing relevant news
about a given stock.

The first API is alphavantageco, which returns daily price data for the stock.
Using this data, the percent price change for the previous day, and the day prior,
is calculated.

Then, the newsapi.org API is used to retrieve the most recent articles relevant
to the given stock. Relevance is determined by the presence of the company name
in the article title.

Finally, the Twilio API is used to send a text containing the stock symbol,
the percent change, article title, and article description.

This is the most finicky part of the code, and doesn't always work for reasons I
have yet to discover

## Goals
1. Gather stock prices of the stocks your interested in with an API call
   2. Get closing price of current_day and closing price of previous day
   3. calculate current price as percentage of previous day price
   4. program will fetch and send us news when a certain % change threshold is met
5. send SMS with fluctuation data and relevant news