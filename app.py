from flask import g, copy_current_request_context, send_file, flash, Flask, session, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from python_files.tagging_from_xml_Mark import tags_from_xml
from python_files.xml_to_db import update_database
from python_files.get_click_data import *
from pymongo import MongoClient
from non_flask_functions import *
import click
import os
import flask_login
import json

"""
app.py

Within this script the main app is defined as an flask application.
First the environment variables and the login system are defnied as well as the login keys

"""
login_manager = flask_login.LoginManager()
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir,'uploads')
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
login_manager.init_app(app)

# define the login layer
users = {'tinka': {'pw': 'secret'}, 'mark': {'pw': 'secret'}, 'admin': {'pw': 'secret'}}
class User(flask_login.UserMixin):
    pass

"""
When a session is started, there is not a login registered to that user.
Therefore, the user is redirected to the /login tab where they can register.
"""
@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''
    click.echo('email')
    email = request.form['username']
    click.echo('hi')
    if request.form['pw'] == users[email]['pw']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        click.echo('hi')
        return redirect(url_for('step1'))

    return 'Bad login'

@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

"""
When the user is registered or an old session is continued.
The user is redirected to the index/welcome page on which he can give the foldername and the folder id.
After submitting these, the user is redirected to the next page inwhich they have to choose whether they want to tag the articles or retrieve the link datatrics
"""
@app.route("/")
@app.route("/index", methods=['GET', 'POST'])
@app.route("/step1")
@flask_login.login_required
def step1():
    retailers = get_retailers()
    print(retailers)
    if 'fid' in session:
        session['fid'] = ""
    if 'Foldernaam' in session:
        session['Foldernaam'] = ""
    if 'filename' in session:
        session['filename'] = ""
    return render_template('index.html', retailers = retailers)

@app.route("/folder_data.php")
@flask_login.login_required
def data():
    Foldernaam = request.args.get("Foldernaam")
    fid = request.args.get("fid")
    session['fid'] = fid
    session['Foldernaam'] = Foldernaam
    return redirect(url_for('keuzemenu'))

@app.route("/keuzemenu", methods=['GET', 'POST'])
@flask_login.login_required
def keuzemenu():
    return render_template('keuzemenu.html')

"""
If chosen to retrieve tags from the products, the user is asked to upload a .csv file containing the clickalble url's from the folder.
It is important that this csv contains a header with 'urls' with all urls in the row below and is of the csv format.
If an error occurs, the user is either warned or redirected.
"""
@app.route("/step2", methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('File extensions not allowed!')
            return render_template('upload_wrong_file.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session['filename'] = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploadcompleted'))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
@flask_login.login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/step3", methods=['GET', 'POST'])
@flask_login.login_required
def uploadcompleted():
    if request.method == 'POST':
        if request.form['button'] == 'Update de XML!':
            click.echo('button clicked!')
    return render_template('uploadcomplete.html', fid = session['fid'], foldernaam = session['Foldernaam'], filename = session['filename'])

"""
When the user eventually gets trough, they can decide to update the XML and retrieve the most up to date data from the company.
Afterwards, the tags can be added to the link. Both the product XML as the website are used for this. The code can be found in 'tagging_from_xml_Mark.py'.
After retrieving the data it is saved as an CSV in the csv_ouput folder
Finally this data can be downloaded by the user on the finishpage
"""

@app.route("/updateXML/<ans>", methods=['GET', 'POST'])
@flask_login.login_required
def HaiXML(ans):
    if ans == 'ja':
        updateXMLdatabase(session)
    return render_template('retrieve_tags.html')

@app.route("/retrieveTags", methods=['GET', 'POST'])
@flask_login.login_required
def getTags():
    links, csv_name = retrieve_tags(session)
    session['download_path'] = '/' + csv_name

    print('render templatje!')
    return render_template('finishpage.html', filename = session['download_path'])

@app.route('/csv_output/<filename>', methods=['GET', 'POST'])
@flask_login.login_required
def download(filename):
    uploads = os.path.join(basedir, 'csv_output')
    return send_from_directory(uploads, filename)

"""
If the user chooses to get the click data related to the links, it is assumed the tags are already
"""

@app.route("/clickhome", methods=['GET', 'POST'])
@flask_login.login_required
def clickhome():
    return render_template('clickmenu.html')

@app.route("/clickdata", methods=['GET', 'POST'])
@flask_login.login_required
def clickdata():
    data = generateClickData(session)
    for x in data:
        print(data)
    #click.echo(data)
    #json.save(data)

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    return('')
    return render_template('present_data.html', data = data)

if __name__ == "__main__":
    app.run()
