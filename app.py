from flask import Flask, render_template, redirect, request, url_for, jsonify, session, flash
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
from functools import wraps
from config import load_users, save_users, email_exists, get_user, update_user_profile,USERS_PATH, SECRET_KEY, username_exists , load_metadata, save_metadata, allowed_file, get_or_create_folder,SUBJECTS



# App Setup
app = Flask(__name__)

# setting max size for a file
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB limit

# Secret Key for Session Management
app.secret_key = SECRET_KEY   # Use a random secret key for production

#Parent Folder I'd
TECHVEDA_PARENT_FOLDER = "1LSl9LmLybfQuVuDpwsgdpfdRxa_Ftn4x"


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
        metadata.sort(key=lambda x: x["filename"].lower())
    elif sort_by == 'uploader':
        metadata.sort(key=lambda x: x["uploaded_by"].lower())
    elif sort_by == 'upload_time': 
        metadata.sort(
        key=lambda x: datetime.strptime(x["upload_time"], "%Y-%m-%d %H:%M:%S"),
        reverse=True
    )
    
    return render_template('index.html', files = metadata)


    # metadata.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    # return render_template("index.html", files=metadata)

# Routes for Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

            #vALIDATION cHECK ethi krni
        if not username or not email or not password:
            flash(f"Sara bhar - All fields are required!", "danger")
            return redirect(url_for('register'))
        # Duplicate iss Check krne
        data = load_users()
        if email_exists(email):
            flash(f"Baar Baar?? - Email already registered!", "danger")
            return redirect(url_for('register'))
        if username_exists(username):
            flash(f"Kuch to Naya Soch - Username already taken!", "danger")
            return redirect(url_for('register'))

        # Pasword Hashing for extraaaaaa protection
        hashed = generate_password_hash(password)
        data["emails"][email] = {
            "username": username,
            "password": hashed,
            "bio": "",
            "social_link": ""
        }
        data["usernames"].append(username)
        save_users(data)

        flash(f"Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template('register.html')

# Routes for Login and Logout
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        data = load_users()
        email = next((em for em, u in data["emails"].items() if u["username"] == username), None)

        if email:
            user = data["emails"][email]
            if check_password_hash(user["password"], password):
                session["email"]    = email
                session["username"] = user["username"]
                flash(f"Malik Aap Aagye - Login successful!", "success")
                return redirect(url_for('dashboard'))
        
        flash(f"Kuch To Gadbadh hai! - Invalid username or password!", "danger")
        return redirect(url_for("login"))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


from flask import render_template, request, redirect, url_for, flash, session

@app.route("/profile")
@login_required
def profile():
    user = get_user(session["email"])
    return render_template("edit_profile.html", user=user)





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

        # Load user profile info
        user = get_user(email) or {}

        

        #   # full user profile

        return render_template(
            "dashboard.html",
            name=name,
            email=email,
            files=user_files,
            user=user,  # ← SEND this to HTML
            subjects = SUBJECTS
        )


# Edit_profile
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    email = session['email']
    user = get_user(email)


    if not user:
        flash(f"Nhi Mila - User not found!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        new_username  = request.form["username"].strip()
        new_bio       = request.form.get("bio", "").strip()
        new_social    = request.form.get("social_link", "").strip()

         # 1) Username uniqueness check
        if new_username != user["username"] and username_exists(new_username):
            flash("Username already taken!", "danger")
            return redirect(url_for("edit_profile"))

        # 2) Update JSON store & get back updated user dict
        updated = update_user_profile(
            email,
            username=new_username,
            bio=new_bio,
            social_link=new_social
        )

        # 3) Sync session username
        session["username"] = updated["username"]

        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_profile.html", user=user)






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
@app.route('/upload', methods=["POST","GET"])
@login_required
def upload():
    uploaded_file = request.files.get('file')
    subject       = request.form.get('subject', '').strip()
    uploader      = session['username']
    print("Subject:", subject)
    print("Uploaded File:", uploaded_file.filename if uploaded_file else "No file")

    if not uploaded_file or uploaded_file.filename == '':
        flash('No file selected!', 'warning')
        return redirect(url_for('dashboard'))

    if not allowed_file(uploaded_file.filename):
        flash('File type not allowed!', 'danger')
        return redirect(url_for('dashboard'))
    try:
        from config import get_or_create_folder

        # STEP: Get Folder ID or Create Folder
        folder_id = get_or_create_folder(subject, parent_id=TECHVEDA_PARENT_FOLDER)

        print("Folder ID:", folder_id)

        # STEP: Upload File to Drive
        media = MediaIoBaseUpload(uploaded_file.stream, mimetype=uploaded_file.mimetype)
        file_metadata = {
            'name': uploaded_file.filename,
            'parents': [folder_id]
        }

        drive_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        # 🔓 Grant “anyone with link” read permission:
        drive_service.permissions().create(
        fileId=drive_file["id"],
        body={"type": "anyone", "role": "reader"},fields="id").execute()

        print("Drive File Created:", drive_file)

        # STEP: Save Metadata
        metadata = load_metadata()
        metadata.append({
            "filename": uploaded_file.filename,      # unified key
            "uploaded_by": uploader,
            "email": session["email"],
            "file_type": uploaded_file.filename.rsplit('.',1)[1].lower(),
            "subject": subject,
            "upload_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "drive_file_id": drive_file["id"],       # unified key
            "web_link": drive_file["webViewLink"]
        })
        save_metadata(metadata)

        print("✅ Metadata written successfully")
        flash("Upload successful!", "success")
    except Exception as e:
        print("🔥 ERROR during upload:", e)
        flash("Something went wrong during upload.", "danger")

    return redirect(url_for("dashboard"))


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
    flash (f"Itni Badi! 20MB se chota la - File too large! Max allowed 20MB","danger")
    return redirect(url_for('dashboard'))

# Run App
if __name__ == "__main__":
    app.run(debug=True)
