import base64
import hashlib
from time import sleep

import httpx
import dotenv
import os

dotenv.load_dotenv()

API_KEY = os.environ["API_KEY"]

# Open the image to upload - change this in order to upload your image
IMAGE_PATH = "./static/uploaded-img/uploaded.png"
# Change this accordingly
CONTENT_TYPE = "image/jpeg"
OUTPUT_CONTENT_TYPE = "image/jpeg"

_TIMEOUT = 60
_BASE_URL = os.environ["BASE_URL"]


def _get_image_md5_content() -> tuple[str, bytes]:
    with open(IMAGE_PATH, "rb") as fp:
        content = fp.read()
        image_md5 = base64.b64encode(hashlib.md5(content).digest()).decode(
            "utf-8")
    return image_md5, content


async def process_image() -> None:
    image_md5, content = _get_image_md5_content()
    # Setup an HTTP client with the correct options
    with httpx.Client(
            base_url=_BASE_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
    ) as client:
        # Submit the task
        response = client.post(
            "/tasks",
            json={
                "tools": [
                          {"type": "face_enhance",
                           "mode": "beautify"},
                          {"type": "background_enhance",
                           "mode": "base"}
                          ],
                "image_md5": image_md5,
                "image_content_type": CONTENT_TYPE,
                "output_content_type": OUTPUT_CONTENT_TYPE}
        )
        assert response.status_code == 200
        body = response.json()
        task_id = body["task_id"]

        # Upload the image
        response = httpx.put(
            body["upload_url"], headers=body["upload_headers"],
            content=content, timeout=_TIMEOUT
        )
        assert response.status_code == 200

        # Process the image
        response = client.post(f"/tasks/{task_id}/process")
        assert response.status_code == 202

        # Get the image
        for i in range(50):
            response = client.get(f"/tasks/{task_id}")
            assert response.status_code == 200

            if response.json()["status"] == "completed":
                break
            else:
                sleep(2)

        # Print the output URL to download the enhanced image
        print(response.json()["result"]["output_url"])
        return response.json()["result"]["output_url"]


if __name__ == '__main__':
    process_image()