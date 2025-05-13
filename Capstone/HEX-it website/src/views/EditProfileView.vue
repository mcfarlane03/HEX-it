<template>
  <div class="profile-container" v-if="profile">
    <h1>Edit Profile</h1>
    <form @submit.prevent="submitForm" class="profile-form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input id="name" v-model="profile.name" type="text" />
      </div>
      <div class="form-group">
        <label for="parish">Parish:</label>
        <input id="parish" v-model="profile.parish" type="text" />
      </div>
      <div class="form-group">
        <label for="biography">Biography:</label>
        <textarea id="biography" v-model="profile.biography"></textarea>
      </div>
      <!-- Add other fields as needed -->
      <div class="form-group">
        <label for="photo">Profile Photo:</label>
        <input id="photo" type="file" @change="handleFileChange" />
      </div>
      <button type="submit" class="btn">Save Changes</button>
      <button type="button" @click="goBack" class="btn cancel-btn">Cancel</button>
    </form>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
  <div v-else>
    <p>Loading profile...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const profile = ref(null);
const error = ref('');
const selectedFile = ref(null);

async function fetchProfile() {
  const token = authStore.token;
  const profileId = route.params.id || null;

  try {
    // If profileId is provided, fetch that profile, else fetch current user's profile
    const url = profileId ? `/api/profiles/${profileId}` : `/api/profiles/user/${authStore.user.id}`;
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!response.ok) {
      throw new Error('Failed to load profile');
    }
    const data = await response.json();
    // If fetching current user's profiles, take the first one
    profile.value = Array.isArray(data) ? data[0] : data;
  } catch (err) {
    error.value = err.message;
  }
}

function handleFileChange(event) {
  selectedFile.value = event.target.files[0];
}

async function submitForm() {
  const token = authStore.token;
  const formData = new FormData();

  for (const key in profile.value) {
    if (profile.value.hasOwnProperty(key) && key !== 'id' && key !== 'user_id_fk') {
      formData.append(key, profile.value[key] || '');
    }
  }
  if (selectedFile.value) {
    formData.append('photo', selectedFile.value);
  }

  try {
    const response = await fetch(`/api/profiles/${profile.value.id}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update profile');
    }
    alert('Profile updated successfully!');
    router.push('/profile');
  } catch (err) {
    error.value = err.message;
  }
}

function goBack() {
  router.back();
}

onMounted(() => {
  fetchProfile();
});
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
  text-align: center;
  color: #333;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  text-align: left;
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

button.cancel-btn {
  background-color: #f4a261;
}

button.cancel-btn:hover {
  background-color: #d18e3a;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
  text-align: center;
}
</style>
