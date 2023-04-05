from flask import Flask
from flask import Flask, redirect, render_template, request, session
import os
from flask_discord import DiscordOAuth2Session
import jinja2
from reader import TOKEN, REDIRECT_URI, CLIENT_SECRET, CLIENT_ID, TRANSCRIPTS_PASSWORD, TRANSCRIPTS_USERNAME

# Create the Flask application and a random 32 character secret key
app = Flask(__name__)
app.secret_key = os.urandom(32)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

app.config["DISCORD_CLIENT_ID"] = CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = REDIRECT_URI
app.config["DISCORD_BOT_TOKEN"] = TOKEN

discord = DiscordOAuth2Session(app)

# Authorized username/password combo and list of valid discord user IDs
user = {"username": TRANSCRIPTS_USERNAME, "password": TRANSCRIPTS_PASSWORD}
valid_users = [608893895635370005, 455221909257453577]

# Create the default app route
@app.route('/', methods = ['POST', 'GET'])
def login():
    # If the user attempts to login, check the username and password against the ones in the dictionary
    try:
        if(request.method == 'POST'):
            username = request.form.get('username')
            password = request.form.get('password')     
            if username == user['username'] and password == user['password']:
                # If the username and password are correct, create a session and redirect to the ticket_search page
                session['user'] = username
                return redirect('/ticket_search')
            # Else, render the login_incorrect file
            return render_template('login_incorrect.html')
    except:
        pass

@app.route('/discord_login')
def discord_login():
    try:
        return discord.create_session()
    except:
        return render_template('login_incorrect.html')


@app.route('/callback')
async def callback():
    try:
        discord.callback()
    except:
        return render_template('login.html')
    # Get the user and check that their ID matches one of the IDs in the valid_users list
    disc_user = discord.fetch_user()
    if disc_user.id not in valid_users:
        return render_template('login.html')
    # If everything is good, show the ticket search page
    return redirect('/ticket_search')


@app.route('/ticket_search', methods=['GET'])
def ticket_search():
    # If the user has a valid session, return render the ticket_search.html file
    if('user' in session and session['user'] == user['username']) or discord.authorized:
        return render_template('ticket_search.html')
    # Otherwise, they are not signed in/have an invalid session, redirect to the login page
    return render_template('login.html')


@app.route('/ticket_search_submit', methods = ['POST', 'GET'])
def ticket_search_submit():
    if('user' in session and session['user'] == user['username']) or discord.authorized:
        if(request.method == 'POST'):
            ticket_num = request.form.get('ticket_num')
            try:
                return render_template(f'/transcripts/{ticket_num}.html')
            except jinja2.exceptions.TemplateNotFound:
                return render_template('ticket_not_found.html')
    # Otherwise, they are not signed in/have an invalid session, redirect to the login page
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    try:
        session.pop('user')
    except KeyError:
        pass
    # Try to revoke access from the Discord login
    try:
        discord.revoke()
    # Otherwise, pass
    except:
        pass

    return redirect('/')

# Routes for the terms of service and privacy policy pages
@app.route('/tos', methods=['GET'])
def tos():
    return render_template('terms_of_service.html')

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy_policy.html')

# If there is a 404 or 500 error, return render the login.html file
@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html')

@app.errorhandler(500)
def error_500(e):
    return render_template('login.html')

if __name__ == '__main__':
    # Run on localhost at port 5000
    app.run(host='localhost', port=5000)