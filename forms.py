from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class Instance2SubclassForm(FlaskForm):
    wikidata_id = StringField("Target Wikidata ID", validators=[DataRequired()])
    submit = SubmitField(""" Change "instance of" to "subclass of" (which is the case whenever we are not talking about a real-world substance that occupies space).""")