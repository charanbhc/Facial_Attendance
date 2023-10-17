from flask import Flask, render_template, Response
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time
import csv

app = Flask(__name__)

path = './images'  # Update this path to match your image directory
images = []
personNames = []
myList = os.listdir(path)
for cu_img in myList:
    current_Img = cv2.imread(f'{path}/{cu_img}')
    images.append(current_Img)
    personNames.append(os.path.splitext(cu_img)[0])

def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def attendance(name):
    with open('./Attendance.csv', 'a', newline='') as f:
        time_now = datetime.now()
        tStr = time_now.strftime('%H:%M:%S')
        dStr = time_now.strftime('%d/%m/%Y')
        writer = csv.writer(f)
        writer.writerow([name, tStr, dStr])

encodeListKnown = faceEncodings(images)
print('All Encodings Complete!!!')

cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    last_attendance = {}
    with open('./Attendance.csv', 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) == 3:  # Ensure that each row has three columns
                last_attendance = {'image_name': row[0], 'time': row[1]}

    return render_template('index.html', last_attendance=last_attendance)

def gen():
    last_attendance_update = time.time()
    while True:
        ret, frame = cap.read()
        faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

        facesCurrentFrame = face_recognition.face_locations(faces)
        encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)
        current_time = time.time()

        for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = personNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                if current_time - last_attendance_update >= 30:  # 30 seconds
                    attendance(name)
                    last_attendance_update = current_time

            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask, render_template, request, redirect, url_for, Response
# import cv2
# import numpy as np
# import face_recognition
# import os
# from datetime import datetime
# import time

# app = Flask(__name__)

# path = './images'  # Update this path to match your image directory
# images = []
# personNames = []
# myList = os.listdir(path)
# print(myList)
# for cu_img in myList:
#     current_Img = cv2.imread(f'{path}/{cu_img}')
#     images.append(current_Img)
#     personNames.append(os.path.splitext(cu_img)[0])
# print(personNames)

# def faceEncodings(images):
#     encodeList = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
#     return encodeList

# def attendance(name):
#     with open('./Attendance.csv', 'a') as f:
#         time_now = datetime.now()
#         tStr = time_now.strftime('%H:M:S')
#         dStr = time_now.strftime('%d/%m/%Y')
#         f.writelines(f'\n{name},{tStr},{dStr}')

# encodeListKnown = faceEncodings(images)
# print('All Encodings Complete!!!')

# cap = cv2.VideoCapture(0)

# # Initialize the time for attendance update as a global variable
# last_attendance_update = time.time()

# @app.route('/')
# def index():
#     return render_template('index.html')

# def gen():
#     global last_attendance_update  # Declare it as a global variable
#     while True:
#         ret, frame = cap.read()
#         faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
#         faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

#         facesCurrentFrame = face_recognition.face_locations(faces)
#         encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

#         current_time = time.time()  # Move this line here to ensure last_attendance_update is defined

#         for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
#             matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
#             faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
#             # print(faceDis)
#             matchIndex = np.argmin(faceDis)

#             if matches[matchIndex]:
#                 name = personNames[matchIndex].upper()
#                 # print(name)
#                 y1, x2, y2, x1 = faceLoc
#                 y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#                 cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

#                 # Check if it's time to update attendance
#                 if current_time - last_attendance_update >= 30:  # 30 seconds
#                     attendance(name)
#                     last_attendance_update = current_time

#         _, jpeg = cv2.imencode('.jpg', frame)
#         frame = jpeg.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True)



