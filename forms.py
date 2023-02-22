from flask_wtf import FlaskForm
from pyparsing import Optional
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Optional


class Instance2SubclassForm(FlaskForm):
    wikidata_id = StringField("Target Wikidata ID", validators=[DataRequired()])
    submit = SubmitField(
        """ Change "instance of" to "subclass of" (which is the case whenever we are not talking about a real-world substance that occupies space)."""
    )


class Category2WikidataForm(FlaskForm):
    wikipedia_category = StringField(
        "Target English Wikipedia Category", validators=[DataRequired()]
    )
    P279_value = StringField("The P279 value to add", validators=[DataRequired()])
    submit = SubmitField(""" Add P279 value to items in the category """)
