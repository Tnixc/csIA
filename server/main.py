from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template("login.html")

@main.route("/home")
@login_required
def home():
    return render_template("base.html")

@main.route("/home/report")
@login_required
def report():
    return render_template("report.html")

@main.route("/home/manage")
@login_required
def manage():
    return render_template("base.html")