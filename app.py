from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys
from urllib.parse import urlencode

app = Flask(__name__)

app.config["SECRET_KEY"] = "flasksurvey"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

responses = ["one"]
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
    return redirect("/questions/0")


@app.route("/questions/<int:question_id>")
def render_question(question_id):
    """Renders the current question to the user, or redirects to /completed if
    all questions have been answered.

    Contains basic validation to redirect user to their current question. (i.e. trying
    to manually update to access question out of order or non-existant question)
    """

    # User ties manually editing URL to prev question after finishing
    if len(current_survey.questions) == len(responses):
        flash("You've already completed this survey", "error")
        return redirect("/completed")

    # User tries skipping ahead / to non-existant question by editing URL.
    if len(responses) != question_id:
        flash(f"/questions/{question_id} is not a valid question.", "error")
        return redirect(f"/questions/{len(responses)}")

    # When user navigates to previous question, their submitted answers
    # are passed as URL Paremeters to auto fill / select answers.
    prev_answer = request.args.get("answer", "")
    prev_comment = request.args.get("comment", "")

    return render_template(
        "question.html",
        title=current_survey.title,
        question=current_survey.questions[question_id],
        current_question=question_id,
        total_questions=len(current_survey.questions) - 1,
        answer=prev_answer,
        comment=prev_comment,
    )


@app.route("/answer", methods=["POST"])
def submit_answer():
    """Adds users answer to responses list and then redirects to next question."""

    # answer is mandatory, while comment is optional.
    answer = request.form["answer"]
    comment = request.form.get("comment", "")

    responses.append({"answer": answer, "comment": comment})

    # User has answered all questions
    if len(current_survey.questions) == len(responses):
        return redirect("/completed")

    return redirect(f"/questions/{len(responses)}")


@app.route("/prev")
def render_previous_question():
    """Removes most recent response from responses list and redirects to the previous
    question, passing along response info as URL Paremeters for autofill."""

    prev_response = responses.pop()
    encoded_params = urlencode(prev_response)

    return redirect(f"/questions/{len(responses)}?{encoded_params}")
