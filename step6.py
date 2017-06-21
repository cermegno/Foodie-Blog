import os
import re
import time
import boto
import redis
from flask import Flask, render_template, redirect, request, url_for, make_response
from werkzeug import secure_filename

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    CREDENTIALS = VCAP_SERVICES["rediscloud"][0]["credentials"]
    r = redis.Redis(host=CREDENTIALS["hostname"], port=CREDENTIALS["port"], password=CREDENTIALS["password"])
else:
    r = redis.Redis(host='127.0.0.1', port='6379')

ecs_access_key_id = '131234567890000@ecstestdrive.emc.com'  
ecs_secret_key = 'AAAAABBBBBBBBBCCCCDDDDDDDEEEEEEE'

session = boto.connect_s3(ecs_access_key_id, ecs_secret_key, host='object.ecstestdrive.com')  
bname = 'foodblog'
b = session.get_bucket(bname)
print "Bucket is: " + str(b)

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'JPG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def mainpage():

    CalorieCount = r.get('caloriecount')
        
    response = """
    <HTML><BODY><h2>Welcome to my Food Blog</h2>
    <a href="/newmeal">Add New Meal</a><br>
    <a href="/dumpmeals">Show Meal Blog</a><br><br>
    Calories so far: <b>{}</b>
    </BODY>
    """.format(str(CalorieCount))
    return response

@app.route('/newmeal')
def survey():
    resp = make_response(render_template('newmeal.html'))
    return resp

@app.route('/mealthankyou.html', methods=['POST'])
def mealthankyou():

    global r
    d = request.form['mealdate']
    m = request.form['mealtype']
    c = request.form['calories']
    t = request.form['description']

    print "Meal Date is " + d
    print "Meal Type is " + m
    print "Calories are " + c
    print "Description: " + t

    r.incrby('caloriecount',int(c))
    
    Counter = r.incr('counter_meal')
    print "the meal counter is now: ", Counter
    ## Create a new key that with the counter and pad with leading zeroes
    newmeal = 'meal' + str(Counter).zfill(3)
    print newmeal

    print "Storing the meal now"
    ## Now the key name is the content of the variable newsurvey
    r.hmset(newmeal,{'mealdate':d, 'mealtype':m,'calories':c, 'description':t})

    myfile = request.files['file']
    print myfile
    if myfile and allowed_file(myfile.filename):
        ## Newmeal is unique. Let's use it to store the object
        myfile.save(os.path.join("uploads", newmeal))

        print "Uploading " + newmeal + " to ECS"
        k = b.new_key(newmeal)
        k.set_contents_from_filename("uploads/" + newmeal)
        k.set_acl('public-read')
        # Finally remove the file from our container. We don't want to fill it up ;-)
        os.remove("uploads/" + newmeal)
    
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
        response += "Meal Date   : " + r.hget(eachmeal,'mealdate') + "<br>"
        response += "Meal Type   : " + r.hget(eachmeal,'mealtype') + "<br>"
        response += "Calories    : " + r.hget(eachmeal,'calories') + "<br>"
        response += "Description : " + r.hget(eachmeal,'description') + "<br><br>"
        response += """<img src="http://131030155286710005.public.ecstestdrive.com/foodblog/{}" width=500><br>""".format(eachmeal)
        response += "<hr>"

    return response


if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
