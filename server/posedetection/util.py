from ultralytics import YOLO
import numpy as np
import math
from headers import *


def calculate_angle(a, b, c):
    A, B, C = a, b, c

    # Vector AB
    AB = [A[0] - B[0], A[1] - B[1]]

    # Vector BC
    BC = [C[0] - B[0], C[1] - B[1]]

    # Dot product of vectors AB and BC
    dot_product = AB[0] * BC[0] + AB[1] * BC[1]

    # Magnitudes of vectors AB and BC
    magnitude_AB = math.sqrt(AB[0] ** 2 + AB[1] ** 2)
    magnitude_BC = math.sqrt(BC[0] ** 2 + BC[1] ** 2)

    # Calculate the angle in radians and then convert it to degrees
    angle_radians = math.acos(dot_product / (magnitude_AB * magnitude_BC))
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees


def get_average_xy(a, b):
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]


def get_keypoints(file):
    # Load the YOLOv8 pose model (pre-trained model from Ultralytics)
    model = YOLO("yolo11n-pose.pt")

    # Run inference on a video file
    results = model(
        source=file,
        task="pose",
        conf=0.7,
        save=True,
        project="posedetection",
        name="prediction",
    )

    # Process the results
    keypoints = []
    for result in results:
        keypoints.append(result.keypoints)  # Keypoints object for pose outputs
    return keypoints


def check_squat(coords, angles):
    warning_frames = []

    straight_angle = angles["hip"][0]
    straight_i = 0

    for i in range(len(angles["hip"])):
        angle = angles["hip"][i]
        if 180 - angle < straight_angle:
            straight_angle = angle
            straight_i = i

    straight_back_length = np.linalg.norm(
        [
            (coords["shoulder"][straight_i][0]) - coords["hip"][straight_i][0],
            (coords["shoulder"][straight_i][1]) - coords["hip"][straight_i][1],
        ]
    )

    for frame_i in range(len(angles["hip"])):
        hip_angle = angles["hip"][frame_i]
        knee_angle = angles["knee"][frame_i]

        ratio = knee_angle / hip_angle
        print(hip_angle, knee_angle, ratio)
        # print(hip_angle, knee_angle)
        # print(coords["shoulder"][frame_i][0], coords["shoulder"][frame_i][1])
        # print(coords["hip"][frame_i][0], coords["hip"][frame_i][1])
        # print(coords["knee"][frame_i][0], coords["knee"][frame_i][1])
        # print(np.subtract(coords["hip"][frame_i], coords["shoulder"][frame_i]))
        # print(np.subtract(coords["hip"][frame_i], coords["knee"][frame_i]))
        # break
        back_length = np.linalg.norm(
            [
                (coords["shoulder"][frame_i][0]) - coords["hip"][frame_i][0],
                (coords["shoulder"][frame_i][1]) - coords["hip"][frame_i][1],
            ]
        )
        if ratio > 1 or back_length < straight_back_length * 0.8:
            warning_frames.append(frame_i)

    return warning_frames


def check_bench(angles, coords, indiv_coords):
    UPPER_ANGLE_BOUND = 60
    LOWER_ANGLE_BOUND = 30

    warning_frames = []

    start_angle = start_angle = angles["arm"][0]
    start_index = 0
    for i in range(len(angles["arm"])):
        angle = angles["arm"][i]
        if 180 - angle < start_angle:
            start_angle = angle
            start_index = i
    
    straight_upper_arm = np.linalg.norm(
        [
            coords("elbow")[0] - coords("shoulder")[0],
            coords("elbow")[1] - coords("shoulder")[1]
        ]
    )

    upper_arm_bound = straight_upper_arm * 0.8
    lower_arm_bound = straight_upper_arm * 0.4
    for frame_i in range(len(angles["arm"])):
        left_arm_length = np.linalg.norm(
            [
                indiv_coords("left_elbow")[0] - indiv_coords("left_shoulder")[0],
                indiv_coords("left_elbow")[1] - indiv_coords("left_shoulder")[1]
            ]
        )
        right_arm_length = np.linalg.norm(
            [
                indiv_coords("right_elbow")[0] - indiv_coords("right_shoulder")[0],
                indiv_coords("right_elbow")[1] - indiv_coords("right_shoulder")[1]
            ]
        )
        if (left_arm_length > upper_arm_bound or left_arm_length < lower_arm_bound or 
            right_arm_length > upper_arm_bound or right_arm_length < lower_arm_bound):
            warning_frames.append(frame_i)
    
    return warning_frames

def check_deadlift(coords, angles):
    warning_frames = []

    straight_angle = angles["hip"][0]
    straight_i = 0

    for i in range(len(angles["hip"])):
        angle = angles["hip"][i]
        if 180 - angle < straight_angle:
            straight_angle = angle
            straight_i = i

    initial_back_length = np.linalg.norm(
        np.array(coords["shoulder"][straight_i].x) - coords["hip"][straight_i].x,
        np.array(coords["shoulder"][straight_i].y) - coords["hip"][straight_i].y,
    )

     # Determine facing direction of user
    facing_left = 0
    if (coords["knee"][straight_i].x < coords["ankle"[straight_i].x]):
        facing_left = 1
        
    for frame in range(coords["knee"]):
        hip_angle = angles["hip"][frame]
        knee_angle = angles["knee"][frame]

        ratio = knee_angle / hip_angle

        back_length = np.linalg.norm(
            np.array(coords["shoulder"][frame].x) - coords["hip"][frame].x,
            np.array(coords["shoulder"][frame].y) - coords["hip"][frame].y,
        )

        margin_error = back_length / 5
        if (back_length < initial_back_length * 0.8 or ratio > DEADLIFT_UPPER_WARNING_RATIO or ratio < DEADLIFT_LOWER_WARNING_RATIO or (coords["shoulder"][frame].x < coords["hip"][frame].x - margin_error and facing_left == 0) or (coords["shoulder"][frame].x > coords["hip"][frame].x + margin_error and facing_left == 1)):
            warning_frames.append(frame)
    
    return warning_frames
