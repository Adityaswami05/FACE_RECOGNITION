from flask import Flask, render_template, request, Response
import sqlite3
from datetime import datetime
import csv
from io import StringIO
from datetime import date

app = Flask(__name__)

# Function to fetch real-time data from SQLite database
def get_attendance_data(selected_date):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Convert selected_date to formatted date
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    return attendance_data

# Function to generate CSV data dynamically based on real-time data
def generate_csv_data(selected_date):
    attendance_data = get_attendance_data(selected_date)

    csv_data = [['Name', 'Time']]  # Initialize CSV data with header row
    for row in attendance_data:
        csv_data.append(list(row))  # Append each row of data to CSV data

    return csv_data

@app.route('/')
def index():

    return render_template('index.html', selected_date=date.today(), no_data=False)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')

    attendance_data = get_attendance_data(selected_date)

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True)

    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)

@app.route('/download_csv')
def download_csv():
    selected_date = request.args.get('selected_date')  # Get selected date from query parameters

    csv_data = generate_csv_data(selected_date)
    attendance_data = get_attendance_data(selected_date)

    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerows(csv_data)

    response = Response(csv_output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=attendance.csv'
    return response

# Run the app on localhost:5000

if __name__ == '__main__':
    app.run(debug=True)
