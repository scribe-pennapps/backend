#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask
from flask import make_response
from flask import request
from flask import render_template

from pymongo import MongoClient

from werkzeug.utils import secure_filename

import json
import random
import string
import subprocess
import os


# Configs

UPLOAD_FOLDER = 'cache/'


# Hacked shit
JUMBOTRON_ELEMENTS = 3
TILE_ROW_ELEMENTS = 2

# Legit stuff (in comparision)
DATABASE = 'inscriptions'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mongo
client = MongoClient('localhost', 27017)
db = client[DATABASE]
sessions = db['sessions']


def random_string(length=8):
    return random.choice(string.letters) + ''.join([random.choice(string.letters + string.digits) for n in xrange(length-1)])

def item_type(div):
    if len(div['children']) == 1:
        return 'jumbotron'
    else:
        return 'thumbnail-row'

@app.route('/')
def main():
    # TODO: make this beautifuler
    response = make_response('Watch the magic ensue.', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/upload', methods=['POST'])
def function():
    assert request.method == 'POST'
    # Prepares session id.
    identifier = random_string()
    img = 'cache/%s.png' % identifier
    image = request.files['file']
    if not image:
        print('Image not found.')
        response = make_response(json.dumps({'Error':'No image found.'}), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    filename = secure_filename('%s.png' % identifier)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(request.form)
    # Incase id is in place
    # os.system('rm -rf %s' % img)
    # os.system('touch %s' % img)
    # cache = open(img, 'wb')
    # cache.write(image)
    # cache.close()

    # Cache has been written. Time to get the real shit going.
    try:
        parse = json.loads(subprocess.check_output(['scribe-process', img]))
    except StandardError as e:
        response = make_response(json.dumps({'Error':'Please retake the image.'}), 400)
        response.headers['Content-Type'] = 'application'
        return response
    print(parse)

    # Parse has a lot of stuff I don't actually need. Ignore that.

    #Hella hacky
    #screen is the window from which everything happens
    screen = dict()
    screen['navbar'] = dict()
    # screen['navbar'] = parse['children'][0]['attr']
    screen['navbar']['inverse'] = True
    screen['navbar']['stuck-top'] = True
    screen['navbar']['title'] = 'Scribe' #parse['children'][0]['attr']['content']
    # screen['navbar']['elements'] = parse['children'][0]['attr']['elements']

    screen['container'] = dict()
    screen['container']['attr'] = []
    screen['container']['children'] = []

    for div in parse['children'][1:]:
        div_type = item_type(div)
        if div_type == 'jumbotron':
            child = {
                'attr':{
                    'row':True
                },
                'children':[],
                'components':[
                    {
                        'type':'jumbotron',
                        'attr':{
                            'button-type':'default',
                            # 'button-content':div['children'][0]['attr']['content'],
                            'button-content':'Click!',
                            # 'header':div['attr']['content'],
                            'header':'Scribe. Pure creation.',
                            # 'subheader':div['attr'].get('subheader', '')
                            'subheader':'Yeezus brought us through our struggles.'
                        }
                    }
                ]
            }
        elif div_type == 'thumbnail-row':
            child = {
                'attr':{
                    'row':True
                },
                'children':[],
                'components':[
                    {
                        'type':'thumbnail-row',
                        'attr':{}
                    }
                ]
            }
        else:
            print('Fuuuuuuuuck.')    
            return make_response('Fuuuuuuuuck', 500)
        screen['container']['children'].append(child)

    html = render_template('page.html', screen=screen, identifier=identifier)
    session = {'html':html, 'identifier':identifier}
    session_id = sessions.insert(session)
    print('Created session %s with MongoDB ID %s.' % (identifier, str(session_id)))
    response = make_response(json.dumps({'Success':'Page generated.', 'SessionID':identifier}))
    response.headers['Content-Type'] = 'application/json'
    return response

    response = make_response(json.dumps({'Success':'Image uploaded.'}), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


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