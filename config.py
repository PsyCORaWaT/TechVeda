#
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime




ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'docx', 'txt'}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USERS_PATH = os.path.join(BASE_DIR, "users.json")
SECRET_KEY = os.urandom(24)
def load_users():
    """Return the entire { emails: {...}, usernames: [...] } dict."""
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def save_users(data):
    """Overwrite users.json with the given dict."""
    with open(USERS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def email_exists(email):
    return email in load_users()["emails"]

def username_exists(username):
    return username in load_users()["usernames"]

def get_user(email):
    return load_users()["emails"].get(email)

def update_user_profile(email, *,
                        username=None,
                        bio=None,
                        social_link=None,
                        password=None):
    """
    Update the given fields on user[email], sync usernames list if username changed,
    then save and return the updated user dict.
    """
    data = load_users()
    user = data["emails"][email]

    # 1) Handle username change
    if username and username != user["username"]:
        data["usernames"].remove(user["username"])
        data["usernames"].append(username)
        user["username"] = username

    # 2) Other fields
    if bio       is not None: user["bio"]         = bio
    if social_link is not None: user["social_link"] = social_link
    if password  is not None: user["password"]    = password

    data["emails"][email] = user
    save_users(data)
    return user


METADATA_PATH = os.path.join(BASE_DIR, "metadata.json")

# def load_metadata():
#     with open(METADATA_PATH, "r") as f:
#         return json.load(f)

def load_metadata():
    with open(METADATA_PATH, "r") as f:
        data = json.load(f)

    # Normalize keys, timestamps, and ensure subject exists
    for entry in data:
        # 1️⃣ unify filename
        if "name" in entry and "filename" not in entry:
            entry["filename"] = entry.pop("name")

        # 2️⃣ unify drive file id
        if "drive_id" in entry and "drive_file_id" not in entry:
            entry["drive_file_id"] = entry.pop("drive_id")

        # 3️⃣ unify upload_time
        #    - if it's ISO (has 'T'), parse with fromisoformat
        raw = entry.get("upload_time") or entry.get("timestamp")
        if raw:
            if "T" in raw:
                # parse ISO, drop microseconds, reformat
                dt = datetime.fromisoformat(raw)
                entry["upload_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # assume it's already in correct "YYYY-MM-DD HH:MM:SS"
                entry["upload_time"] = raw

        # 4️⃣ ensure subject key always present
        entry.setdefault("subject", "Uncategorized")

    return data

def save_metadata(data):
    with open(METADATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


# Defining Allowed subjects  for adding file
# Allowed Subjects (ONLY these will be used to create folders)
SUBJECTS = [
    "Math",
    "History",
    "Hindi",
    "Physics",
    "Computer Science"
]
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USER_FILES = os.path.join(BASE_DIR, "users.json")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")

ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'docx', 'txt'}

# Google Drive setup
SCOPE = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
drive_service = build('drive', 'v3', credentials=credentials)


# Functionality For Adding Files in dedicated Folder (get-or-create-folder helper)
def get_or_create_folder(folder_name, parent_id=None):
    """
    Returns a Drive folder ID for `folder_name` (creates it if missing).
    """
    # Build search query for a folder with this name (and optional parent)
    q = (
        "mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name}'"
    )
    if parent_id:
        q += f" and '{parent_id}' in parents"

    # 1) Try to find an existing folder
    res = drive_service.files().list(
        q=q,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1
    ).execute()
    items = res.get('files', [])
    if items:
        return items[0]['id']

    # 2) Create it if not found
    body = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        body['parents'] = [parent_id]
    folder = drive_service.files().create(body=body, fields='id').execute()
    return folder['id']
