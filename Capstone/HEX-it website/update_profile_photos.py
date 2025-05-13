import os
from app import app, db
from app.models import Profile

def update_profile_photos():
    with app.app_context():
        uploads_dir = os.path.join(os.getcwd(), 'app', 'uploads')
        profiles = Profile.query.all()
        for profile in profiles:
            if not profile.photo:
                # Try to find a matching photo file by profile name or assign a default
                # For simplicity, assign a default photo filename here
                profile.photo = 'default-profile.png'
                print(f"Updated profile id {profile.id} with default photo")
        db.session.commit()
        print("Profile photo update complete.")

if __name__ == "__main__":
    update_profile_photos()
