from flask import Flask, render_template, request, redirect, jsonify, url_for, session, Markup
from models import db, Users, OAuth, UserExperience, Companies
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from werkzeug.utils import secure_filename
from sqlalchemy import func, distinct
import os
import uuid
import shortuuid
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
UPLOAD_FOLDER = 'static/uploads'


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
        name = account_info_json["localizedFirstName"] + \
            " " + account_info_json["localizedLastName"]
        user_exist = Users.query.filter_by(linkedinid=linkedin_id).first()
        email = linkedin.get(
            'https://api.linkedin.com/v2/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))')
        email = email.json()
        actual_email = email['elements'][0]['handle~']['emailAddress']
        if not user_exist:
            new_user = Users(linkedinid=linkedin_id,
                             email=actual_email, name=name)
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
    session['initial_review_request'] = 0
    if account_info.ok:
        account_info_json = account_info.json()
        name = account_info_json["localizedFirstName"] + \
            " " + account_info_json["localizedLastName"]
        profile_picture = linkedin.get(
            'https://api.linkedin.com/v2/me?projection=(id,profilePicture(displayImage~digitalmediaAsset:playableStreams))')
        profile_picture = profile_picture.json()

        pic_actual = profile_picture['profilePicture']['displayImage~']['elements'][3]['identifiers'][0]['identifier']
        session["profile_picture"] = pic_actual
        reviews_written = UserExperience.query.filter_by(
            owner=current_user.uid).all()
        all_companies = Companies.query.all()
        company_review_data = []
        for company in all_companies:
            number = len(UserExperience.query.filter_by(
                company=company.uid).all())
            company_name = company.name
            company_uid = company.uid
            company_data = (company_name, company_uid, number)
            company_review_data.append(company_data)

        payload = {
            'name': name,
            'email': current_user.email,
            'profile_picture': pic_actual,
            'reviews_written': reviews_written,
            'all_companies': company_review_data,
        }
        if 'message' in request.args:
            return render_template('dashboard.html', message=request.args['message'], payload=payload)
        return render_template('dashboard.html', payload=payload)
    else:
        return redirect('/')


@app.route("/getreviews")
@login_required
def get_reviews():
    review_count = UserExperience.query.count()
    if session['initial_review_request'] >= review_count:
        return jsonify({})
    results = []
    required_review = UserExperience.query.offset(session['initial_review_request']).limit(8).all()
    print (len(required_review))
    print(session['initial_review_request'])
    session['initial_review_request'] += 8
    for reviews in required_review:
        user_details = Users.query.filter_by(uid=reviews.owner).first()
        company_details = Companies.query.filter_by(
            uid=reviews.company).first()
        data = [
            user_details.name,
            reviews.role,
            company_details.name,
            reviews.created_on,
            company_details.img,
            reviews.uid,
            reviews.difficulty_level,
            reviews.experience_level,
        ]
        results.append(data)
    return jsonify(results)

@app.route("/getspecificcompany/<id>")
@login_required
def specific_company_review(id):
    company_id = id
    reviews = UserExperience.query.filter_by(company = company_id).all()
    company_details = Companies.query.filter_by(uid = company_id).first()
    review_list = []
    for review in reviews:
        user_details = Users.query.filter_by(uid = review.owner).first()
        payload = {
                "user_name": user_details.name,
                "position":review.role,
                "date":review.created_on,
                "logo":company_details.img,
                "review_id":review.uid,
                "difficulty_level":review.difficulty_level,
                "experience":review.experience_level,
        }
        review_list.append(payload)

    return render_template("companyreview.html", reviews = review_list, company = company_details, current_user = current_user, profile_pic = session["profile_picture"])


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


@app.route("/addReview", methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        company_uid = request.form['reviewCompanyName']
        number_of_rounds = request.form['rounds']
        role = request.form['reviewRole']
        recruitment_type = request.form['reviewRecruitType']
        description = request.form['details']
        difficulty_level = request.form['difficultyLevel']
        experience_level = request.form['experienceLevel']

        new_review = UserExperience(
            owner=current_user.uid, company=uuid.UUID(company_uid), number_of_rounds=number_of_rounds, role=role,
            recruitment_type=recruitment_type, description=description, difficulty_level=difficulty_level, experience_level=experience_level)
        try:
            db.session.add(new_review)
            db.session.commit()
            return jsonify({
                'success': 'Your review recorded successfully. Refresh to see your magic 🤩'
            })

        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({
                'error': "Opps! It's on us. we went wrong. 😟"
            })


@app.route("/deleteexperience/<id>", methods=['GET', 'POST'])
@login_required
def delete_review(id):
    review = UserExperience.query.filter_by(uid = id).first()
    if review and  review.owner == current_user.uid:
        try:
            db.session.delete(review)
            db.session.commit()
            return redirect(url_for('.dashboard', message="Your review was deleted successfully. 🥳"))
        except Exception as e:
            db.session.rollback()
            print(e)
            return url_for('.dashboard', message="Opps! It's on us. we went wrong. 😟")
    else:
        return url_for('.dashboard', message="Opps! did you try to access something, which you weren't supposed to? 🤨")


@app.route("/editexperience/<id>", methods=['GET', 'POST'])
@login_required
def edit_review(id):
    print(request.form)
    if request.method == "POST":
        review = UserExperience.query.filter_by(uid = id).first()
        print(review)
        rounds = request.form["no_rounds"]
        position = request.form["role"]
        experience = request.form["experience"]
        difficulty = request.form["difficulty"]
        exp = request.form["exp"]
        print(review.owner == current_user.uid)
        if review and review.owner == current_user.uid:
            try:
                UserExperience.query.filter_by(uid = id).update(dict(number_of_rounds = rounds, role = position, description = experience, difficulty_level = difficulty, experience_level = exp  ))
                db.session.commit()
                return redirect(url_for('.dashboard', message="Your review was edited successfully. 🥳"))
            except Exception as e:
                db.session.rollback()
                print(e)
                return redirect(url_for('.dashboard', message="Opps! It's on us. we went wrong. 😟"))
        else:
            return redirect(url_for('.dashboard', message="Opps! did you try to access something, which you weren't supposed to? 🤨"))


@app.route("/viewexperience/<id>", methods=['GET', 'POST'])
@login_required
def view_review(id):
    if request.method == "GET":
        exp_id  = id
        review_detail = UserExperience.query.filter_by(uid = exp_id).first_or_404()
        company_details = Companies.query.filter_by(uid = review_detail.company).first()
        contributor = Users.query.filter_by(uid = review_detail.owner).first()
        is_author = False
        if contributor.uid == current_user.uid:
            is_author = True
        payload = {
            "review_id": exp_id,
            "company": company_details.name,
            "profile_picture" : session["profile_picture"],
            "number_rounds": review_detail.number_of_rounds,
            "position": review_detail.role,
            "written_by" : contributor.name,
            "onoffcampus" : review_detail.recruitment_type,
            "description": Markup(review_detail.description),
            "difficulty_level": review_detail.difficulty_level,
            "experience_level": review_detail.experience_level,
            "created_on": review_detail.created_on,
            "is_author": is_author
        }
        return render_template('experience.html', payload = payload, user_detail = current_user)
        
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    del linkedin_bp.token
    print(current_user.is_authenticated)
    return redirect("https://linkedin.com/m/logout")

@app.route("/team", methods=['GET'])
def team():
    return render_template("features.html")


@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
