from pyrebase import initialize_app

firebase_config = {
  "apiKey": "AIzaSyAJZpfII7jcZBez4MZOPEO8VBIH4DPjaA4",
  "authDomain": "timney-b068d.firebaseapp.com",
  "projectId": "timney-b068d",
  "storageBucket": "timney-b068d.appspot.com",
  "messagingSenderId": "736104565808",
  "appId": "1:736104565808:web:14ff67e73fa50b825eb1f5",
  "measurementId": "G-RZ7CDW5YWB"
}

firebase = initialize_app(config=firebase_config)
firebase_auth = firebase.auth()
firebase.database()
print(firebase_auth.current_user)