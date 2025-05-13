import os
from app import app, db
from app.models import User

def check_user_photos():
    upload_folder = os.path.abspath('uploads')
    users = User.query.all()
    missing_photos = []
    for user in users:
        if user.photo:
            photo_path = os.path.join(upload_folder, user.photo)
            if not os.path.isfile(photo_path):
                missing_photos.append((user.id, user.username, user.photo))
    if missing_photos:
        print("Users with missing photo files:")
        for user_id, username, photo in missing_photos:
            print(f"User ID: {user_id}, Username: {username}, Photo: {photo}")
    else:
        print("All user photos are present in the uploads directory.")

if __name__ == "__main__":
    with app.app_context():
        check_user_photos()
