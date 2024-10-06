import os
import math
from ultralytics import YOLO
import numpy as np
import boto3
from dotenv import load_dotenv
from .headers import *

load_dotenv()


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


def upload_video(file_path, bucket_name, object_name=None):
    # Create a session using the R2 credentials
    s3_client = boto3.Session().client(
        service_name="s3",
        aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
        endpoint_url=os.environ.get("R2_CONNECTION_URL"),
    )

    # If no object name is specified, use the file name
    if object_name is None:
        object_name = file_path.split("/")[-1]

    s3_client.upload_file(file_path, bucket_name, object_name)
    return f"{os.environ.get('R2_PUBLIC_ENDPOINT')}/{bucket_name}/{object_name}"


def get_pose_estimation(file):
    # Load the YOLOv8 pose model (pre-trained model from Ultralytics)
    model = YOLO("yolo11n-pose.pt")

    # Run inference on a video file
    results = model(
        source=file,
        task="pose",
        conf=0.7,
        save=True,
        project="posedetection",
        boxes=False,
        exist_ok=True,
    )
    file_name = file.split("/")[-1]
    url = upload_video(f"posedetection/predict/{file_name}", "howsmyform")

    # Process the results
    keypoints = []
    for result in results:
        keypoints.append(result.keypoints)  # Keypoints object for pose outputs
    return url, keypoints


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

    start_angle = angles["arm"][0]
    start_index = 0

    bottom_pos = coords["elbow"][0]
    bottom_index = 0
    for i in range(len(angles["arm"])):
        angle = angles["arm"][i]
        pos = coords["elbow"][i]
        if 180 - angle < start_angle:
            start_angle = angle
            start_index = i
        if pos > bottom_pos:
            bottom_pos = pos
            bottom_index = i

    straight_upper_arm = np.linalg.norm(
        [
            coords("elbow")[start_index][0] - coords("shoulder")[start_index][0],
            coords("elbow")[start_index][1] - coords("shoulder")[start_index][1]
        ]
    )
    upper_arm_bound = straight_upper_arm * 0.8
    lower_arm_bound = straight_upper_arm * 0.4
    left_arm_length = np.linalg.norm(
        [
            indiv_coords("left_elbow")[bottom_index][0] - indiv_coords("left_shoulder")[bottom_index][0],
            indiv_coords("left_elbow")[bottom_index][1] - indiv_coords("left_shoulder")[bottom_index][1]
        ]
    )
    right_arm_length = np.linalg.norm(
        [
            indiv_coords("right_elbow")[bottom_index][0] - indiv_coords("right_shoulder")[bottom_index][0],
            indiv_coords("right_elbow")[bottom_index][1] - indiv_coords("right_shoulder")[bottom_index][1]
        ]
    )
    if (left_arm_length > upper_arm_bound or left_arm_length < lower_arm_bound or 
        right_arm_length > upper_arm_bound or right_arm_length < lower_arm_bound):
        warning_frames.append(bottom_index)
    
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
