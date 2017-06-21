import os, time, boto
from flask import Flask, render_template, request
from werkzeug import secure_filename

ecs_access_key_id = '11234567890671000@ecstestdrive.emc.com'  
ecs_secret_key = 'AAAAAAbbbbbbCCCCCCDDDDDDEEEE1234'

session = boto.connect_s3(ecs_access_key_id, ecs_secret_key, host='object.ecstestdrive.com')  
bname = 'foodblog'
b = session.get_bucket(bname)
print "Bucket is: " + str(b)

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg', 'JPG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('upload_photo.html')

@app.route('/upload', methods=['POST'])
def upload():
    myfile = request.files['file']
    if myfile and allowed_file(myfile.filename):
        ## Make the file name safe, remove unsupported chars
        file_name = secure_filename(myfile.filename)
        ## Apple iPhones use just "image" as the filename when uploading
        ## So need to come up with a unique name
        ## In this case we prepend epoch time in milliseconds to file name
        unique_name = str(int(time.time()*1000)) + "-" + file_name
        ## Now we save the file in the uploads folder
        myfile.save(os.path.join("uploads", unique_name))

        print "Uploading " + unique_name + " to ECS"
        k = b.new_key(unique_name)
        k.set_contents_from_filename("uploads/" + unique_name)
        k.set_acl('public-read')
        # Finally remove the file from our container. We don't want to fill it up ;-)
        os.remove("uploads/" + unique_name)
        return"""<h3>Thanks for your photo</h3>"""

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)
