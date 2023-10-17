from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

app = Flask(__name__)

# Define the path to the directory containing images of people you want to recognize
path = './images'  # Update this path to match your image directory

images = []
personNames = []
myList = os.listdir(path)

# Load images and extract person names from the file names
for cu_img in myList:
    current_Img = cv2.imread(f'{path}/{cu_img}')
    images.append(current_Img)
    personNames.append(os.path.splitext(cu_img)[0])

# Function to compute face encodings for a list of images
def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Function to mark attendance
def attendance(name):
    with open('./Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            time_now = datetime.now()
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.writelines(f'\n{name},{tStr},{dStr}')

encodeListKnown = faceEncodings(images)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            # Read the uploaded image
            image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            
            # Process the uploaded image for facial recognition
            facesCurrentFrame = face_recognition.face_locations(image)
            encodesCurrentFrame = face_recognition.face_encodings(image, facesCurrentFrame)

            for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = personNames[matchIndex].upper()
                    attendance(name)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask
# app = Flask(__name__)
# @app.route ('/')
# def index():
#     return "Hello World 🌍"
# if __name__== "__main__":
#     app.run(debug=True)