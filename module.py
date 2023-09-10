from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

db = SQLAlchemy()


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String)
    done = db.Column(db.Boolean)
    create_at = db.Column(db.String)
    last_edit = db.Column(db.String, default=None)


class CreateNewForm(FlaskForm):
    text = StringField('הערה חדשה:', validators=[DataRequired(), Length(min=1, max=1000)])
    done = BooleanField('done')
    submit = SubmitField('submit')


class UpdateTodoForm(FlaskForm):
    text = StringField('עידכון הערה:', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('submit')


class MarkDone(FlaskForm):
    done = BooleanField('done')
    submit = SubmitField('submit')
