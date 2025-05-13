<template>
  <div class="profile-container">
    <h1>Create Profile</h1>
    <form @submit.prevent="handleCreateProfile" enctype="multipart/form-data" class="profile-form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="profile.name" required />
      </div>

      <div class="form-group">
        <label for="parish">Parish:</label>
        <input type="text" id="parish" v-model="profile.parish" required />
      </div>

      <div class="form-group">
        <label for="biography">Biography:</label>
        <textarea id="biography" v-model="profile.biography" required></textarea>
      </div>

      <div class="form-group">
        <label for="sex">Sex:</label>
        <select id="sex" v-model="profile.sex" required>
          <option value="">Select Sex</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="form-group">
        <label for="race">Race:</label>
        <input type="text" id="race" v-model="profile.race" required />
      </div>

      <div class="form-group">
        <label for="birthYear">Birth Year:</label>
        <input type="number" id="birthYear" v-model="profile.birthYear" required />
      </div>

      <div class="form-group">
        <label for="height">Height (feet'inches"):</label>
        <input
          type="text"
          id="height"
          v-model="heightInput"
          @input="formatHeightInput"
          placeholder="e.g. 5'7&quot;"
          required
        />
      </div>

      <div class="form-group">
        <label for="favCuisine">Favorite Cuisine:</label>
        <input type="text" id="favCuisine" v-model="profile.favCuisine" required />
      </div>

      <div class="form-group">
        <label for="favColour">Favorite Colour:</label>
        <input type="text" id="favColour" v-model="profile.favColour" required />
      </div>

      <div class="form-group">
        <label for="favSchoolSubject">Favorite School Subject:</label>
        <input type="text" id="favSchoolSubject" v-model="profile.favSchoolSubject" required />
      </div>

      <div class="form-group checkbox-group">
        <label><input type="checkbox" v-model="profile.political" /> Political</label>
        <label><input type="checkbox" v-model="profile.religious" /> Religious</label>
        <label><input type="checkbox" v-model="profile.familyOriented" /> Family Oriented</label>
      </div>

      <div class="form-group">
        <label for="photo">Profile Photo:</label>
        <input type="file" id="photo" @change="handlePhotoUpload" accept="image/png, image/jpeg" />
        <small>Please upload a JPG or PNG image for your profile picture.</small>
      </div>

      <button type="submit" class="btn">Create Profile</button>

      <div v-if="message" class="success-message">{{ message }}</div>
      <div v-if="errors.length" class="error-messages">
        <ul>
          <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
        </ul>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const router = useRouter();
const token = authStore.token;

const profile = ref({
  name: '',
  parish: '',
  biography: '',
  sex: '',
  race: '',
  birthYear: '',
  height: '',
  favCuisine: '',
  favColour: '',
  favSchoolSubject: '',
  political: false,
  religious: false,
  familyOriented: false,
});
const photo = ref(null);
const message = ref('');
const errors = ref([]);

// Separate input model for height with formatting
const heightInput = ref('');

// Watch heightInput and update profile.height as total inches number
watch(heightInput, (val) => {
  const match = val.match(/^(\d+)'(\d+)"?$/);
  if (match) {
    const feet = parseInt(match[1], 10);
    const inches = parseInt(match[2], 10);
    profile.value.height = feet * 12 + inches;
  } else {
    profile.value.height = '';
  }
});

function formatHeightInput(event) {
  let val = event.target.value;

  // Remove invalid characters except digits, single quote, double quote
  val = val.replace(/[^0-9'"]/g, '');

  // Auto-insert single quote after first digit(s) if missing
  if (/^\d{1,2}$/.test(val)) {
    val = val + "'";
  }

  // Auto-insert double quote if pattern matches feet and inches without it
  if (/^\d{1,2}'\d{1,2}$/.test(val)) {
    val = val + '"';
  }

  heightInput.value = val;
}

function handlePhotoUpload(event) {
  photo.value = event.target.files[0];
}

async function handleCreateProfile() {
  errors.value = [];
  message.value = '';

  const formData = new FormData();
  formData.append('name', profile.value.name);
  formData.append('parish', profile.value.parish);
  formData.append('biography', profile.value.biography);
  formData.append('sex', profile.value.sex);
  formData.append('race', profile.value.race);
  formData.append('birth_year', profile.value.birthYear);
  formData.append('height', profile.value.height);
  formData.append('fav_cuisine', profile.value.favCuisine);
  formData.append('fav_colour', profile.value.favColour);
  formData.append('fav_school_subject', profile.value.favSchoolSubject);
  formData.append('political', profile.value.political);
  formData.append('religious', profile.value.religious);
  formData.append('family_oriented', profile.value.familyOriented);
  if (photo.value) {
    formData.append('photo', photo.value);
  }

  try {
    const response = await fetch('/api/profiles', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      if (data.errors) {
        errors.value = Object.values(data.errors).flat();
      } else if (data.message) {
        errors.value = [data.message];
      } else {
        errors.value = ['Failed to create profile.'];
      }
    } else {
      message.value = 'Profile created successfully!';
      errors.value = [];
      router.push('/profile');
    }
  } catch (error) {
    errors.value = ['An error occurred while creating the profile.'];
    console.error(error);
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 700px;
  margin: 50px auto;
  padding: 20px;
  background-color: #fff9f9;
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(255, 105, 97, 0.2);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

h1 {
  color: #ff6f61;
  margin-bottom: 20px;
  text-align: center;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
}

input[type="text"],
input[type="number"],
select,
textarea {
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ccc;
  font-size: 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

button.btn {
  background: linear-gradient(135deg, #ffb347 0%, #ff69b4 100%);
  color: white;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: background 0.3s ease;
  align-self: center;
  width: 150px;
}

button.btn:hover {
  background: linear-gradient(135deg, #ffcc70 0%, #ff85c1 100%);
}

.success-message {
  color: #ff6f61;
  margin-top: 10px;
  text-align: center;
}

.error-messages {
  color: #dc3545;
  margin-top: 10px;
  text-align: center;
}
</style>
