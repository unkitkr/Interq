from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from models import db, Users, OAuth, UserExperience, Companies
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from werkzeug.utils import secure_filename
import os
import uuid
import shortuuid
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:SudoAdmin123@localhost/interq"
app.config['SECRET_KEY'] = '0817PDNTSPA'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

linkedin_bp = make_linkedin_blueprint(scope=["r_liteprofile", "r_emailaddress"],
                                      client_id='78qzro4mo4fjas', client_secret='vFFSwRhq7bCII41S', redirect_to='dashboard')
app.register_blueprint(linkedin_bp, url_prefix='/login')

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
        print(current_user)
        return redirect("/dashboard")


@oauth_authorized.connect
def linkedin_logged_in(blueprint, token):
    account_info = linkedin.get('me')
    if account_info.ok:
        account_info_json = account_info.json()
        linkedin_id = account_info_json['id']
        user_exist = Users.query.filter_by(linkedinid=linkedin_id).first()
        email = linkedin.get(
            'https://api.linkedin.com/v2/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))')
        email = email.json()
        actual_email = email['elements'][0]['handle~']['emailAddress']
        if not user_exist:
            new_user = Users(linkedinid=linkedin_id, email=actual_email)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
            except Exception as e:
                db.session.rollback()
                print(e)
                return jsonify({
                    'Database Error': 'Internal data base error occured. Please try again later.'
                })
        else:
            login_user(user_exist)


@app.route("/dashboard")
@login_required
def dashboard():
    account_info = linkedin.get('me')
    if account_info.ok:
        account_info_json = account_info.json()
        name = account_info_json["localizedFirstName"] + \
            " " + account_info_json["localizedLastName"]
        profile_picture = linkedin.get(
            'https://api.linkedin.com/v2/me?projection=(id,profilePicture(displayImage~digitalmediaAsset:playableStreams))')
        profile_picture = profile_picture.json()

        pic_actual = profile_picture['profilePicture']['displayImage~']['elements'][3]['identifiers'][0]['identifier']
        reviews_written = UserExperience.query.filter_by(
            owner=current_user.uid).all()
        all_companies = Companies.query.all()
        payload = {
            'name': name,
            'email': current_user.email,
            'profile_picture': pic_actual,
            'reviews_written': reviews_written,
            'all_companies': all_companies,
        }
        print(payload)
        if 'message' in request.args:
            return render_template('dashboard.html', message = request.args['message'], payload=payload )
        return render_template('dashboard.html', payload=payload)
    else:
        return redirect('/')


@app.route("/addCompany", methods=['GET', 'POST'])
@login_required
def add_company():
    if request.method == 'POST':
        company_name = request.form['addCompanyname']
        company_logo = request.files['addCompanyImage']
        company_type = request.form['addCompanyType']
        filename = secure_filename(company_logo.filename)
        new_filename = shortuuid.ShortUUID().random(length=8)
        new_filename += os.path.splitext(filename)[1]
        check_exist = Companies.query.filter_by(name=company_name).all()
        if not check_exist:
            logo_location = os.path.join(
                app.config['UPLOAD_FOLDER'], new_filename)
            new_company = Companies(
                company_type=company_type, name=company_name, img=logo_location)
            try:
                company_logo.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], new_filename))
                db.session.add(new_company)
                db.session.commit()
                return redirect(url_for('.dashboard', message=company_name + " added successfully"))

            except Exception as e:
                db.session.rollback()
                print(e)
                return redirect(url_for('.dashboard', message="Error! Internal database error happened!"))
        else:
            return redirect(url_for('.dashboard', message="A company with same name exists. You may consider naming the company with specific department."))


if __name__ == '__main__':
    app.run(debug=True)
