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
    file_stem = file_name.split(".")[0]
    url = upload_video(f"posedetection/predict/{file_stem}.mp4", "howsmyform")

    # Process the results
    keypoints = []
    for result in results:
        keypoints.append(result.keypoints)  # Keypoints object for pose outputs
    return url, keypoints


def check_squat(coords, angles):
    warning_frames = []
    warning_messages = []

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
        if ratio > 1:
            warning_messages.append("Knees too far forward")
            warning_frames.append(frame_i)
        elif back_length < straight_back_length * 0.7:
            warning_messages.append("Back too bent")
            warning_frames.append(frame_i)

    # Remove warning frames within 0.5 seconds of one another
    while True:
        popped = False
        for i in range(len(warning_frames) - 1):
            if warning_frames[i + 1] - warning_frames[i] < 25:
                warning_frames.pop(i + 1)
                warning_messages.pop(i + 1)
                popped = True
                break

        if not popped:
            return warning_frames, warning_messages


def check_bench(angles, coords, indiv_coords):
    warning_frames = []
    warning_messages = []

    start_angle = angles["arm"][0]
    start_index = 0

    frame = 0
    for i in range(len(angles["arm"])):
        angle = angles["arm"][i]
        if 180 - angle < start_angle:
            start_angle = angle
            start_index = i
            frame = i

    shoulder_width = abs(
        indiv_coords["right_shoulder"][start_index][0]
        - indiv_coords["left_shoulder"][start_index][0]
    )

    frames = []
    for i in range(len(coords["elbow"])):
        if coords["elbow"][i][1] >= coords["shoulder"][i][1]:
            frames.append(i)

    for frame in frames:
        if abs(
            indiv_coords["left_shoulder"][frame][0]
            - indiv_coords["left_elbow"][frame][0]
        ) > shoulder_width * 0.8 or (
            abs(
                indiv_coords["right_shoulder"][frame][0]
                - indiv_coords["right_elbow"][frame][0]
            )
            > shoulder_width * 0.8
        ):
            warning_messages.append(
                "Elbows too far from body, try keeping them 45 degrees from torso"
            )
            warning_frames.append(frame)

    # Remove warning frames within 0.5 seconds of one another
    while True:
        popped = False
        for i in range(len(warning_frames) - 1):
            if warning_frames[i + 1] - warning_frames[i] < 25:
                warning_frames.pop(i + 1)
                warning_messages.pop(i + 1)
                popped = True
                break

        if not popped:
            return warning_frames, warning_messages


def check_deadlift(coords, angles):
    warning_frames = []
    warning_messages = []

    straight_angle = angles["hip"][0]
    straight_i = 0

    for i in range(len(angles["hip"])):
        angle = angles["hip"][i]
        if 180 - angle < straight_angle:
            straight_angle = angle
            straight_i = i

    initial_back_length = np.linalg.norm(
        [
            coords["shoulder"][straight_i][0] - coords["hip"][straight_i][0],
            coords["shoulder"][straight_i][1] - coords["hip"][straight_i][1],
        ]
    )

    # Determine facing direction of user
    facing_left = 0
    if coords["knee"][straight_i][0] < coords["ankle"][straight_i][0]:
        facing_left = 1

    for frame in range(len(angles["hip"])):
        hip_angle = angles["hip"][frame]
        knee_angle = angles["knee"][frame]

        ratio = knee_angle / hip_angle

        back_length = np.linalg.norm(
            [
                coords["shoulder"][frame][0] - coords["hip"][frame][0],
                coords["shoulder"][frame][1] - coords["hip"][frame][1],
            ]
        )

        margin_error = back_length / 5
        if back_length < initial_back_length * 0.7:
            warning_messages.append("Make sure to keep your back straight")
            warning_frames.append(frame)
        elif (ratio > 3 or ratio < 0.7) and coords["hip"][frame][1] < coords["knee"][
            frame
        ][1] - margin_error:
            warning_messages.append(
                "Lift with your entire body, not just your legs or back"
            )
            warning_frames.append(frame)
        elif (
            coords["shoulder"][frame][0] < (coords["hip"][frame][0] - margin_error)
            and facing_left == 0
            or coords["shoulder"][frame][0] > (coords["hip"][frame][0] + margin_error)
            and facing_left == 1
        ):
            warning_messages.append("Make sure not to lean back too much")
            warning_frames.append(frame)

    # Remove warning frames within 0.5 seconds of one another
    while True:
        popped = False
        for i in range(len(warning_frames) - 1):
            if warning_frames[i + 1] - warning_frames[i] < 25:
                warning_frames.pop(i + 1)
                warning_messages.pop(i + 1)
                popped = True
                break

        if not popped:
            return warning_frames, warning_messages
