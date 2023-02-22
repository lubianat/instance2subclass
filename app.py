import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from forms import Instance2SubclassForm, Category2WikidataForm, MultiSelectForm
from pathlib import Path
from wdcuration import render_qs_url, query_wikidata
from jinja2 import Template
from category_functions import (
    extract_ids_from_category,
    render_quickstatements_for_category,
)

# Configure application

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

HERE = Path(__file__).parent.resolve()
SPARQL = HERE.joinpath("sparql").resolve()


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@app.route("/")
def index():
    return render_template("index.html", form=form)


@app.route("/instance2subclass", methods=["GET", "POST"])
@app.route("/instance2subclass")
def instance2subclass():
    form = Instance2SubclassForm()
    if form.validate_on_submit():
        flash(
            "InstanceOf to SubclassOf change requested for id {}".format(
                form.wikidata_id.data
            )
        )
        instance2subclass = Template(
            SPARQL.joinpath("instance2subclassof.jinja.rq").read_text(encoding="UTF-8")
        )
        query = instance2subclass.render(base_id=form.wikidata_id.data)
        query_result = query_wikidata(query)
        qs = ""

        for result in query_result:
            qs += f"{result['itemQIDWithSignal']}|{result['property']}|{result['target_qid']}\n"

        qs_url = render_qs_url(qs)
        return render_template("instance2subclass.html", qs_url=qs_url, form=form)
    return render_template("instance2subclass.html", form=form)


@app.route("/category2wikidata", methods=["GET", "POST"])
@app.route("/category2wikidata")
def category2wikidata():
    form = Category2WikidataForm()
    if form.validate_on_submit():
        category = form.wikipedia_category.data
        P279_value = form.P279_value.data
        category_entries = extract_ids_from_category(category, save_json=False)
        statements = render_quickstatements_for_category(
            category, category_entries, P279_value=P279_value
        )
        qs_url = render_qs_url(statements)

        return render_template("category2wikidata.html", qs_url=qs_url, form=form)
    return render_template("category2wikidata.html", form=form)
