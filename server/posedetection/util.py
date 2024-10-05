from ultralytics import YOLO
import numpy as np
from headers import *


class Coord:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)


# Define function to calculate angle between vectors
def calculate_angle(a: Coord, b: Coord, c: Coord):
    """Calculate the angle between 3 points

    Args:
        a (Coord): First point
        b (Coord): Second point
        c (Coord): Third point

    Returns:
        float: Angle between the 3 points
    """
    ba = a - b
    bc = c - b

    # Calculate the dot product
    dot_product = np.dot(np.array([ba.x, ba.y]), np.array([bc.x, bc.y]))

    # Calculate the magnitudes
    magnitude_ba = np.linalg.norm(np.array([ba.x, ba.y]))
    magnitude_bc = np.linalg.norm(np.array([bc.x, bc.y]))

    # Calculate the angle in radians
    angle = np.arccos(dot_product / (magnitude_ba * magnitude_bc))

    # Convert the angle to degrees
    angle = np.degrees(angle)

    return angle


def get_average_xy(a, b):
    return Coord((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def get_keypoints(file):
    # Load the YOLOv8 pose model (pre-trained model from Ultralytics)
    model = YOLO("yolo11n-pose.pt")

    # Run inference on a video file
    results = model(
        source=file,
        task="pose",
        conf=0.7,
        show=True,
        save=False,
        project="predictions",
    )

    # Process the results
    for result in results:
        keypoints = result.keypoints  # Keypoints object for pose outputs
        return keypoints


def check_squat(coords, angles):
    warning_frames = []

    start_angle = angles["hip"][0]
    start_index = 0

    end_angle = angles["hip"][-1]
    end_index = -1
    for i in range(len(angles["hip"])):
        angle = angles["hip"][i]
        if 180 - angle < start_angle:
            start_angle = angle
            start_index = i
    if start_index = len(angles["hip"]) - 1:
        end_index = i
    else:
        for i in range(len(angles["hip"]) - 1, start_index + 1, -1):
            angle = angles["hip"][i]
            if 180 - angle < end_angle:
                end_angle = angle
                end_index = i

    initial_back_length = np.linalg.norm(
        np.array(coords["shoulder"][start_index].x) - coords["hip"][start_index].x,
        np.array(coords["shoulder"][start_index].y) - coords["hip"][start_index].y,
    )

    initial_calf_length = np.linalg.norm(
        np.array(coords["knee"][start_index].x) - coords["ankle"][start_index].x,
        np.array(coords["knee"][start_index].y) - coords["ankle"][start_index].y
    )
    for frame in range(start_index + 1, end_index):
        hip_angle = angles["hip"][frame]
        knee_angle = angles["knee"][frame]

        ratio = knee_angle / hip_angle
        back_length = np.linalg.norm(
            np.array(coords["shoulder"][frame].x) - coords["hip"][frame].x,
            np.array(coords["shoulder"][frame].y) - coords["hip"][frame].y,
        )
        calf_length = np.linalg.norm(
            np.array(coords["knee"][frame].x) - coords["ankle"][frame].x,
            np.array(coords["knee"][frame].y) - coords["ankle"][frame].y,
        )
        if ratio > SQUAT_WARNING_RATIO or back_length < initial_back_length * 0.9 or calf_length < initial_calf_length * 0.9:
            warning_frames.append(frame)

    return warning_frames


def check_bench(angles):
    UPPER_ANGLE_BOUND = 60
    LOWER_ANGLE_BOUND = 30

    warning_frames = []

    start_angle = angles["arm"][0]
    start_index = 0

    end_angle = angles["arm"][-1]
    end_index = -1
    for i in range(len(angles["arm"])):
        angle = angles["arm"][i]
        if 180 - angle < start_angle:
            start_angle = angle
            start_index = i
    for i in range(len(angles["arm"]) - 1, 0, -1):
        angle = angles["arm"][i]
        if 180 - angle < end_angle:
            end_angle = angle
            end_index = i

    for frame in range(start_index + 1, end_index):
        if (
            angles["shoulder"][frame] > UPPER_ANGLE_BOUND
            or angles["shoulder"][frame] < LOWER_ANGLE_BOUND
        ):
            warning_frames.append(frame)

    return warning_frames


def check_deadlift(coords, angles):
    warning_frames = []

    start_y_pos = coords["wrist"][0].y
    start_index = 0

    for i in range(len(coord["wrist"])):
        coord = coords["wrist"][i]
        if coord.y > start_y_pos:
            start_y_pos = coord.y
            start_index = i
            
    # Check for back compression
    initial_back_length = np.linalg.norm(
        np.array(coords["shoulder"][start_index].x) - coords["hip"][start_index].x,
        np.array(coords["shoulder"][start_index].y) - coords["hip"][start_index].y,
    )

    # Determine facing direction of user
    facing_left = 0
    if (coords["knee"][start_index].x < coords["ankle"[start_index].x]):
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
        if (back_length < initial_back_length * 0.9 or ratio > DEADLIFT_UPPER_WARNING_RATIO or ratio < DEADLIFT_LOWER_WARNING_RATIO or (coords["shoulder"][frame].x < coords["hip"][frame].x - margin_error and facing_left == 0) or (coords["shoulder"][frame].x > coords["hip"][frame].x + margin_error and facing_left == 1)):
            warning_frames.append(frame)
    return warning_frames