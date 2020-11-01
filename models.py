from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from flask_login import  UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
import uuid
import datetime

db = SQLAlchemy()

class Users(db.Model,UserMixin):
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    linkedinid = db.Column(db.String, nullable = False, unique = True)
    name = db.Column(db.String, nullable = False, unique = False)
    email = db.Column(db.String, nullable=False, unique = True)
    date_of_joining = db.Column(db.DateTime, default = datetime.datetime.today().strftime('%Y/%m/%d'), nullable = False)
    user_experiences = db.relationship('UserExperience', backref="users")
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
    recruitment_type = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    difficulty_level = db.Column(db.Integer, nullable = False)
    experience_level = db.Column(db.Integer, nullable = False)
    created_on = db.Column(db.DateTime, default = datetime.datetime.today().strftime('%Y/%m/%d'), nullable = False)

class Companies(db.Model,UserMixin):
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    img = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    company_type = db.Column(db.String(40), nullable=True)

    
    

    
