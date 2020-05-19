from django.shortcuts import render
from django.http import StreamingHttpResponse
from imutils.video import FileVideoStream
from tensorflow.keras.models import load_model
from face_mask_detect.src.detect_mask_video import detect_and_predict_mask
import imutils
import argparse
import time
import cv2
import os
import sys
import json

class VideoStream():
    def __init__(self):
        # initialize the video into our 
        video_url_path = os.path.join("face_mask_detect", "static", "footages", "stock_footage.webm")
        self.vs = FileVideoStream(path=video_url_path).start()

    def get_frame(self):
        frame = self.vs.read()
        return frame

    def reset(self):
        self.end_process()
        video_url_path = os.path.join("face_mask_detect", "static", "footages", "stock_footage.webm")
        self.vs = FileVideoStream(path=video_url_path).start()

    def end_process(self):
        self.vs.stop()

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
        frame = imutils.resize(frame, width=400)

        # processed data
        (face_count, mask_count) = detect_and_predict_mask(frame, faceNet, maskNet, args)

        ratio = str(mask_count / face_count if face_count > 0 else None)
        result = f'data: {{\ndata: "mask_count": {mask_count},\ndata: "face_count": {face_count},\ndata: "ratio": {ratio}\ndata: }}\n\n'

        # time.sleep(1.5)
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

