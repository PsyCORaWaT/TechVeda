from flask import Flask, render_template, redirect, request, url_for, jsonify, session
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)   
# Always resolve file paths *relative to where this script is saved*
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILES = os.path.join(BASE_DIR, "users.json")

# ------------------Meta-Data Helper function-----------------
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")

def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE, "r") as file:
        return json.load(file)

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as file:
        json.dump(metadata, file, indent=4)

# -----Setup for Google Drive Access (Load credentials and set up the Google Drive service)----
SCOPE = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')  # Fix path to credentials.json

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)

drive_service = build('drive', 'v3', credentials=credentials)

app.secret_key = "super-secret-key (ye bahut jada sceret hai <001199228833$$&&%%^^>)"  # You can use any long random string

# --------------------------------------Handling user data----------------------------- 
# Load users from file   
def load_users():
    if not os.path.exists(USER_FILES):   
        return[] 
    with open(USER_FILES, "r") as file:  #"r" = read mode
        return json.load(file)

#save users to file 
def save_users(users):
    with open(USER_FILES,"w") as file:   # "w" = write mode
        json.dump(users, file, indent=4)   # json.dump = Writes data to the file as JSON

# -----MAIN ROUTE -------
@app.route('/')
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    metadata= load_metadata()
    return render_template("index.html", files=metadata)

#--------------------------------route for Register Page  and handling data in Register ----------------------------
@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            return "All fields are required!",400
        
        users = load_users()

        for user in users:
            if user["username"] == username:
                return "Kuch aur soch na yaar, yeh username already occupied hai!(Username already existed)"
            if user["email"] == email:
                return "E-mail already registered!"
        
        users.append({
            "username": username,
            "email": email,
            "password": password
        })

        save_users(users)
        return redirect(url_for("login"))

    return render_template('register.html')

#----------------------------------route for Login Page--------------------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        
        users = load_users()

        for user in users:
            if user["username"] == username and user["password"] == password:
                session["username"] = user["username"]
                session["email"] = user["email"]
                return redirect(url_for('dashboard'))
        return "Ek minute...! Tu kon hai bey?  (Invalid Username or Password!)", 401

    return render_template('login.html')

# loguot session
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --------------------------------------------Route For dashboard-----------------------
@app.route('/dashboard', methods=["POST", "GET"])
def dashboard():
    if "username" in session:
        name = session["username"]
        email = session["email"]
        return render_template("dashboard.html", name=name, email=email)

#-------------------Route For Upload----------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Upload to Google Drive
            file_id = upload_to_drive(filepath, filename)

            # Save file metadata
            metadata = load_metadata()
            metadata.append({
                "filename": filename,
                "uploaded_by": session.get("username"),
                "email": session.get("email"),
                "file_type": filename.rsplit('.', 1)[1].lower(),
                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "drive_file_id": file_id
            })
            save_metadata(metadata)

            # Delete local copy
            os.remove(filepath)

            return f"✅ Upload successful! File ID on Drive: {file_id}"
        else:
            return "❌ Invalid file type!"
    return render_template('upload.html')

#Uplaod-to-Drive Function
def upload_to_drive(filepath, filename):
    file_metadata = {
        'name': filename,
        'parents': ['154kFHYM0HwC2X_R7jV6DV74q_4dIVZzx']  # Folder ID (not URL)
    }
    media = MediaFileUpload(filepath)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Grant 'anyone' permission to view/download
    drive_service.permissions().create(
        fileId=uploaded_file['id'],
        body={
            'type': 'anyone',
            'role': 'reader'
        },
        fields='id'
    ).execute()
    return uploaded_file.get('id')

#Set upload folder and allowed file extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')  # "os.path.abspath(__file__)" gives full path of the current script (app.py).
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSION = {'pdf', 'ppt', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION





#-----------Display Function---------------
@app.route('/files')
def list_files():
    if "username" not in session:
        return redirect(url_for("login"))

    metadata = load_metadata()
    return render_template("files.html", files=metadata)










if __name__ == "__main__":
    app.run(debug=True)
