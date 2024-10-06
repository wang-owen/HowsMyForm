import os, requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dotenv import load_dotenv

load_dotenv()


@api_view(["POST"])
def chat(request):
    API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{os.environ.get('R2_ACCOUNT_ID')}/ai/run/"
    headers = {"Authorization": f"Bearer {os.environ.get('AI_API_TOKEN')}"}

    inputs = [
        {
            "role": "system",
            "content": "You are Chadbot, a friendly assistant that answers questions about weightlifting and the importance of achieving proper form when doing heavy lifts. Keep all your answers short and concise.",
        },
        *[
            {"role": "user", "content": message["content"]}
            for message in request.data["messages"]
        ],
    ]
    input = {"messages": inputs}
    response = requests.post(
        f"{API_BASE_URL}@cf/meta/llama-3-8b-instruct", headers=headers, json=input
    )
    output = response.json()

    return Response(output, status=status.HTTP_200_OK)
