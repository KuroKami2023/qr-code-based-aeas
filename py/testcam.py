import cv2
from pyzbar.pyzbar import decode
import sqlite3
import numpy as np

def fetch_student_details(student_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Course FROM stud_list WHERE ID_Number=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row

cap = cv2.VideoCapture(0)
fps = 60
cap.set(cv2.CAP_PROP_FPS, fps)


results = []

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (400, 300))

    decoded_objects = decode(frame)
    
    for obj in decoded_objects:
        student_id = obj.data.decode('utf-8')
        student_details = fetch_student_details(student_id)
        if student_details:
            name, course = student_details
            result = f"ID Number: {student_id}, Student Name: {name}, Course: {course}"
            results.append(result)
            print(result)
        else:
            results.append("Student ID not found in database")
            print("Student ID not found in database")
        
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points
        
        n = len(hull)
        for j in range(0, n):
            cv2.line(frame, hull[j], hull[(j + 1) % n], (67, 235, 52), 3)

    cv2.imshow('QR Code Scanner', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

with open('qr_results.txt', 'w') as file:
    for result in results:
        file.write(result + '\n')
