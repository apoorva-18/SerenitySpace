import eventlet
eventlet.monkey_patch()  
from flask import Flask, render_template, request, jsonify,redirect,url_for
from flask_socketio import SocketIO, emit, join_room
from flask_login import UserMixin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import os
from AI_Chatbot.main import calling_the_bot, handle_voice_input
import speech_recognition as sr
import pyttsx3
import time
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

from datetime import datetime
import logging
app = Flask(__name__)
socketio = SocketIO(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to this route if user is not logged in

app.config['SECRET_KEY'] = 'a9723d06cf11ecdb2dbadf755c90bef26f43c015dee9fe838124cfb8f26964fb'
print(app.config['SECRET_KEY'])


app.config["MONGO_URI"] = "mongodb+srv://Apoorva:apoorva21@cluster0.dk4dx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
mongo = PyMongo(app)
logging.basicConfig(level=logging.INFO)

class User(UserMixin):
    def __init__(self, user_id,username, email, password):
        self.id = user_id  # Replace with unique user ID if needed
        self.username = username
        self.email = email
        # Hash the password securely (discussed later)
        self.password_hash = generate_password_hash(password)
        
    
    def get_user(username):
        return users_collection.find_one({"username": username})

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def create_user(username, email, password):
        user = User(username, email, password)
    # Use bcrypt to hash the password
        user.password_hash = generate_password_hash(user.password_hash)
        users_collection.insert_one(user.__dict__)
    def generate_password_hash(password):
        return generate_password_hash(password)
    def verify_password(hashed_password, plain_text_password):
        return check_password_hash(hashed_password, plain_text_password)   
# Access collections
db = mongo.cx["mongodbVSCodePlaygroundDB"]  # Explicitly set the database
users_collection = db["users"]
diary_collection = db["diary_entries"]
forum_posts_collection = db["forum_posts"]
rewards_collection = db["rewards"]
group_sessions_collection = db["group_sessions"]

engine = pyttsx3.init()
engine.setProperty('rate', 175)  # Set speech rate
engine.setProperty('volume', 1.0)  # Set volume

@app.route("/")
def index():
    # Redirect to the register page as the default route
    return redirect(url_for("register"))
# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user["_id"]), user["username"], user["email"],user["password"])
    return None

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Find user in the database
        user = users_collection.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid email or password.")
        if user and check_password_hash(user["password"], password):
            user_obj = User(user_id=user["_id"], username=user["username"], email=user["email"],password=user["password"])
            login_user(user_obj)
            return redirect(url_for("home", user_id=user["_id"]))
        return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return render_template("register.html", error="Email already registered.")

        # Hash password and create user
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user = {
            "username": username,
            "email": email,
            "password": hashed_password
        }
        result = users_collection.insert_one(user)
        return redirect(url_for("login"))
    return render_template("register.html")


def check_for_reward(user_id, activity):
    
    # Fetch user data from the database
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None  # User not found

    rewards = []  # To store rewards earned during this check

    # Track activity count for daily rewards
    if activity == "journal_entry":
        daily_entries = user.get("daily_entries", 0) + 1
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"daily_entries": daily_entries}})
        if daily_entries == 5:  # Milestone: 5 entries in a day
            rewards.append({
                "title": "Daily Achiever",
                "description": "You completed 5 journal entries today! Keep it up!"
            })

    # Increment points for any activity and check milestone
    points = user.get("points", 0) + 10  # Add 10 points for this activity
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"points": points}})
    if points >= 100 and "100 Points Milestone" not in user.get("badges", []):
        rewards.append({
            "title": "100 Points Milestone",
            "description": "Congratulations on earning 100 points!"
        })
        # Add badge for this milestone
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"badges": "100 Points Milestone"}})

    # Badge for helping someone
    if activity == "helped_someone" and "Community Helper" not in user.get("badges", []):
        rewards.append({
            "title": "Community Helper",
            "description": "You earned the Community Helper badge for helping others!"
        })
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"badges": "Community Helper"}})

    # Return the first reward earned, if any
    return rewards[0] if rewards else None

    # Return the latest reward earned
    return rewards[0] if rewards else None

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    join_room(room)
    emit('message', {'msg': f"{data['username']} has joined the room."}, to=room)

@socketio.on('new_comment')
def handle_new_comment(data):
    post_id = data['post_id']
    comment = {"username": data['username'], "content": data['content']}
    # Save to the database
    forum_posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment}})
    emit('comment_added', comment, to=post_id)
    
@socketio.on('new_activity')
def handle_activity(data):
    try:
        user_id = data["user_id"]
        activity = data["activity"]
        reward = check_for_reward(user_id, activity)
        if reward:
            emit('reward_notification', reward, room=user_id)
    except Exception as e:
        logging.error(f"Error handling activity: {e}")
        
# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Protect routes with login_required
@app.route("/protected_route")
@login_required
def protected_route():
    return f"Hello, {current_user.username}! This is a protected route."

# Home Page
@app.route("/home/<user_id>")
@login_required
def home(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for("login"))
    return render_template("home.html", user=user)

# Forums
@app.route("/forums/<user_id>", methods=["GET", "POST"])
def forums(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for("landing"))
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = request.form.get("user_id")
        if title and content:
            forum_posts_collection.insert_one({
                "user_id": user_id,
                "title": title,
                "content": content,
                "created_at": datetime.utcnow(),
                "comments": []
            })
            return redirect(url_for("forums",user_id=user_id))
    posts = list(forum_posts_collection.find())
    return render_template("forums.html", posts=posts,user=user)

@app.route("/forums/<post_id>/comment", methods=["POST"])
def add_comment(post_id):
    user_id = request.form.get("user_id")
    if not user_id:
        return "User ID is required", 400
    comment = {
        "username": request.form.get("username"),
        "content": request.form.get("content"),
        "created_at": datetime.utcnow()
    }
    forum_posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment}})
    return redirect(url_for("forums",user_id=user_id))

# DELETE route for posts
@app.route('/forums/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    user_id = request.json.get("user_id")

    post = forum_posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if post["user_id"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    forum_posts_collection.delete_one({"_id": ObjectId(post_id)})
    return jsonify({"message": "Post deleted successfully"}), 204

# DELETE route for comments
@app.route('/forums/<post_id>/comment/<comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    post = forum_posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404

    comment = next((c for c in post["comments"] if str(c["_id"]) == comment_id), None)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    user_id = request.json.get("user_id")
    if comment["user_id"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    forum_posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}
    )
    return jsonify({"message": "Comment deleted successfully"}), 204

# Rewards
@app.route("/rewards/<user_id>")
def rewards(user_id):
    # Fetch the user details
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for("index"))

    rewards = {
        "points": user.get("points", 0),  # Points earned by the user
        "badges": user.get("badges", [])  # List of badges earned
    }

    # Render the rewards page with user data
    return render_template("rewards.html", user=user, rewards=rewards)

# Group Therapy
@app.route("/group_therapy/<user_id>")
def group_therapy(user_id):
    # Fetch user details
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for("landing"))

    # Fetch group sessions
    sessions = list(group_sessions_collection.find())
    for session in sessions:
        session["_id"] = str(session["_id"])  # Convert ObjectId to string

    return render_template("group_therapy.html", user=user, sessions=sessions)

@app.route("/add_group_therapy", methods=["POST"])
def add_group_therapy():
    data = request.json
    session = {
        "title": data["title"],
        "time": data["time"],
        "description": data["description"],
        "created_at": datetime.utcnow(),
    }
    group_sessions_collection.insert_one(session)
    socketio.emit("group_therapy_update", session, broadcast=True)
    return jsonify({"status": "success", "message": "Group therapy session added!"})

@app.route("/group_sessions", methods=["GET"])
def get_group_sessions():
    sessions = list(group_sessions_collection.find())
    for session in sessions:
        session["_id"] = str(session["_id"])  # Convert ObjectId to string
    return jsonify(sessions)

@app.route("/register_group_session/<session_id>", methods=["POST"])
def register_group_session(session_id):
    user_id = request.json.get("user_id")
    username = request.json.get("username")

    session = group_sessions_collection.find_one({"_id": ObjectId(session_id)})
    if not session:
        return jsonify({"message": "Session not found!"}), 404

    if len(session["registered_users"]) >= session["max_participants"]:
        return jsonify({"message": "Session is full!"}), 400

    group_sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"registered_users": {"user_id": user_id, "username": username}}}
    )
    return jsonify({"message": "Successfully registered for the session!"})

# Challenges
@app.route("/challenges/<user_id>")
def challenges(user_id):
    # Fetch user details using the user_id
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    # If user is not found, redirect to the landing page
    if not user:
        return redirect(url_for("landing"))

    challenges = [
        {"title": "5 Minutes of Mindfulness", "description": "Meditate for 5 minutes every day."},
        {"title": "Write 3 Positive Thoughts", "description": "List three things you are grateful for."}
    ]
    
    # Pass user and challenges to the template
    return render_template("challenges.html", challenges=challenges, user=user)

# Quizzes
@app.route("/quizzes/<user_id>")
def quizzes(user_id):
    # Fetch user details
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for("landing"))
    
    quizzes = [
        {"title": "Stress Quiz", "description": "Take this quiz to understand your stress levels."},
        {"title": "Happiness Quiz", "description": "Evaluate your happiness scale with this quiz."}
    ]
    
    return render_template("quizzes.html", quizzes=quizzes, user=user)

# Chatbot Interaction Route
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get("message")
        if user_input:
            # Call the chatbot function
            response = calling_the_bot(user_input)
            if response:
                return jsonify({
                    "status": "success",
                    "guidance": response["guidance"],
                    "medication": response["medication"]
                })
            else:
                return jsonify({
                    "status": "fail",
                    "message": "Sorry, I couldn't find any specific guidance for your symptoms."
                })
        return jsonify({"status": "fail", "message": "Invalid input."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
    
@app.route("/voice-chat", methods=["POST"])
def voice_chat():
    try:
        # Delegate voice input handling to `handle_voice_input` in `main.py`
        response = handle_voice_input()
        if response and response["status"] == "success":
            # Voice response
            engine.say(response["guidance"])
            if "medication" in response and response["medication"]:
                engine.say(f"Suggested medications are {', '.join(response['medication'])}.")
            engine.runAndWait()
            
            return jsonify(response)
        else:
            message = response.get("message", "No guidance available or an error occurred.")
            engine.say(message)
            engine.runAndWait()
            
            return jsonify({"status": "error", "message": message})
    except Exception as e:
        engine.say("An error occurred while processing your voice input.")
        engine.runAndWait()
        return jsonify({"status": "error", "message": str(e)})

# Add Diary Entry
@app.route("/add_diary/<user_id>", methods=["GET", "POST"])
def add_diary(user_id):
    if request.method == "POST":
        mood = request.form.get("mood")
        thoughts = request.form.get("thoughts")
        if mood and thoughts:
            entry = {
                "user_id": user_id,
                "date": datetime.utcnow(),
                "mood": mood,
                "thoughts": thoughts,
            }
            diary_collection.insert_one(entry)
            check_for_reward(user_id, "journal_entry")

            return redirect(url_for("home", user_id=user_id))
    return render_template("add_diary.html", user_id=user_id)

# Track Progress
@app.route("/track_progress/<user_id>")
def track_progress(user_id):
    entries = list(diary_collection.find({"user_id": user_id}).sort("date", -1))
    for entry in entries:
        entry["_id"] = str(entry["_id"])  # Convert ObjectId to string
    return render_template("track_progress.html", entries=entries)

# Crisis Management
@app.route("/check_crisis/<user_id>")
def check_crisis(user_id):
    # Categorized keywords
    keyword_categories = {
        "general_crisis": ["suicide", "hopeless", "depressed", "self-harm", "worthless", "no way out", "can't go on", "give up", "alone", "nobody cares"],
        "anxiety_stress": ["panic", "anxious", "overwhelmed", "suffocating", "drowning"],
        "grief_loss": ["loss", "grief", "heartbreak", "mourning"],
        "anger_frustration": ["rage", "frustration", "resentful", "enraged"],
        "substance_use": ["overdose", "alcohol abuse", "drug abuse", "addicted"]
    }

    # Initialize flagged entries and categories
    flagged_entries = []
    detected_categories = set()

    # Fetch entries for the user
    entries = diary_collection.find({"user_id": user_id})

    for entry in entries:
        entry_flagged = False
        for category, keywords in keyword_categories.items():
            if any(keyword in entry["thoughts"].lower() for keyword in keywords):
                detected_categories.add(category)
                if not entry_flagged:  # Add entry only once
                    entry["_id"] = str(entry["_id"])
                    flagged_entries.append(entry)
                    entry_flagged = True

    return render_template("crisis_management.html", flagged_entries=flagged_entries, detected_categories=detected_categories)

# AI Chatbot Page
@app.route('/ai_chatbot/<user_id>', methods=["GET", "POST"])
def ai_chatbot(user_id):
    if request.method == "POST":
        user_input = request.json.get("message")
        if user_input:
            response = calling_the_bot(user_input)
            if response:
                return jsonify({
                    "status": "success",
                    "guidance": response["guidance"],
                    "medication": response["medication"]
                })
            return jsonify({
                "status": "fail",
                "message": "Sorry, I couldn't find any specific guidance for your symptoms."
            })
        return jsonify({"status": "fail", "message": "Invalid input."})
    # Render the chatbot HTML page
    return render_template("ai_chatbot.html", user_id=user_id)

app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1-hour session timeout

@app.before_request
def make_session_permanent():
    session.permanent = True

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)

