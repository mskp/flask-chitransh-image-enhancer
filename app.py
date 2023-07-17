from flask import Flask, request, render_template, jsonify
import dotenv
import os
import util
import asyncio

from util.api_func import process_image

dotenv.load_dotenv()

app = Flask(__name__)
PHOTO_PATH = "./static/uploaded-img/"


@app.route('/', methods=['GET', 'POST'])
async def home():
    try:
        if (request.method == "POST"):
            photo = request.files.get("imageFile")
            photo.filename = "uploaded.png"
            print(os.path.join(PHOTO_PATH, photo.filename))
            photo.save(os.path.join(PHOTO_PATH, photo.filename))

            print("before request")
            processed_img_url = await process_image()
            print(processed_img_url)
            response = {
                'uploadedImage': "uploaded.png",
                'processedImage': processed_img_url
            }
            return jsonify(response), 200

        return render_template("index.html")

    except Exception as e:
        print(e)
        response = {
            "success": "false",
            "message": str(e)
        }
        return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
