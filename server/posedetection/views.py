from collections import defaultdict
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import util
from .headers import *


@api_view(["POST"])
def check_form(request):
    # Get file from request body video-upload
    if request.method == "POST":
        # Get the uploaded file
        file = request.FILES.get("video-upload")

        if file:
            # Save the file
            file_name = default_storage.save(
                f"posedetection/uploads/{file.name}", ContentFile(file.read())
            )
            # get path of file url after saving
            file_url = "/".join(default_storage.url(file_name).split("/")[1:])

            movement = request.data["movement"]

            if movement not in ["bench", "squat", "deadlift"]:
                return Response(
                    {"message": "Invalid movement type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            estimation = util.get_pose_estimation(file_url)
            keypoints = estimation[1]

            angles = defaultdict(list)
            coords = defaultdict(list)
            indiv_coords = defaultdict(list)
            for keypoint in keypoints:
                xy = keypoint.xy[0]

                indiv_coords["left_shoulder"].append(xy[LEFT_SHOULDER])
                indiv_coords["right_shoulder"].append(xy[RIGHT_SHOULDER])

                indiv_coords["left_elbow"].append(xy[LEFT_ELBOW])
                indiv_coords["right_elbow"].append(xy[RIGHT_ELBOW])

                shoulder = util.get_average_xy(xy[LEFT_SHOULDER], xy[RIGHT_SHOULDER])
                coords["shoulder"].append(shoulder)

                elbow = util.get_average_xy(xy[LEFT_ELBOW], xy[RIGHT_ELBOW])
                coords["elbow"].append(elbow)

                wrist = util.get_average_xy(xy[LEFT_WRIST], xy[RIGHT_WRIST])
                coords["wrist"].append(wrist)

                hip = util.get_average_xy(xy[LEFT_HIP], xy[RIGHT_HIP])
                coords["hip"].append(hip)

                knee = util.get_average_xy(xy[LEFT_KNEE], xy[RIGHT_KNEE])
                coords["knee"].append(knee)

                ankle = util.get_average_xy(xy[RIGHT_ANKLE], xy[RIGHT_ANKLE])
                coords["ankle"].append(ankle)

                angles["hip"].append(util.calculate_angle(shoulder, hip, knee))
                angles["shoulder"].append(util.calculate_angle(hip, shoulder, elbow))
                angles["knee"].append(util.calculate_angle(hip, knee, ankle))
                angles["arm"].append(util.calculate_angle(shoulder, elbow, wrist))

            if movement == "squat":
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "url": estimation[0],
                        "warning_frames": util.check_squat(coords, angles),
                    },
                )
            if movement == "bench":
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "url": estimation[0],
                        "warning_frames": util.check_bench(
                            angles, coords, indiv_coords
                        ),
                    },
                )
            if movement == "deadlift":
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "url": estimation[0],
                        "warning_frames": util.check_deadlift(coords, angles),
                    },
                )
    return Response(
        {"message": "No keypoint found"}, status=status.HTTP_400_BAD_REQUEST
    )
