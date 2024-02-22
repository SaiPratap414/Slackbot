import os
import io
import json
import mimetypes
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import load_dotenv
from flask import Flask, request
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


# Load environment variables from .env file
load_dotenv()

# Load service account credentials from client_secrets.json
with open("client_secrets.json", "r") as file:
    service_account_info = json.load(file)

# Initialize Google Drive authentication
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

# Set Slack and other environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
universal_folder_id = "1IbYhtCCdU_b094tksnL5Dr3VqGusxyCw"

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

def upload_to_drive(file_content, file_name, folder_id):
    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}], 'mimeType': mime_type})
    file_drive.content = io.BytesIO(file_content)
    file_drive.Upload()

    file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})

    drive_link = f"https://drive.google.com/file/d/{file_drive['id']}/view"
    return f"File uploaded successfully. Google Drive link: {drive_link}"


@app.event("app_mention")
def handle_mentions(body, say):
    try:
        text = body["event"]["text"]
        user_id = body["event"]["user"]
        
        # Check if the user uploaded a file
        if "files" in body["event"]:
            file_url = body["event"]["files"][0]["url_private_download"]
            file_name = body["event"]["files"][0]["name"]
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

            # Download the file
            response = requests.get(file_url, headers=headers)
            if response.status_code == 200:
                file_content = response.content

                # Upload to Google Drive
                result = upload_to_drive(file_content, file_name, universal_folder_id)

                # Respond in the channel
                say(result)
            else:
                say("Error downloading the file from Slack.")


        else:
            if "project description" in text.lower():
                say("Sure, I'll get right on that!")
                project_description = generate_project_description(text)
                say(project_description)
            elif "draft email" in text.lower():
                say("Sure, I'll get right on that!")
                response = draft_email(text)
                say(response)
            elif "anime waifu" in text.lower():
                say("Sure, I'll get right on that!")
                waifu_image_url = get_anime_waifu_image()
                say(waifu_image_url)
            else:
                say("Sorry, I couldn't understand that. How can I assist you?")
    except Exception as e:
        print(f"Error handling mention: {e}")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    if "challenge" in request.json:
        return request.json["challenge"]
    else:
        return handler.handle(request)
    
@flask_app.route('/')
def home():
    return 'Welcome to my Flask Slack App!'

# Run the Flask app
if __name__ == "__main__":
    flask_app.run(debug=True)
