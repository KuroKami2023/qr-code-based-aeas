import cv2
from pyzbar.pyzbar import decode
import sqlite3
import numpy as np
import time

# Function to create a table for attendance if not exists
def create_attendance_table(cursor, table_name):
    try:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table_name}' (ID_Number TEXT, Name TEXT, Course TEXT, Time_In DATETIME DEFAULT CURRENT_TIMESTAMP, Time_Out DATETIME)")
    except sqlite3.Error as e:
        print(f"Error creating table '{table_name}': {e}")


# Function to insert student information into the attendance table
def insert_attendance(cursor, table_name, student_id, name, course, time_in, time_out):
    cursor.execute(f"INSERT INTO '{table_name}' (ID_Number, Name, Course, Time_In, Time_Out) VALUES (?, ?, ?, ?, ?)", (student_id, name, course, time_in, time_out))

# Function to check if the same student ID was scanned within the last minute
def check_duplicate_scan(last_scan_time):
    if time.time() - last_scan_time < 30:
        return True
    return False

def fetch_student_details(student_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Course FROM stud_list WHERE ID_Number=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def initialize_student_attendance():
    student_attendance = {}
    today_date = time.strftime("%Y_%m_%d")
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()

    # Create the attendance table if it doesn't exist
    create_attendance_table(cursor, today_date)

    # Fetch student attendance data
    try:
        cursor.execute(f"SELECT ID_Number, Time_In FROM '{today_date}' WHERE Time_Out IS NULL")
        rows = cursor.fetchall()
        for row in rows:
            student_id, time_in = row
            student_attendance[student_id] = time_in
    except sqlite3.OperationalError as e:
        print(f"Error fetching data from table '{today_date}': {e}")

    conn.close()
    return student_attendance


# Initialize student attendance
student_attendance = initialize_student_attendance()

cap = cv2.VideoCapture(0)
fps = 60
cap.set(cv2.CAP_PROP_FPS, fps)

results = []
last_scan_time = {}

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (600, 500))

    decoded_objects = decode(frame)

    for obj in decoded_objects:
        student_id = obj.data.decode('utf-8')

        # Check if the same student ID was scanned within the last minute
        if student_id in last_scan_time and check_duplicate_scan(last_scan_time[student_id]):
            continue

        student_details = fetch_student_details(student_id)
        if student_details:
            name, course = student_details
            print(student_id, name)

            # Determine if it's a time in or time out
            time_now = time.strftime("%Y-%m-%d %H:%M:%S")
            if student_id in student_attendance:
                time_in = student_attendance[student_id]
                time_out = time_now
                del student_attendance[student_id]  # Remove student from attendance dict

                # Update the database record
                today_date = time.strftime("%Y_%m_%d")
                conn = sqlite3.connect('database/data.db')
                cursor = conn.cursor()
                cursor.execute(f"UPDATE '{today_date}' SET Time_Out=? WHERE ID_Number=?", (time_out, student_id))
                conn.commit()
                conn.close()

            else:
                time_in = time_now
                time_out = None
                student_attendance[student_id] = time_in  # Add student to attendance dict

                # Create a table for today's attendance if not exists
                today_date = time.strftime("%Y_%m_%d")
                conn = sqlite3.connect('database/data.db')
                cursor = conn.cursor()
                create_attendance_table(cursor, today_date)
                insert_attendance(cursor, today_date, student_id, name, course, time_in, time_out)
                conn.commit()
                conn.close()

            last_scan_time[student_id] = time.time()  # Update last scan time
        else:
            results.append("Student ID not found in database")
            print("Student ID not found in database")

    # Draw bounding boxes for all detected objects
    for obj in decoded_objects:
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points

        n = len(hull)
        for j in range(0, n):
            cv2.line(frame, hull[j], hull[(j + 1) % n], (67, 235, 52), 3)

    # Draw text for each detected object
    for obj in decoded_objects:
        student_id = obj.data.decode('utf-8')
        student_details = fetch_student_details(student_id)
        if student_details:
            name, course = student_details
            text_size, _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            text_x = int((frame.shape[1] - text_size[0]) / 2)
            text_y = hull[0][1] - 10
            cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # Indicate if it's time in or time out
        if student_id in student_attendance:
            cv2.putText(frame, "Time In", (text_x, text_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)  # Dark green
        else:
            cv2.putText(frame, "Time Out", (text_x, text_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red


    cv2.imshow('QR Code Scanner', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
