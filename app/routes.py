from app import app
from flask import render_template, redirect
from flask import request as r
from urllib.parse import urlencode
import requests
import base64
import json
CLIENT_ID = ''
CLIENT_SECRET = ''

with open('credentials.txt') as fin:
    x = [l.rstrip("\n") for l in fin]
    CLIENT_ID = x[0]
    CLIENT_SECRET = x[1]


@app.route('/')
@app.route('/index')
def index(code=''):
    if code:
        code = json.loads(code)
        token = code['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            'https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
        return response.text
    else:
        return redirect('/login')


@app.route('/login')
def login():
    SCOPES = 'user-read-currently-playing'
    payload = {'client_id': CLIENT_ID,
               'response_type': 'code',
               'redirect_uri': 'http://localhost:5000/callback',
               'scope': SCOPES}
    return redirect('https://accounts.spotify.com/authorize?' + urlencode(payload))


@app.route('/callback')
def callback(count=0, code=None):
    if not count:
        code = r.args.get('code', default='', type=str)
        return parse_toke(code)
    if count:
        return index(code)


def parse_toke(code):
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:5000/callback'
    }
    response = requests.post(
        'https://accounts.spotify.com/api/token', headers=headers, data=data)
    return callback(1, response.text)
