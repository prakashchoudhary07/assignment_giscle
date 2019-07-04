from pymongo import MongoClient
import time
import base64
import hashlib
import cv2
from socketIO_client import SocketIO, LoggingNamespace
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):

    return render(request, 'index.html')


frame = 0
old_count = 0
new_count = 0
total_count = 0


def add_to_database(args):
    try:
        connection = MongoClient('localhost', 27017)
        print("Connected successfully!!!")
        database = connection.body_detect
        collection = database.people_count
        result = collection.insert(args)
        print(result)
        print("Data inserted successfully!!!")

    except:
        print("Could not connect to MongoDB, Please try again ")

    finally:
        connection.close()
        print("Connection Closed")


def extract_data(args):
    global old_count, new_count, total_count
    print(time.time() - t)
    print(args)

    add_to_database(args)

    new_count = args["Output"]["total_person"]
    if(new_count-old_count > 0):
        total_count = total_count + (new_count-old_count)
        old_count = new_count
    elif(new_count-old_count < 0):
        old_count = new_count
    print(total_count)

    for key in args['Output'].keys():
        if key != 'total_person':
            x, y, h, w = (args['Output'][str(key)])
            x, y, h, w = int(x), int(y), int(h), int(w)
            cv2.rectangle(frame, (x, y), (x+h, y+w), (255, 255, 255))

    # cv2.imshow("frame",frame)


def detectpeople(request):

    try:
        token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im9tLnBjcHJha2FzaEBnbWFpbC5jb20iLCJ1c2VybmFtZSI6InByYWthc2giLCJmaXJzdG5hbWUiOiJQcmFrYXNoIn0.j8WsE7aMrgyIA59gg84DDy3BnlFUaDl3q7Umw7jbN9o'
        g_url = 'http://api.giscle.ml'

        socketio = SocketIO(g_url, 80, LoggingNamespace)
        socketio.emit('authenticate', {'token': token})

        cam = cv2.VideoCapture("http://93.87.72.254:8090/mjpg/video.mjpg")

    except:
        print("Error while making connection \nPlease check url and api key, authentaion error")
        exit()

    frame_count = 1

    while True:
        global t
        t = time.time()
        ret, frame = cam.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (900, 600))
        encoded, buffer = cv2.imencode('.jpg', frame)
        encoded_frame = base64.b64encode(buffer)
        encoded_frame = encoded_frame.decode('utf-8')
        socketio.emit('count_people', {'data': encoded_frame})
        socketio.on('response', extract_data)
        socketio.wait(0.0001)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    socketio.disconnect()
    cam.release()

    return HttpResponse("Detect people Counts")
