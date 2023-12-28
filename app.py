from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

app.config["SECRET_KEY"] = "flasksurvey"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

responses = ['one']
current_survey = None


@app.route("/", methods=["GET", "POST"])
def index():
    """Home page for the survey site.
    GET - Renders form to select desired survey.
    POST - Grabs desired survey and renders instructions page."""

    if request.method == "GET":
        return render_template("index.html", surveys=surveys.keys())

    if request.method == "POST":
        global current_survey

        survey_id = request.form.get("survey_id")
        current_survey = surveys[survey_id]

        return render_template(
            "instructions.html",
            title=current_survey.title,
            instructions=current_survey.instructions,
        )


@app.route("/start", methods=["POST"])
def begin_survey():
    """Clears response data and redirects user to the first question."""

    responses.clear()
    return redirect('/questions/0')