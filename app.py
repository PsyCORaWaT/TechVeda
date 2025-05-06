from flask import Flask, render_template, redirect,request
import os
import json

app = Flask(__name__)   




# --------------------------------------Handling user data----------------------------- 


# Always resolve file paths *relative to where this script is saved*
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILES= os.path.join(BASE_DIR, "users.json")

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







@app.route('/')
def index():
    return render_template("index.html") 

#--------------------------------route for Register Page  and handling data in Register ----------------------------
@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            return "All fields are required!"
        
        users = load_users()

        for user in users:
            if user["username"] ==username:
                return "Kuch aur soch na yaar, yeh username already occupied hai!(Username already existed)"
            if user["email"] ==email:
                return "E-mail already registered!"
        
        users.append({
            "username": username,
            "email":email,
            "password": password
        })

        save_users(users)
        return "Register Successfully"

    return render_template('register.html') 




#----------------------------------route for Login Page--------------------------
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        
        users = load_users()

        for user in users:
            if user["username"] == username and user["password"]==password:
                # return "Malilk! Aap aa gye.... (Login Successful)"
                return render_template('dashboard.html')
        return "Ek minute...! Tu kon hai bey?  (Invalid Username or Password!)"



    return render_template('login.html')





if __name__ in "__main__":
    app.run(debug=True)
