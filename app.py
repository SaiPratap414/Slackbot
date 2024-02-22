import os
import json
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

# Import functions from functions.py
from functions import draft_email, generate_project_description, get_anime_waifu_image

# Load environment variables from .env file
load_dotenv()

# Load service account credentials from client_secrets.json
with open("client_secrets.json", "r") as file:
    service_account_info = json.load(file)

# Set service account credentials as environment variables
os.environ["GOOGLE_SERVICE_ACCOUNT_TYPE"] = service_account_info["type"]
os.environ["GOOGLE_SERVICE_ACCOUNT_PROJECT_ID"] = service_account_info["project_id"]
os.environ["GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID"] = service_account_info["private_key_id"]
os.environ["GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY"] = service_account_info["private_key"]
os.environ["GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL"] = service_account_info["client_email"]
os.environ["GOOGLE_SERVICE_ACCOUNT_CLIENT_ID"] = service_account_info["client_id"]
os.environ["GOOGLE_SERVICE_ACCOUNT_AUTH_URI"] = service_account_info["auth_uri"]
os.environ["GOOGLE_SERVICE_ACCOUNT_TOKEN_URI"] = service_account_info["token_uri"]
os.environ["GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"] = service_account_info["auth_provider_x509_cert_url"]
os.environ["GOOGLE_SERVICE_ACCOUNT_CLIENT_CERT_URL"] = service_account_info["client_x509_cert_url"]
os.environ["GOOGLE_SERVICE_ACCOUNT_UNIVERSE_DOMAIN"] = service_account_info["universe_domain"]

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]
WAIFU_PICS_API_KEY = os.environ["WAIFU_PICS_API_KEY"]  # Your Waifu.pics API key

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Set the universal Google Drive folder ID
universal_folder_id = "1IbYhtCCdU_b094tksnL5Dr3VqGusxyCw"

# Initialize the Google Drive authentication
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

def upload_to_drive(file_path, folder_id):
    try:
        # Create a GoogleDriveFile instance with the name and folder ID
        file_drive = drive.CreateFile({'title': file_path.split("/")[-1], 'parents': [{'id': folder_id}]})
        
        # Set the content of the file
        file_drive.SetContentFile(file_path)

        # Upload the file
        file_drive.Upload()

        # Get the link to the uploaded file
        link = file_drive['alternateLink']
        return f"File uploaded successfully. Link: {link}"

    except Exception as e:
        return f"Error uploading file to Google Drive: {str(e)}"

def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = WebClient(token=SLACK_BOT_TOKEN)
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")

# Print the bot user ID when the script runs
print("Bot User ID:", get_bot_user_id())

@app.event("app_mention")
def handle_mentions(body, say):
    try:
        text = body["event"]["text"]
        user_id = body["event"]["user"]
        
        # Check if the user uploaded a file
        if "files" in body["event"]:
            file_url = body["event"]["files"][0]["url_private_download"]
            file_name = body["event"]["files"][0]["name"]

            # Download the file
            response = requests.get(file_url)
            if response.status_code == 200:
                local_file_path = f"C:/Users/prata/Desktop/{file_name}"  # Adjust the file path as per your desktop location
                with open(local_file_path, "wb") as f:
                    f.write(response.content)

                # Upload to Google Drive
                result = upload_to_drive(local_file_path, universal_folder_id)

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

# Run the Flask app
if __name__ == "__main__":
    flask_app.run()
