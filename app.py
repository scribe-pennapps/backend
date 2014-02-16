#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask
from flask import make_response
from flask import request
from flask import render_template

from pymongo import MongoClient

import json
import random
import string
import os


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
    response = make_response('Watch the magic ensue.', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/upload', methods=['POST'])
def function():
    assert request.method == 'POST'
    identifier = random_string()
    image = request.form.get('image')
    if not image:
        response = make_response(json.dumps({'Error':'No image found.'}), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Incase id is inplace
    os.system('rm -rf cache/%s.png' % identifier)
    os.system('touch cache/%s.png' % identifier)
    cache = open('cache/%s.png' % identifier, 'wb')
    cache.write(image)
    cache.close()


@app.route('/make_site', methods=['POST'])
def make_website():
    assert request.method == 'POST'
    content = request.form.get('content')
    print(content)
    if not content:
        response = make_response(json.dumps({'Error':'No content found.'}), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        content = json.loads(content)
    except ValueError:
        response = make_response(json.dumps({'Error':'Invalid JSON.'}), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Generate Markup Page
    identifier = random_string()
    html = render_template('page.html', screen=content, identifier=identifier)
    session = {'html':html, 'identifier':identifier}
    session_id = sessions.insert(session)
    print('Created session %s with MongoDB ID %s.' % (identifier, str(session_id)))
    response = make_response(json.dumps({'Success':'Page generated.', 'SessionID':identifier}))
    response.headers['Content-Type'] = 'application/json'
    return response



@app.route('/p/<page>')
def get_website(page):
    session = sessions.find_one({'identifier':page})
    if not session:
        response = make_response('Shit.', 404)
        response.headers['Content-Type'] = 'text/plain'
    else:
        response = make_response(session['html'])
        response.headers['Content-Type'] = 'text/html'
    return response

    
@app.route('/css/<page>')
def get_css(page):
    response = make_response('//Fuck this shit.')
    response.headers['Content-Type'] = 'text/css'
    return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)