from flask import Flask, render_template, redirect, request, url_for, jsonify, session, flash
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
from functools import wraps


# App Setup
app = Flask(__name__)

# setting max size for a file
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB limit

# Secret Key for Session Management
app.secret_key = os.urandom(24)  # Use a random secret key for production

# Directories and Files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILES = os.path.join(BASE_DIR, "users.json")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'upload')

# Allowed Extensions for File Upload
ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'docx', 'txt'}

# Google Drive Setup
SCOPE = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
drive_service = build('drive', 'v3', credentials=credentials)

# Create Upload Folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper Functions
def load_users():
    if not os.path.exists(USER_FILES):
        return []
    with open(USER_FILES, "r") as file:
        users = json.load(file)
        print("Loaded User:", users)  # Delete later
        return users

def save_users(users):
    with open(USER_FILES, "w") as file:
        json.dump(users, file, indent=4)

def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE, "r") as file:
        return json.load(file)

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as file:
        json.dump(metadata, file, indent=4)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Session Protection Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("You need to log in first!", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes for Index
@app.route('/')
def index():
    metadata = load_metadata()

    query = request.args.get('q','').lower()
    file_type = request.args.get('type','')
    sort_by = request.args.get('sort_by','upload_time') #Default Sorting (Sort By Time)

    #applying Filter Functionality

    # Filter by search
    if query:
        metadata = [file for file in metadata
                     if query in file['filename'].lower()]
    
    # Filter by file type
    if file_type:
        metadata = [file for file in metadata if file["file_type"].lower() == file_type.lower()]

    # sorting
    if sort_by == 'name':
        metadata.sort(key=lambda x: x["flename"].lower())
    elif sort_by == 'uploader':
        metadata.sort(key=lambda x: x["uploaded_by"].lower())
    elif sort_by == 'upload_time':
        metadata.sort(key=lambda x: datetime.strptime(x["upload_time"], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    return render_template('index.html', files = metadata)


    # metadata.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    # return render_template("index.html", files=metadata)

# Routes for Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        users = load_users()
        if any(user["username"] == username for user in users):
            flash("Username already taken!", "danger")
            return redirect(url_for('register'))
        if any(user["email"] == email for user in users):
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        # users.append({"username": username, "email": email, "password": password})
        hashed_password = generate_password_hash(password)
        users.append({"username": username, "email": email, "password": hashed_password})

        save_users(users)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template('register.html')

# Routes for Login and Logout
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")

        users = load_users()
        # user = next((user for user in users 
        #              if user["username"] == username and user["password"] == password), None)

        user = next((user for user in users if user["username"] == username), None)
        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        
        flash("Invalid username or password!", "danger")
        return redirect(url_for("login"))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# Route for Dashboard
@app.route('/dashboard', methods=["POST", "GET"])
@login_required  # Ensure user is logged-in
def dashboard():
    if "username" in session:
        name = session["username"]
        email = session["email"]

        metadata = load_metadata()

        # Filter files uploaded by the logged-in user
        user_files = [file for file in metadata if file.get("uploaded_by") == name]
        
        print("User Files:", user_files)  # Debugging

    return render_template("dashboard.html", name=session["username"], email=email, files=user_files)
    


# Google Drive file deletion function (used later)
def delete_from_drive(file_id):
    try:
        drive_service.files().delete(fileId=file_id).execute()
    except Exception as e:
        print(f"Error deleting file from Google Drive: {e}")

# Route for deleting files
@app.route('/delete_files/<file_id>', methods=["POST","GET"])
@login_required
def delete_files(file_id):
    metadata = load_metadata()  # Load metadata from json file

    file_to_delete = next((file for file in metadata 
                           if file['drive_file_id'] == file_id), None)
    if file_to_delete:
        delete_from_drive(file_id)  # Delete file from Google Drive

        metadata = [file for file in metadata 
                    if file['drive_file_id'] != file_id]  # Remove file/data from metadata.json
        
        save_metadata(metadata)

        flash("Le bhai kr diya Delete", "Success")
        return redirect(url_for("dashboard"))
    else:
        flash("Bhai jo hai hi nhi usko kahan se Delete Karun????", "File Not Found")
        return redirect(url_for("dashboard"))

# Route for file upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            file_id = upload_to_drive(filepath, filename)

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

            os.remove(filepath)
            flash("Upload successful!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid file type!", "danger")
        return redirect(request.url)

    return redirect(url_for('dashboard'))

def upload_to_drive(filepath, filename):
    file_metadata = {'name': filename, 'parents': ['154kFHYM0HwC2X_R7jV6DV74q_4dIVZzx']}
    media = MediaFileUpload(filepath)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    drive_service.permissions().create(
        fileId=uploaded_file['id'],
        body={'type': 'anyone', 'role': 'reader'},
        fields='id'
    ).execute()

    return uploaded_file.get('id')

@app.route('/files')
@login_required
def list_files():
    metadata = load_metadata()
    return render_template("files.html", files=metadata)

# File size handling "Error Print"
@app.errorhandler(413)
def file_too_large(e):
    flash (f"Itni Badi! 20MB se chota la - File too large! Max allowed 30MB","danger")
    return redirect(url_for('dashboard'))

# Run App
if __name__ == "__main__":
    app.run(debug=True)
