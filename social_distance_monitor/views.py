from django.shortcuts import render
from social_distance_monitor.src.social_distancing import SocialDistancing
import os
import sys
import threading

class dotdict(dict):
    # dot.notation access to dictionary attributes
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# Create your views here.
def social_distance_monitor(request):
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
        except ImportError as e:
            print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON`'
                  'in CMake and have this Python script in the right folder?')
            sys.exit(-1)
    except Exception as e:
        print(e)
        sys.exit(-1)

    '''
        Set Arguments 
    '''
    args = dict()

    # Path to the local OpenPose installation directory
    args["openpose_folder"] = "/home/meeexy/Downloads/openpose/models/"

    # Path to the video to process
    args["stream_in"] = os.path.join(dir_path, "static", "footages", "pexels_people_walking.mp4")

    # video streaming port
    args["video_port"] = "5002"

    # video streaming port
    args["js_port"] = "5005"

    # Select background image and set masked to enabled to mask the output frmae onto the selected background image
    args["masked"] = "disabled"

    # Path to the background image
    args["background_in"] = ""

    # Openpose network size
    args["net_size"] = "512x384"

    # calibrate each point of view with this value
    args["calibration"] = "1.0"

    # remove too low confidential body
    args["body_threshold"] = "0.2"

    # Ratio between the closest horizotal line of the scene to the furthest visible. It must be a float value in (0,1)
    args["horizontal_ratio"] = "0.7"

    # Ratio between the height of the trapezoid wrt the rectangular bird’s view scene (image height). It must be a float value in (0,1)
    args["vertical_ratio"] = "0.7"

    # Create social_distance object
    social_distance = SocialDistancing(dotdict(args), op)
    
    # Process the frames and streams the processed frames on '0.0.0.0:5002' and json response on '0.0.0.0:5005' by defualt
    social_distance.analyze()
    

def social_distancing_index(request):
    # render template
    return render(request, 'social_distancing.html', {})