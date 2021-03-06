import os
import re
import boto
import redis
import json
from flask import Flask, render_template, redirect, request, url_for, make_response
from werkzeug import secure_filename

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    CREDENTIALS = VCAP_SERVICES["rediscloud"][0]["credentials"]
    r = redis.Redis(host=CREDENTIALS["hostname"], port=CREDENTIALS["port"], password=CREDENTIALS["password"])
else:
    r = redis.Redis(host='127.0.0.1', port='6379')

app = Flask(__name__)

@app.route('/')
def mainpage():
      
    response = """
    <HTML><BODY><h2>Welcome to my Food Blog</h2>
    <a href="/newmeal">Add New Meal</a><br>
    <a href="/dumpmeals">Show Meal Blog</a><br>
    </BODY>
    """
    return response

@app.route('/newmeal')
def survey():
    resp = make_response(render_template('newmeal.html'))
    return resp

@app.route('/mealthankyou.html', methods=['POST'])
def mealthankyou():

    global r
    m = request.form['mealtype']
    c = request.form['calories']
    t = request.form['description']

    print "Mealtype is " + m
    print "Calories is " + c
    print "Description: " + t
    
    Counter = r.incr('counter_meal')
    print "the meal counter is now: ", Counter
    ## Create a new key that with the counter. Pad with leading zeroes
    newmeal = 'meal' + str(Counter).zfill(3)
    print newmeal

    print "Storing the meal now"
    ## Now the key name is the content of the variable newsurvey
    r.hmset(newmeal,{'mealtype':m, 'calories':c, 'description':t})	
    resp = """
    <h3> - New entry added to the blog - </h3>
    <a href="/">Back to main menu</a>
    """
    return resp

@app.route('/dumpmeals')
def dumpmeals():

    global r
    response = "<center><h1>Meals to date</h1>"
    response += "<hr>"
    print "Reading back from Redis"
    for eachmeal in sorted(r.keys('meal*')):
        print eachmeal
        response += "Meal Type   : " + r.hget(eachmeal,'mealtype') + "<br>"
        response += "Calories    : " + r.hget(eachmeal,'calories') + "<br>"
        response += "Description : " + r.hget(eachmeal,'description') + "<br>"
        response += "<hr>"

    return response

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
