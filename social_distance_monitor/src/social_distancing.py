#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" 
	Social-Distancing: Code for estimating the distance between people and show warning if they are standing too close to each other.
   
	IIT : Istituto italiano di tecnologia
	
    Pattern Analysis and Computer Vision (PAVIS) research line
	
    Description: Social-Distancing is an open-source project for automatically estimating interpersonal distance from uncalibrated RGB
	cameras. The software can be freely used for any non-commercial applications to assess compliance with safe distances. Given a frame
	captured from a scene, the algorithm first detects visible people in the scene using an off-the-shelf body pose detector and 
	estimates the height of the people through measuring the distance from their body joints. In the second step, the algorithm estimates
	an area of one meter around all the detected people. This distance is roughly estimated proportional to a typical human body height
	of 160 cm and can be used to draw a circle centered in human position in the scene. In the third step, the Homography of the scene
	is estimated given two parameters which essentially map the rectangular bird’s view model for the scene to the trapezoidal perspective
	view of the scene. These two parameters need to be manually tuned to estimate best the scene perspective. According to the Homography
	matrix, the safe circular distance for each person is converted to ellipsoids in perspective view. The people are considered to be
	staying in safe distance from each other if their ellipsoids do not collide. Conversely, if ellipsoids of two people collide, those
	people are considered as being in risk and their ellipsoids will be shown in red.
	
    Usage Example:  
		$ python3 social-distancing.py --image_in [path to the input image] --image_out [path to the result image] --horizontal_ratio 0.7 --vertical_ratio 0.7
        $ python3 social-distancing.py --stream_in [path to the input sequence] --stream_out [path to the result sequence] --horizontal_ratio 0.7 --vertical_ratio 0.7
	
        $ python3 social-distancing.py -h to get others parameters infos 
    
    Tested on ShanghaiTech [1] dataset.
	[1] Zhang, Yingying, et al. "Single-image crowd counting via multi-column convolutional neural network." Proceedings of the IEEE conference on computer vision and pattern recognition. 2016.
	
    Disclaimer:
	The information and content provided by this application is for information purposes only. 
	You hereby agree that you shall not make any health or medical related decision based in whole 
	or in part on anything contained within the application without consulting your personal doctor.
	The software is provided "as is", without warranty of any kind, express or implied, 
	including but not limited to the warranties of merchantability, 
	fitness for a particular purpose and noninfringement. In no event shall the authors, 
	PAVIS or IIT be liable for any claim, damages or other liability, whether in an action of contract, 
	tort or otherwise, arising from, out of or in connection with the software 
	or the use or other dealings in the software.
	
    LICENSE:
	This project is licensed under the terms of the MIT license.
	This project incorporates material from the projects listed below (collectively, "Third Party Code").  
	This Third Party Code is licensed to you under their original license terms.  
	We reserves all other rights not expressly granted, whether by implication, estoppel or otherwise.
	The software can be freely used for any non-commercial applications and it is useful
	for maintaining the safe social distance among people in pandemics. The code is open and can be 
	improved with your support, please contact us at socialdistancig@iit.it if you will to help us.
"""

import numpy as np
import cv2
import math
import itertools
import sys
import os
import argparse
import time
import json
import queue

from turbojpeg import TurboJPEG, TJPF_GRAY, TJSAMP_GRAY, TJFLAG_PROGRESSIVE

from social_distance_monitor.src.stream_server import StreamServer
from social_distance_monitor.src.response_server import ResponseServer

class SocialDistancing:
    colors = [(0, 255, 0), (0, 0, 255)]

    nd_color = [(153, 0, 51), (153, 0, 0),
                (153, 51, 0), (153, 102, 0),
                (153, 153, 0), (102, 153, 0),
                (51, 153, 0), (0, 153, 0),
                (0, 102, 153), (0, 153, 51),
                (0, 153, 102), (0, 153, 153),
                (0, 102, 153), (0, 51, 153),
                (0, 0, 153), (153, 0, 102),
                (102, 0, 153), (153, 0, 153),
                (102, 0, 153), (0, 0, 153),
                (0, 0, 153), (0, 0, 153),
                (0, 153, 153), (0, 153, 153),
                (0, 153, 153)
                ]

    connections = [(0, 16), (0, 15), (16, 18), (15, 17),
                   (0, 1), (1, 2), (2, 3), (3, 4),
                   (1, 5), (5, 6), (6, 7), (1, 8),
                   (8, 9), (9, 10), (10, 11),
                   (8, 12), (12, 13), (13, 14),
                   (11, 24), (11, 22), (22, 23),
                   (14, 21), (14, 19), (19, 20)]

    '''
        Initialize Object
    '''

    def __init__(self, args, op):
        # Ratio params
        horizontal_ratio = float(args.horizontal_ratio)
        vertical_ratio = float(args.vertical_ratio)

        # Open video capture
        self.cap = cv2.VideoCapture(args.stream_in)

        if not self.cap.isOpened():
            print("Error: Opening video stream or file {0}".format(
                args.stream_in))
            sys.exit(-1)

        # Get input size
        width = int(self.cap.get(3))
        height = int(self.cap.get(4))

        # Get image size
        im_size = (width, height)

        # Compute Homograpy
        self.homography_matrix = self.compute_homography(
            horizontal_ratio, vertical_ratio, im_size)

        self.background_masked = False
        # Open image backgrouns, if it is necessary
        if args.masked == "enabled":
            # Set masked flag
            self.background_masked = True

            # Load static background
            self.background_image = cv2.imread(args.background_in)

            # Close, if no background, but required
            if self.background_image is None:
                print("Error: Unable to load background image (flag enabled)")
                sys.exit(-1)

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()

        # Openpose params

        # Model path
        params["model_folder"] = args.openpose_folder

        # Face disabled
        params["face"] = False

        # Hand disabled
        params["hand"] = False

        # Net Resolution
        params["net_resolution"] = args.net_size

        # Gpu number
        params["num_gpu"] = 1  # Set GPU number

        # Gpu Id
        # Set GPU start id (not considering previous)
        params["num_gpu_start"] = 0

        # Starting OpenPose
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()

        # Process Image
        self.datum = op.Datum()

        # Json server
        self.dt_vector = {}

        # Client list
        self.stream_list = []

        # Initialize video server
        self.video_server = StreamServer(
            int(args.video_port), self.stream_list, "image/jpeg")
        self.video_server.activate()

        # Initialize json server
        self.js_server = ResponseServer(
            int(args.js_port), "application/json")
        self.js_server.activate()

        # turbo jpeg initialization
        self.jpeg = TurboJPEG()

        # Calibrate heigh value
        self.calibrate = float(args.calibration)

        # Actually unused
        self.ellipse_angle = 0

        # Body confidence threshold
        self.body_th = float(args.body_threshold)

        # Show confidence 
        self.show_confidence = True

    '''
        Draw Skelethon
    '''

    def draw_skeleton(self, frame, keypoints, colour):

        for keypoint_id1, keypoint_id2 in self.connections:
            x1, y1 = keypoints[keypoint_id1]
            x2, y2 = keypoints[keypoint_id2]

            if 0 in (x1, y1, x2, y2):
                continue

            pt1 = int(round(x1)), int(round(y1))
            pt2 = int(round(x2)), int(round(y2))

            cv2.circle(frame, center=pt1, radius=4,
                       color=self.nd_color[keypoint_id2], thickness=-1)
            cv2.line(frame, pt1=pt1, pt2=pt2,
                     color=self.nd_color[keypoint_id2], thickness=2)

    '''
        Compute skelethon bounding box
    '''

    def compute_simple_bounding_box(self, skeleton):
        x = skeleton[::2]
        x = np.where(x == 0.0, np.nan, x)
        left, right = int(round(np.nanmin(x))), int(round(np.nanmax(x)))
        y = skeleton[1::2]
        y = np.where(y == 0.0, np.nan, y)
        top, bottom = int(round(np.nanmin(y))), int(round(np.nanmax(y)))
        return left, right, top, bottom

    '''
        Compute Homograpy
    '''

    def compute_homography(self, H_ratio, V_ratio, im_size):
        rationed_hight = im_size[1] * V_ratio
        rationed_width = im_size[0] * H_ratio
        src = np.array([[0, 0], [0, im_size[1]], [
            im_size[0], im_size[1]], [im_size[0], 0]])
        dst = np.array([[0+rationed_width/2, 0+rationed_hight], [0, im_size[1]], [im_size[0],
                                                                                  im_size[1]], [im_size[0]-rationed_width/2, 0+rationed_hight]], np.int32)
        h, status = cv2.findHomography(src, dst)
        return h

    '''
        Compute overlap
    '''

    def compute_overlap(self, rect_1, rect_2):
        x_overlap = max(
            0, min(rect_1[1], rect_2[1]) - max(rect_1[0], rect_2[0]))
        y_overlap = max(
            0, min(rect_1[3], rect_2[3]) - max(rect_1[2], rect_2[2]))
        overlapArea = x_overlap * y_overlap
        if overlapArea:
            overlaps = True
        else:
            overlaps = False
        return overlaps

    '''
        Trace results
    '''

    def trace(self, image, skeletal_coordinates, draw_ellipse_requirements, is_skeletal_overlapped):
        bodys = []

        # Trace ellipses and body on target image
        i = 0

        for skeletal_coordinate in skeletal_coordinates[0]:
            if float(skeletal_coordinates[1][i])<self.body_th:
                continue

            # Trace ellipse
            cv2.ellipse(image,
                        (int(draw_ellipse_requirements[i][0]), int(
                            draw_ellipse_requirements[i][1])),
                        (int(draw_ellipse_requirements[i][2]), int(
                            draw_ellipse_requirements[i][3])), 0, 0, 360,
                        self.colors[int(is_skeletal_overlapped[i])], 3)

            # Trace skelethon
            skeletal_coordinate = np.array(skeletal_coordinate)
            self.draw_skeleton(
                image, skeletal_coordinate.reshape(-1, 2), (255, 0, 0))

            if int(skeletal_coordinate[2])!=0 and int(skeletal_coordinate[3])!=0 and self.show_confidence:
                cv2.putText(image, "{0:.2f}".format(skeletal_coordinates[1][i]),
                            (int(skeletal_coordinate[2]), int(skeletal_coordinate[3])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Append json body data, joints coordinates, ground ellipses
            bodys.append([[round(x) for x in skeletal_coordinate],
                          draw_ellipse_requirements[i], int(is_skeletal_overlapped[i])])

            i += 1

        self.dt_vector["bodys"] = bodys

    '''
        Evaluate skelethon height
    '''

    def evaluate_height(self, skeletal_coordinate):
        # Calculate skeleton height
        calculated_height = 0
        pointer = -1

        # Left leg
        joint_set = [12, 13, 14]

        # Check if leg is complete
        left_leg = True
        for k in joint_set:
            x = int(skeletal_coordinate[k*2])
            y = int(skeletal_coordinate[k*2+1])
            if x == 0 or y == 0:
                # No left leg, try right_leg
                joint_set = [9, 10, 11]
                left_leg = False
                break

        if not left_leg:
            joint_set = [9, 10, 11]
            # Check if leg is complete
            for k in joint_set:
                x = int(skeletal_coordinate[k*2])
                y = int(skeletal_coordinate[k*2+1])
                if x == 0 or y == 0:
                    # No left leg, no right leg, then body
                    joint_set = [0, 1, 8]
                    break

        # Evaluate leg height
        pointer = -1
        for k in joint_set[:-1]:
            pointer += 1
            if skeletal_coordinate[joint_set[pointer]*2]\
                    and skeletal_coordinate[joint_set[pointer+1]*2]\
                    and skeletal_coordinate[joint_set[pointer]*2+1]\
                    and skeletal_coordinate[joint_set[pointer+1]*2+1]:
                calculated_height = calculated_height +\
                    math.sqrt(((skeletal_coordinate[joint_set[pointer]*2] -
                                skeletal_coordinate[joint_set[pointer+1]*2])**2) +
                              ((skeletal_coordinate[joint_set[pointer]*2+1] -
                                skeletal_coordinate[joint_set[pointer+1]*2+1])**2))

        return calculated_height * self.calibrate

    '''
        Evaluate overlapping
    '''

    def evaluate_overlapping(self, ellipse_boxes, is_skeletal_overlapped, ellipse_pool):
        # checks for overlaps between people's ellipses, to determine risky or not
        for ind1, ind2 in itertools.combinations(list(range(0, len(ellipse_pool))), 2):
            
            is_overlap = cv2.bitwise_and(
                ellipse_pool[ind1], ellipse_pool[ind2])

            if is_overlap.any() and (not is_skeletal_overlapped[ind1] or not is_skeletal_overlapped[ind2]):
                is_skeletal_overlapped[ind1] = 1
                is_skeletal_overlapped[ind2] = 1

    '''
        Create Joint Array
    '''

    def create_joint_array(self, skeletal_coordinates):
        # Get joints sequence
        bodys_sequence = []
        bodys_probability = []
        for body in skeletal_coordinates:
            body_sequence = []
            body_probability = 0.0
            # For each joint put it in vetcor list
            for joint in body:
                body_sequence.append(joint[0])
                body_sequence.append(joint[1])

                # Sum joints probability to find body probability
                body_probability += joint[2]

            body_probability = body_probability/len(body)

            # Add body sequence to list
            bodys_sequence.append(body_sequence)
            bodys_probability.append(body_probability)

        # Assign coordiates sequence
        return [bodys_sequence, bodys_probability]

    '''
        Evaluate ellipses shadow, for each body
    '''

    def evaluate_ellipses(self, skeletal_coordinates, draw_ellipse_requirements, ellipse_boxes, ellipse_pool):
        for skeletal_coordinate in skeletal_coordinates:
            # Evaluate skeleton bounding box
            left, right, top, bottom = self.compute_simple_bounding_box(
                np.array(skeletal_coordinate))

            bb_center = np.array(
                [(left + right) / 2, (top + bottom) / 2], np.int32)

            calculated_height = self.evaluate_height(skeletal_coordinate)

            # computing how the height of the circle varies in perspective
            pts = np.array(
                [[bb_center[0], top], [bb_center[0], bottom]], np.float32)

            pts1 = pts.reshape(-1, 1, 2).astype(np.float32)  # (n, 1, 2)

            dst1 = cv2.perspectiveTransform(pts1, self.homography_matrix)

            # height of the ellipse in perspective
            width = int(dst1[1, 0][1] - dst1[0, 0][1])

            # Bounding box surrending the ellipses, useful to compute whether there is any overlap between two ellipses
            ellipse_bbx = [bb_center[0]-calculated_height,
                           bb_center[0]+calculated_height, bottom-width, bottom+width]

            # Add boundig box to ellipse list
            ellipse_boxes.append(ellipse_bbx)

            ellipse = [int(bb_center[0]), int(bottom),
                       int(calculated_height), int(width)]

            mask_copy = self.mask.copy()

            ellipse_pool.append(cv2.ellipse(mask_copy, (bb_center[0], bottom), (int(
                calculated_height), width), 0, 0, 360, (255, 255, 255), -1))

            draw_ellipse_requirements.append(ellipse)

    '''
        Analyze image and evaluate distances
    '''

    def distances_evaluate(self, image, background):
        ellipse_boxes = []

        draw_ellipse_requirements = []

        ellipse_pool = []

        # Assign input image to openpose
        self.datum.cvInputData = image

        # Start wrapper
        self.opWrapper.emplaceAndPop([self.datum])

        # Get openpose coordinates (rounding values)
        skeletal_coordinates = self.datum.poseKeypoints.tolist()

        # Trace on background
        if self.background_masked:
            image = background

        self.dt_vector['ts'] = int(round(time.time() * 1000))
        self.dt_vector['bodys'] = []

        if type(skeletal_coordinates) is list:
            # Remove probability from joints and get a joint position list
            skeletal_coordinates = self.create_joint_array(
                skeletal_coordinates)

            # Initialize overlapped buffer
            is_skeletal_overlapped = np.zeros(
                np.shape(skeletal_coordinates[0])[0])

            # Evaluate ellipses for each body detected by openpose
            self.evaluate_ellipses(skeletal_coordinates[0],
                                   draw_ellipse_requirements, ellipse_boxes, ellipse_pool)

            # Evaluate overlapping
            self.evaluate_overlapping(
                ellipse_boxes, is_skeletal_overlapped, ellipse_pool)

            # Trace results over output image
            self.trace(image, skeletal_coordinates,
                       draw_ellipse_requirements, is_skeletal_overlapped)

        # Send video to client queues
        self.send_image(self.stream_list, image, int(self.dt_vector['ts']))

        # Put json vector availble to rest requests
        self.js_server.put(bytes(json.dumps(self.dt_vector), "UTF-8"))

        return image

    '''
        Send image over queue list and then over http mjpeg stream
    '''

    def send_image(self, queue_list, image, ts):

        encoded_image = self.jpeg.encode(image, quality=80)
        # Put image into queue for each server thread
        for q in queue_list:
            try:
                block = (ts, encoded_image)
                q.put(block, True, 0.02)
            except queue.Full:
                pass

    '''
        Analyze video
    '''

    def analyze(self):
        while self.cap.isOpened():
            # Capture from image/video
            ret, image = self.cap.read()

            # Check image
            if image is None or not ret:
                os._exit(0)

            self.mask = np.zeros(image.shape, dtype=np.uint8)

            # Get openpose output
            if self.background_masked:
                background = self.background_image.copy()
            else:
                background = image

            image = self.distances_evaluate(image, background)

            # # Show image and wait some time [preview]
            # cv2.imshow('Social Distance', image)
            # cv2.waitKey(1)    
