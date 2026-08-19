import os

from reports.report import generate_pdf
from predict import predict_heart_disease
from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from datetime import datetime

import mysql.connector

app = Flask(__name__)
app.secret_key = "heart_disease_project"

@app.route("/")
def home():
    return render_template("register.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        Full_Name = request.form.get("Full_Name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check password and confirm password
        if password != confirm_password:
            flash("Password and Confirm Password do not match!", "error")
            return redirect(url_for("register"))

        # MySQL connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="14072004",
            database="heart_disease_db"
        )

        cursor = connection.cursor()

        sql = """
            INSERT INTO users
            (Full_Name, email, username, password)
            VALUES (%s, %s, %s, %s)
        """

        values = (Full_Name, email, username, password)

        cursor.execute(sql, values)
        connection.commit()

        cursor.close()
        connection.close()

        # Success notification
        flash("Registration Successful!", "success")

        return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="14072004",
            database="heart_disease_db"
        )

        cursor = connection.cursor(buffered=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[3]

            return redirect(url_for("dashboard"))

        else:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    # GET request  return 
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor(buffered=True)

    # Total Registered Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_patients = cursor.fetchone()[0]

    # Total Predictions
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    # High Risk Patients
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='High'")
    high_risk = cursor.fetchone()[0]

    # Low Risk Patients
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='Low'")
    low_risk = cursor.fetchone()[0]

    # Medium Risk Patients
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='Medium'")
    medium_risk = cursor.fetchone()[0]

    # Today's Predictions
    cursor.execute("""
    SELECT COUNT(*)
    FROM predictions
    WHERE DATE(prediction_date) = CURDATE()
    """)

    today_predictions = cursor.fetchone()[0]

    risk_level = request.args.get("risk_level", "All")

    if risk_level == "All":
        cursor.execute("""
            SELECT
                p.patient_id,
                pt.patient_name,
                p.age,
                p.sex,
                p.prediction,
                p.probability,
                p.risk_level,
                p.prediction_date
            FROM predictions p
            LEFT JOIN patients pt
            ON p.patient_id = pt.patient_id
            ORDER BY p.prediction_date DESC
        """)
    else:
        cursor.execute("""
            SELECT
                p.patient_id,
                pt.patient_name,
                p.age,
                p.sex,
                p.prediction,
                p.probability,
                p.risk_level,
                p.prediction_date
            FROM predictions p
            LEFT JOIN patients pt
            ON p.patient_id = pt.patient_id
            WHERE p.risk_level = %s
            ORDER BY p.prediction_date DESC
        """, (risk_level,))

    prediction_history = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_predictions=total_predictions,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        today_predictions=today_predictions,
        prediction_history=prediction_history,
        risk_level=risk_level
    )


@app.route("/predict", methods=["GET", "POST"])
def predict():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        patient_name= request.form["patient_name"]
        age = request.form["age"]
        sex = request.form["sex"]
        chest_pain_type = request.form["chest_pain_type"]
        resting_bp = request.form["resting_bp"]
        cholesterol = request.form["cholesterol"]
        fasting_blood_sugar = request.form["fasting_blood_sugar"]
        resting_ecg = request.form["resting_ecg"]
        max_hr = request.form["max_hr"]
        exercise_angina = request.form["exercise_angina"]
        oldpeak = request.form["oldpeak"]
        st_slope = request.form["st_slope"]
        ca = request.form["ca"]
        thal = request.form["thal"]

        patient_data = [
            age,
            sex,
            chest_pain_type,
            resting_bp,
            cholesterol,
            fasting_blood_sugar,
            resting_ecg,
            max_hr,
            exercise_angina,
            oldpeak,
            st_slope,
            ca,
            thal
        ]

        result = predict_heart_disease(patient_data)

        prediction = result["Prediction"]
        probability = result["Probability"]
        risk_level = result["Risk Level"]

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="14072004",
            database="heart_disease_db"
        )

        cursor = connection.cursor()

        # Save patient information
        patient_sql = """
        INSERT INTO patients
        (patient_name, age, gender)
        VALUES (%s, %s, %s)
        """

        patient_values = (
            patient_name,
            age,
            sex
        )

        cursor.execute(patient_sql, patient_values)
        connection.commit()

        # Get automatically generated patient ID
        patient_id = cursor.lastrowid

        # Save prediction with patient ID
        prediction_sql = """
        INSERT INTO predictions
        (patient_id, age, sex, prediction, probability, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        prediction_values = (
            patient_id,
            age,
            sex,
            prediction,
            probability,
            risk_level
        )

        cursor.execute(prediction_sql, prediction_values)
        connection.commit()

        cursor.close()
        connection.close()

        prediction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pdf_file = generate_pdf(
            patient_id,
            patient_name,
            age,
            sex,
            prediction,
            probability,
            risk_level,
            prediction_date
        )

        return render_template(
            "result.html",
            result=result,
            pdf_file=pdf_file
        )

    return render_template("predict.html")






@app.route("/prediction")
def prediction():
    return render_template("prediction.html")







@app.route("/patients")
def patients():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    search = request.args.get("search", "").strip()

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor()

    if search:

        cursor.execute("""
            SELECT patient_id, patient_name, age, gender
            FROM patients
            WHERE patient_id = %s
               OR patient_name LIKE %s
            ORDER BY patient_id DESC
        """, (search, "%" + search + "%"))

    else:

        cursor.execute("""
            SELECT patient_id, patient_name, age, gender
            FROM patients
            ORDER BY patient_id DESC
        """)

    patients = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )

@app.route("/edit_patient/<int:patient_id>", methods=["GET", "POST"])
def edit_patient(patient_id):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        age = request.form["age"]
        gender = request.form["gender"]

        cursor.execute("""
            UPDATE patients
            SET patient_name = %s,
                age = %s,
                gender = %s
            WHERE patient_id = %s
        """, (
            patient_name,
            age,
            gender,
            patient_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("patients"))

    cursor.execute("""
        SELECT patient_id, patient_name, age, gender
        FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    patient = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_patient.html",
        patient=patient
    )

@app.route("/delete_patient/<int:patient_id>")
def delete_patient(patient_id):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor()

    # Delete related predictions first
    cursor.execute("""
        DELETE FROM predictions
        WHERE patient_id = %s
    """, (patient_id,))

    # Delete patient
    cursor.execute("""
        DELETE FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("patients"))

@app.route("/history/<int:patient_id>")
def history(patient_id):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor()

    # Get patient information
    cursor.execute("""
        SELECT patient_id, patient_name, age, gender
        FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    patient = cursor.fetchone()

    # Get patient's prediction history
    cursor.execute("""
        SELECT prediction, probability, risk_level, prediction_date
        FROM predictions
        WHERE patient_id = %s
        ORDER BY prediction_date DESC
    """, (patient_id,))

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "history.html",
        patient=patient,
        history=history
    )

@app.route("/download_history_report/<int:patient_id>/<prediction>")
def download_history_report(patient_id, prediction):

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.patient_id,
            p.patient_name,
            p.age,
            p.gender,
            pr.prediction,
            pr.probability,
            pr.risk_level,
            pr.prediction_date
        FROM patients p
        JOIN predictions pr
        ON p.patient_id = pr.patient_id
        WHERE p.patient_id = %s
        AND pr.prediction = %s
        ORDER BY pr.prediction_date DESC
        LIMIT 1
    """, (patient_id, prediction))

    record = cursor.fetchone()

    cursor.close()
    connection.close()

    if record is None:
        return "Prediction record not found"

    pdf_file = generate_pdf(
        record[0],   # Patient ID
        record[1],   # Patient Name
        record[2],   # Age
        record[3],   # Sex
        record[4],   # Prediction
        record[5],   # Probability
        record[6],   # Risk Level
        record[7]    # Prediction Date
    )

    return send_file(
        pdf_file,
        as_attachment=True
    )



@app.route("/download_generated_report/<path:filename>")
def download_generated_report(filename):

    #  actual filename 
    filename = os.path.basename(filename)

    file_path = os.path.join("reports", filename)

    if not os.path.exists(file_path):
        return "Report not found", 404

    return send_file(
        file_path,
        as_attachment=True
    )


import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")
if __name__ == "__main__":
    Timer(1,open_browser).start()
    app.run(debug=True)



