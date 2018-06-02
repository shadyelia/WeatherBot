#!/usr/bin/env python

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import urllib
import json
import os

import reverse_geocoder as rg
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    checker = 0
    print ("started processing")
    if req.get("queryResult").get("action") == "askingforlocaiton":
        checker = 1
    elif req.get("queryResult").get("action") != "askingforweatherofcity":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    if (checker == 1):
     yql_query = makeYqlQueryfromlocation(req)
    else :
     yql_query =makeYqlQuery(req)
    print ("yql query created")
    if yql_query is None:
        print("yqlquery is empty")
        return {}
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    print(yql_url)

    result = urllib.request.urlopen(yql_url).read()
    print("yql result: ")
    print(result)

    data = json.loads(result)
    res = makeWebhookResult(data)
    return res

def makeYqlQueryfromlocation(req):
    result = req.get("queryResult")
    text = result.get("queryText")
    numbers = text.split(",")

    coordinates = (float(numbers[0]),float(numbers[1]))
    results = rg.search(coordinates)
    city = results[0].get("name")

    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeYqlQuery(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    degeree_in_C = (int(condition.get('temp')) - 32) * 5 / 9
    if ((degeree_in_C - int(degeree_in_C)) > 0.5):
        degeree_in_C = degeree_in_C + 1
    floating = degeree_in_C - int(degeree_in_C)
    degeree_in_C = degeree_in_C - floating
    degeree_in_C = str(degeree_in_C)
    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + degeree_in_C + " C."

    print("Response:")
    print(speech)

    return {
        "fulfillmentText": speech,
       
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
