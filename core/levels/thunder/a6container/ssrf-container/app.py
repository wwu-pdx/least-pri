from flask import Flask, redirect, request, url_for, render_template
import logging
import requests

app = Flask(__name__)

@app.route('/')
def page():
    return "Hello World!"

@app.route('/admin-proxy-aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d')
def proxy():
    if 'url' not in request.args:
        return render_template('proxy.html')
    else:
        metadata_url = request.args['url']
        resp = requests.get(metadata_url, headers={'Metadata-Flavor': 'Google'})
        return resp.text

if __name__ == '__main__':
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('./access_log')
    logger.addHandler(handler)
    app.run(host='0.0.0.0', port=80, debug=True)
