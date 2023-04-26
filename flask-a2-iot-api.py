from flask import Flask, jsonify, request
import mysql.connector
import serial
import time
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)




@app.route('/api/data/latest')
def handle_fetch_data():
    # Execute a query to fetch data from the database
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM health_record ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    mydb.close()

    record = {
        "temperature": result['temperature'],
        "heart_rate": result['heart_rate'],
        "motion_detect": bool(result['motion_detect']),
        "fall_detect": bool(result['fall_detect']),
        "x": result['x'],
        "y": result['y'],
        "z": result['z'],
        "timestamp": str(result['timestamp'])
    }
    return jsonify(record)

@app.route('/api/data/table', methods=['GET'])
def get_table_data():
    # Retrieve query parameters
    page = int(request.args.get('page', default=1))
    limit = int(request.args.get('limit', default=10))

    # Connect to database
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)

    # Count total number of records
    cursor.execute("SELECT COUNT(*) AS count FROM health_record")
    count_result = cursor.fetchone()
    total = count_result['count']

    # Determine offset and limit for current page
    offset = (page - 1) * limit
    if offset < 0:
        offset = 0
    elif offset >= total:
        return jsonify({'total': total, 'data': []})

    # Retrieve data for current page
    cursor.execute("SELECT * FROM health_record ORDER BY timestamp DESC LIMIT %s OFFSET %s", (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    mydb.close()

    data = []
    for result in results:
        record = {
            "temperature": result['temperature'],
            "heart_rate": result['heart_rate'],
            "motion_detect": bool(result['motion_detect']),
            "fall_detect": bool(result['fall_detect']),
            "x": result['x'],
            "y": result['y'],
            "z": result['z'],
            "timestamp": str(result['timestamp'])
        }
        data.append(record)

    return jsonify({'total': total, 'data': data})


@app.route('/api/data', methods=['GET'])
def get_data():
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM health_record ORDER BY timestamp DESC")
    results = cursor.fetchall()
    cursor.close()
    mydb.close()

    data = []
    for result in results:
        record = {
            "temperature": result['temperature'],
            "heart_rate": result['heart_rate'],
            "motion_detect": bool(result['motion_detect']),
            "fall_detect": bool(result['fall_detect']),
            "x": result['x'],
            "y": result['y'],
            "z": result['z'],
            "timestamp": str(result['timestamp'])
        }
        data.append(record)

    return jsonify(data)

@app.route('/api/system-settings', methods=['GET'])
def get_setting_data():
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM settings WHERE id=1;")
    result = cursor.fetchone()
    cursor.close()
    mydb.close()

    return jsonify(result)

@app.route('/api/system-settings', methods=['PUT'])
def update_setting_data():
    data = request.json
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    sql = "UPDATE settings SET age=%s, fall_detect_threshold=%s, auto=%s where id=%s;"
    values = (data['age'], data['fall_detect_threshold'], data['auto'], data['id'])
    cursor.execute(sql, values)
    mydb.commit()

    cursor.close()
    mydb.close()

    return jsonify({'msg':'success'})

@app.route('/api/temp-settings', methods=['GET'])
def get_temp_setting_data():
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM temperature_settings WHERE id=1;")
    result = cursor.fetchone()
    cursor.close()
    mydb.close()

    return jsonify(result)

@app.route('/api/temp-settings', methods=['PUT'])
def update_temp_setting_data():
    data = request.json
    mydb = mysql.connector.connect(
        host="localhost",
        user="pi",
        password="20020908",
        database="sensor_db"
    )
    cursor = mydb.cursor(dictionary=True)
    sql = "UPDATE temperature_settings SET hypothermia=%s, mild_hypothermia=%s, normal=%s, mild_fever=%s, fever=%s, hyperpyrexia=%s where id=%s;"
    values = (data['hypothermia'], data['mild_hypothermia'], data['normal'], data['mild_fever'], data['fever'], data['hyperpyrexia'], data['id'])
    cursor.execute(sql, values)
    mydb.commit()

    cursor.close()
    mydb.close()

    return jsonify({'msg':'success'})




if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
    ser.flush()
    app.run(host='0.0.0.0',port=8080,debug=False)
