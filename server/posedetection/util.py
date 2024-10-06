import os
import math
from ultralytics import YOLO
import numpy as np
import boto3
from dotenv import load_dotenv

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
    R2_ACCESS_KEY_ID_id = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    r2_endpoint_url = os.environ.get("R2_CONNECTION_URL")

    # Create a session using the R2 credentials
    s3_client = boto3.Session().client(
        service_name="s3",
        aws_access_key_id=R2_ACCESS_KEY_ID_id,
        aws_secret_access_key=r2_secret_access_key,
        endpoint_url=r2_endpoint_url,
    )

    # If no object name is specified, use the file name
    if object_name is None:
        object_name = file_path.split("/")[-1]

    s3_client.upload_file(file_path, bucket_name, object_name)
    response = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": "howsmyform", "Key": object_name},
        ExpiresIn=3600,
    )
    return response


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
    signed_url = upload_video(f"posedetection/predict/{file_stem}.mp4", "howsmyform")

    # Process the results
    keypoints = []
    for result in results:
        keypoints.append(result.keypoints)  # Keypoints object for pose outputs
    return signed_url, keypoints


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


def check_bench(coords):
    pass


def check_deadlift(angles):
    pass
