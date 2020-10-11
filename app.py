from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from models import db, Users, OAuth, UserExperience, Companies
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
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






@app.route('/', methods=['GET'])
def home_page():
    return render_template("index.html")


@app.route("/login")
def login():
    if not linkedin.authorized:
        return redirect(url_for("linkedin.login"))
    else:
        resp = linkedin.get('me')
        data = resp.json()
        name = data["localizedFirstName"] + " " + data["localizedLastName"]
        linkedin_id = data['id']
        resp_img = linkedin.get('me?projection=({},backgroundPicture(displayImage~digitalmediaAsset:playableStreams)'.format(linkedin_id))
        resp_img = resp_img.json()
        for x in resp_img:
            print(x)
        linkedin_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
        return redirect("/dashboard")
    

@app.route("/dashboard")
def dashboard():
    return "Party"
    










if __name__ == '__main__':
    app.run(debug=True)
