from app import app, db
from app.models import User

def debug_user_photo_filename(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Username: {user.username}")
            print(f"Photo filename stored in DB: {user.photo}")
        else:
            print(f"User with username '{username}' not found.")

if __name__ == "__main__":
    debug_user_photo_filename("Nishaun")
