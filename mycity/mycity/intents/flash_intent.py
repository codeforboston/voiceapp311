"""
This is the flash intent. It will first debreif on the traffic and then run down the Open News API for local headlines
"""


# API KEY = 8a750ca755344167bc568d29cfe2653d
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='8a750ca755344167bc568d29cfe2653d')


top_headlines = newsapi.get_top_headlines(q='Boston')
print(top_headlines)

