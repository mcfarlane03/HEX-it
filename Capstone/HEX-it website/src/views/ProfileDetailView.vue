<template>
  <div class="profile-detail-container" v-if="profile">
    <h1>{{ profile.name }}</h1>
    <img :src="profile.photo" alt="Profile Photo" class="profile-photo" v-if="profile.photo" />
    <p><strong>Parish:</strong> {{ profile.parish }}</p>
    <p><strong>Biography:</strong> {{ profile.biography }}</p>
    <p><strong>Sex:</strong> {{ profile.sex }}</p>
    <p><strong>Race:</strong> {{ profile.race }}</p>
    <p><strong>Birth Year:</strong> {{ profile.birth_year }}</p>
    <p><strong>Height:</strong> {{ profile.height }}</p>
    <p><strong>Favorite Cuisine:</strong> {{ profile.fav_cuisine }}</p>
    <p><strong>Favorite Colour:</strong> {{ profile.fav_colour }}</p>
    <p><strong>Favorite School Subject:</strong> {{ profile.fav_school_subject }}</p>
    <p><strong>Political:</strong> {{ profile.political ? 'Yes' : 'No' }}</p>
    <p><strong>Religious:</strong> {{ profile.religious ? 'Yes' : 'No' }}</p>
    <p><strong>Family Oriented:</strong> {{ profile.family_oriented ? 'Yes' : 'No' }}</p>
    <div v-if="error" class="error-message">{{ error }}</div>
  <div class="actions">
    <button @click="goBack">Back</button>
    <button @click="emailProfile">Email Profile</button>
    <button v-if="profile.user_id_fk !== authStore.user?.id" class="heart" :class="{ favorited: isFavorited }" @click="toggleFavorite">
      ♥
    </button>
    <button v-if="profile.user_id_fk === authStore.user?.id" @click="goToMatchReport">
      Match Me
    </button>
  </div>
  </div>
  <div v-else>
    <p>Loading profile...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const profile = ref(null);
const error = ref('');
const isFavorited = ref(false);

const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001';

async function fetchProfile() {
  const token = authStore.token;
  const profileId = route.params.id;

  try {
    const response = await fetch(`${backendBaseUrl}/api/profiles/${profileId}`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include'
    });
    if (!response.ok) {
      throw new Error('Failed to load profile');
    }
    profile.value = await response.json();
    await checkIfFavorited();
  } catch (err) {
    error.value = err.message;
  }
}

async function checkIfFavorited() {
  try {
    if (!authStore.user || !authStore.user.id) {
      isFavorited.value = false;
      return;
    }
    const response = await fetch(`${backendBaseUrl}/api/users/${authStore.user.id}/favourites`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      credentials: 'include'
    });
    if (!response.ok) {
      throw new Error('Failed to fetch favourites');
    }
    const favourites = await response.json();
    isFavorited.value = favourites.some(fav => fav.id === profile.value.user_id_fk);
  } catch (err) {
    console.error(err);
  }
}

async function toggleFavorite() {
  try {
    const csrfToken = getCookie('csrf_access_token') || getCookie('csrf_token');
    const method = isFavorited.value ? 'DELETE' : 'POST';
    const response = await fetch(`${backendBaseUrl}/api/profiles/${profile.value.user_id_fk}/favourite`, {
      method,
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'X-CSRFToken': csrfToken,
        'X-CSRF-Token': csrfToken,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });
    if (!response.ok) {
      throw new Error('Failed to favourite profile');
    }
    isFavorited.value = !isFavorited.value;
  } catch (err) {
    console.error(err);
  }
}

function emailProfile() {
  alert('Email Profile button clicked (no functionality implemented).');
}

function goBack() {
  router.back();
}

onMounted(() => {
  fetchProfile();
});

function goToMatchReport() {
  router.push({ name: 'matchReport', params: { id: profile.value.id } });
}
</script>

<style scoped>
.profile-detail-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  background: #f4f4f4;
  border-radius: 10px;
  text-align: left;
}

.profile-photo {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 20px;
}

button {
  background: #007bff;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
}

button:hover {
  background: #0056b3;
}

.heart {
  background: none;
  border: none;
  cursor: pointer;
  color: pink;
  font-size: 1.5rem;
  vertical-align: middle;
}

.heart.favorited {
  color: red;
}
</style>
