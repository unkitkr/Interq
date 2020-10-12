from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from models import db, Users, OAuth, UserExperience, Companies
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
import os, uuid
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:SudoAdmin123@localhost/interq"
app.config['SECRET_KEY'] = '0817PDNTSPA'

linkedin_bp = make_linkedin_blueprint(scope=["r_liteprofile","r_emailaddress"], client_id='78qzro4mo4fjas', client_secret='vFFSwRhq7bCII41S', redirect_to = 'dashboard'  )
app.register_blueprint(linkedin_bp, url_prefix= '/login')

db.app = app
db.init_app(app)
db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)




linkedin_bp.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@app.route('/', methods=['GET'])
def home_page():
    return render_template("index.html")


@app.route("/login")
def login():
    if not linkedin.authorized and not current_user.is_authenticated:
        return redirect(url_for("linkedin.login"))
    else:
        return redirect("/dashboard")

@oauth_authorized.connect
def linkedin_logged_in(blueprint, token):
    account_info = linkedin.get('me')
    if account_info.ok:
        account_info_json = account_info.json()
        linkedin_id = account_info_json['id']
        user_exist = Users.query.filter_by(linkedin_id = linkedin_id).first()
        if not user_exist: 
            name = account_info_json["localizedFirstName"] + " " + account_info_json["localizedLastName"]
            email = linkedin.get('https://api.linkedin.com/v2/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))')
            email = email.json()
            actual_email = email['elements'][0]['handle~']['emailAddress']
            profile_picture = linkedin.get('https://api.linkedin.com/v2/me?projection=(id,profilePicture(displayImage~digitalmediaAsset:playableStreams))')
            profile_picture = profile_picture.json()
            pic_actual = profile_picture['profilePicture']['displayImage~']['elements'][3]['identifiers'][0]['identifier']

            new_user = Users(linkedin_id = linkedin_id, name = name, email = actual_email, profile_photo = pic_actual)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'Database Error' : 'Internal data base error occured. Please try again later.'
                })
        else:
            login_user(user_exist)
        



    

@app.route("/dashboard")
@login_required
def dashboard():
    return str(current_user.name)
    










if __name__ == '__main__':
    app.run(debug=True)
