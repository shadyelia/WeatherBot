# Dialogflow - sample get the weather of any city using Yahoo! Weather API  in Python

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

#Notes :
if you want to use python 3.6.5
you need
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
and use them insert of the old urllib : 
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.request.urlopen(yql_url).read()
