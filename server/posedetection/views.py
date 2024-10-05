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
        file = request.FILES.get("file")

        if file:
            # Save the file
            file_name = default_storage.save(
                f"uploads/{file.name}", ContentFile(file.read())
            )
            file_url = default_storage.url(file_name)

            movement = request.data["movement"]

            if movement not in ["bench", "squat", "deadlift"]:
                return Response(
                    {"message": "Invalid movement type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            keypoints = util.get_keypoints(file_url)

            if keypoints:
                angles = defaultdict(list)
                coords = defaultdict(list)
                for keypoint in keypoints:
                    shoulder = util.get_average_xy(
                        keypoint.xy[LEFT_SHOULDER], keypoint.xy[RIGHT_SHOULDER]
                    )
                    coords["shoulder"].append(shoulder)

                    elbow = util.get_average_xy(
                        keypoint.xy[LEFT_ELBOW], keypoint.xy[RIGHT_ELBOW]
                    )
                    coords["elbow"].append(elbow)

                    wrist = util.get_average_xy(
                        keypoint.xy[LEFT_WRIST], keypoint.xy[RIGHT_WRIST]
                    )
                    coords["wrist"].append(wrist)

                    hip = util.get_average_xy(
                        keypoint.xy[LEFT_HIP], keypoint.xy[RIGHT_HIP]
                    )
                    coords["hip"].append(hip)

                    knee = util.get_average_xy(
                        keypoint.xy[LEFT_KNEE], keypoint.xy[RIGHT_KNEE]
                    )
                    coords["knee"].append(knee)

                    ankle = util.get_average_xy(
                        keypoint.xy[RIGHT_ANKLE], keypoint.xy[RIGHT_ANKLE]
                    )
                    coords["ankle"].append(ankle)

                    angles["hip"].append(util.calculate_angle(shoulder, hip, knee))
                    angles["shoulder"].append(
                        util.calculate_angle(hip, shoulder, elbow)
                    )
                    angles["knee"].append(util.calculate_angle(hip, knee, ankle))
                    angles["arm"].append(util.calculate_angle(shoulder, elbow, wrist))

                warning_frames = []
                if movement == "squat":
                    warning_frames = util.check_squat(coords, angles)
                if movement == "bench":
                    warning_frames = util.check_bench(angles)
                if movement == "deadlift":
                    warning_frames = util.check_deadlift(angles)

                return Response(
                    status=status.HTTP_200_OK, data={"warning_frames": warning_frames}
                )
    return Response(
        {"message": "No keypoints found"}, status=status.HTTP_400_BAD_REQUEST
    )
