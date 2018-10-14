from flask import Flask
from flask_cors import CORS
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import configparser

import json
import urllib.request
from urllib.error import URLError, HTTPError


config = configparser.RawConfigParser()
config.read('config.cfg')

app = Flask(__name__)
CORS(app)

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/socialApi/<platform>')
@limiter.limit("20 per second")
def process(platform):
    arg = request.args
    if platform == "facebook":
        return facebookApi(arg)
    elif platform == "twitter":
        return twitterApi(arg)
    elif platform == "instagram":
        return instagramApi(arg)
    else:
        return '%s not supported' % platform


#get access key: 
#   1. create app in facebook
#   2. go to https://developers.facebook.com/tools/explorer/2198903460379191
#   3. select your app and create access key

#this allows to post all parameters as long as they are accessing the public part of amiv.ethz 
#for feed use:     #?fields=posts{created_time%2Cmessage%2Cfull_picture}%2Cpicture"
def facebookApi(arg):
    accesstoken = config.get('Facebook', 'accessToken', 0)  
    url = "https://graph.facebook.com/" + config.get('Facebook','pageId',0)
    query = request.query_string.decode("utf-8") 
    url = url + "?%s" % query
    url = url + "&access_token=" + accesstoken
    try:
        contents = urllib.request.urlopen(url).read()
    except HTTPError as e:
        data = {}
        data['error'] = "unable to fetch resources from facebook"
        data['response'] = json.loads(e.read().decode("utf-8"))
        json_data = json.dumps(data)
        err_response = app.response_class(
            response=json_data,
            mimetype='application/json'
        )
        return err_response, e.code

    response = app.response_class(
        response=contents,
        mimetype='application/json'
    )
    return response

def twitterApi(arg):
    add_param = ''
    if(request.args.get('limit')):
        add_param = 'data-tweet-limit="%s"' % request.args.get('limit', '')
    return f'<a class="twitter-timeline" data-height="100%" {add_param} href="https://twitter.com/AMIV_ETHZ?ref_src=twsrc%5Etfw">Tweets by AMIV_ETHZ</a>'
def instagramApi(arg):
    return "instagram not yet supported"