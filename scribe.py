#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask
from flask import make_response
from flask import request
from flask import render_template

from pymongo import MongoClient

import json
import string


# Configs
DATABASE = 'inscriptions'

app = Flask(__name__)

# Mongo
client = MongoClient('localhost', 27017)
db = client[DATABASE]
sessions = db['sessions']


def random_string(length=8):
    return random.choice(string.letters) + ''.join([random.choice(string.letters + string.digits) for n in xrange(length-1)])

@app.route('/')
def main():
    # TODO: make this beautifuler
    return 'Watch the magic ensue.'

@app.route('/make_site', methods=['POST'])
def make_website():
    assert request.method == 'POST'
    content = request.form.get('content')
    if not content:
        response = {'Error':'No content found.'}
        return make_response(json.dumps(response), 400, mimetype='application/json')
    try:
        content = json.loads(content)
    except ValueError:
        response = {'Error':'Invalid JSON.'}
    # Generate Markup Page
    identifier = random_string()
    return

@app.route('/p/<page>')
def get_website(page):
    pass
    
@app.route('/css/<page>')
def get_css(page):
    return


if __name__ == '__main__':
    print('Starting Scribe. You are now entering a hard hat area. '
          'Enter at your own risk.')
    app.debug = True
    app.run(host='0.0.0.0', port=80)