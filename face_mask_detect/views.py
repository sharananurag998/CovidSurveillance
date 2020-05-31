from django.shortcuts import render
from django.http import StreamingHttpResponse
from imutils.video import FileVideoStream
from tensorflow.keras.models import load_model
from face_mask_detect.src.detect_mask_video import detect_and_predict_mask
from turbojpeg import TurboJPEG

from social_distance_monitor.src.stream_server import StreamServer
from social_distance_monitor.src.response_server import ResponseServer

import imutils
import argparse
import time
import cv2
import os
import sys
import json
import queue
class VideoStream():
    def __init__(self):
        # initialize the video into our 
        video_url_path = os.path.join("face_mask_detect", "static", "footages", "cottonbro_2.mp4")
        self.vs = FileVideoStream(path=video_url_path).start()

        # Client list
        self.stream_list = []

        # Initialize video server
        self.video_server = StreamServer(
            5001, self.stream_list, "image/jpeg")
        self.video_server.activate()

        # Initialize json server
        self.js_server = ResponseServer(
            5003, "application/json")
        self.js_server.activate()

        # turbo jpeg initialization
        self.jpeg = TurboJPEG()


    def get_frame(self):
        frame = self.vs.read()
        return frame

    def reset(self):
        self.end_process()
        video_url_path = os.path.join("face_mask_detect", "static", "footages", "cottonbro_2.mp4")
        self.vs = FileVideoStream(path=video_url_path).start()

    def end_process(self):
        self.vs.stop()

    def send_image(self, queue_list, image, ts):
        encoded_image = self.jpeg.encode(image, quality=80)
        # Put image into queue for each server thread
        for q in queue_list:
            try:
                block = (ts, encoded_image)
                q.put(block, True, 0.02)
            except queue.Full:
                pass

# instance of our VideoStream
vstream = VideoStream()

# Generates surveillance data to Stream
def gen_surveillance_data():
    # declare path to face_detector serialised model and the face detector model
    args = {
        "face": "face_mask_detect/src/face_detector",
        "model": "face_mask_detect/src/mask_detector.model",
        "confidence": 0.5
    }

    # load our serialized face detector model from disk
    print("[INFO] loading face detector model...")
    prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
    weightsPath = os.path.sep.join([args["face"],
        "res10_300x300_ssd_iter_140000.caffemodel"])
    faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    print("[INFO] loading face mask detector model...")
    maskNet = load_model(args["model"])

    # initialise variables
    mask_count = 0
    face_count = 0

    while True:
        # read frames from the loaded VideoStream
        frame = vstream.vs.read()
        frame = imutils.resize(frame, width=800)

        # processed data
        (locs, preds, face_count, mask_count) = detect_and_predict_mask(frame, faceNet, maskNet, args)

        # loop over the detected face locations and their corresponding
        # locations
        for (box, pred) in zip(locs, preds):
            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            # determine the class label and color we'll use to draw
            # the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output
            # frame
            cv2.putText(frame, label, (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        # Send video to client queues
        vstream.send_image(vstream.stream_list, frame, int(int(round(time.time() * 1000))))

        # Put json vector availble to rest requests
        # vstream.js_server.put(bytes(json.dumps(result), "UTF-8"))

        ratio = mask_count / face_count if face_count > 0 else None
        result = '\ndata: {\n' + 'data: "mask_count": ' + str(mask_count) + ',\n' + 'data: "face_count": ' + str(face_count) + ',\n' + 'data: "ratio": ' + str(ratio) + '\n' + 'data: }\n\n'
        
        yield result
        

def get_surveillance_data(request):
    try:
        response = StreamingHttpResponse(gen_surveillance_data(), content_type='text/event-stream')
    except:
        print("Cannot make a StreamingHttpResponse.")
        vstream.end_process()
    # response['Content-Disposition'] = "inline"        # Defaults to inline
    vstream.end_process()
    return response

def surveillance_view(request):
    global vstream
    vstream.reset()
    return render(request, 'surveillance.html', {})

