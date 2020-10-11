from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from flask_login import  UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
import uuid
import datetime

db = SQLAlchemy()

class Users(db.Model,UserMixin):
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    linkedin_id = profile_photo = db.Column(db.String, nullable = False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique = True)
    date_of_joining = db.Column(db.DateTime, default = datetime.datetime.today().strftime('%d/%m/%Y'), nullable = False)
    profile_photo = db.Column(db.String, nullable = False)
    user_experiences = db.relationship('UserExperience', backref="Users")
    def get_id(self):
        return self.uid

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(UUID(as_uuid=True),  db.ForeignKey(Users.uid))
    user = db.relationship(Users)
    
class UserExperience(db.Model,UserMixin):
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    owner = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uid'))
    company = db.Column(UUID(as_uuid=True), nullable = False )
    number_of_rounds = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default = datetime.datetime.today().strftime('%d/%m/%Y'), nullable = False)

class Companies(db.Model,UserMixin):
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    img = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    company_type = db.Column(db.String(40), nullable=True)

    
    

    
