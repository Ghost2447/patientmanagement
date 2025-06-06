from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "hospital123"  # Change this to your secret password

DATA_FILE = "patients.json"
PASSWORD = "admin123"  # 🔐 Change to your desired password


# Load existing data or create a blank one
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Wrong password!")
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    data = load_data()
    today = str(date.today())

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        medicine = request.form["medicine"]
        quantity = int(request.form["quantity"])
        med_cost = float(request.form["med_cost"])
        consult = float(request.form["consult"])
        recommend = request.form["recommend"]

        entry = {
            "name": name,
            "age": age,
            "gender": gender,
            "medicine": medicine,
            "quantity": quantity,
            "med_cost": med_cost,
            "consult": consult,
            "recommend": recommend
        }

        if today not in data:
            data[today] = []

        data[today].append(entry)
        save_data(data)
        return redirect(url_for("dashboard"))

    today_data = data.get(today, [])
    total_med = sum(p["med_cost"] * p["quantity"] for p in today_data)
    total_consult = sum(p["consult"] for p in today_data)
    total_income = total_med + total_consult

    return render_template("dashboard.html", patients=today_data, med=total_med, consult=total_consult, total=total_income)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
