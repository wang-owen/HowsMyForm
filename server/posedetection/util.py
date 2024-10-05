from ultralytics import YOLO
import numpy as np
import math


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
        if ratio > 1 or back_length < straight_back_length * 0.9:
            warning_frames.append(frame_i)

    return warning_frames


def check_bench(coords):
    UPPER_ANGLE_BOUND = 60
    LOWER_ANGLE_BOUND = 30

    warning_frames = []

    return warning_frames


def check_deadlift(angles):
    pass
