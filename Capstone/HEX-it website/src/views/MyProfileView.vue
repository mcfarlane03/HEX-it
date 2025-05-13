<template>
  <div class="profile-container">
    <h1>Welcome, {{ user ? user.name : '' }}</h1>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="!user" class="loading">Loading...</div>

    <div v-if="user" class="user-details">
      <img :src="user.photo ? `${backendBaseUrl}/api/photo/${user.photo}` : '/default-profile.png'" 
           alt="Profile Photo" class="user-photo" />
      <h2>{{ user.name }}</h2>
      <p><strong>Username:</strong> {{ user.username }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Joined:</strong> {{ formatDate(user.date_joined) }}</p>

      <button @click="editUserProfile(user.id)" class="btn">Edit Profile</button>
      <button @click="createProfile" class="btn">Add Profile</button>
      <p v-if="warning" class="warning-message">{{ warning }}</p>
    </div>

    <h2>My Profiles</h2>
    <div v-if="profiles.length" class="profiles-grid">
      <div v-for="profile in profiles" :key="profile.id" class="profile-card">
        <img :src="profile.photo ? `${backendBaseUrl}/api/photo/${profile.photo}` : '/default-profile.png'" 
             alt="Profile Photo" class="profile-photo" />
        <h3>{{ profile.name }}</h3>
        <p><strong>Parish:</strong> {{ profile.parish }}</p>
        <p><strong>Biography:</strong> {{ profile.biography }}</p>
        <div class="button-group">
          <button @click="viewProfile(profile.id)" class="action-button">Show Details</button>
          <button @click="editProfile(profile.id)" class="action-button">Edit</button>
          <!-- <button @click="findMatches(profile.id)" class="action-button">Match</button> -->
          <button 
            @click="deleteProfile(profile.id)" 
            class="delete-button"
            :disabled="deleting"
          >
            {{ deleting ? '⌛' : '🗑️' }}
          </button>
        </div>
      </div>
    </div>
    <p v-else>No profiles found.</p>

    <h2>My Favorites</h2>
    <div v-if="favorites.length" class="favorites-container">
      <div v-for="fav in favorites" :key="fav.id" class="fav-card">
        <!-- <img :src="fav.photo ? `${backendBaseUrl}/api/photo/${fav.photo}` : '/default-profile.png'" 
             alt="Favorite User Photo" class="profile-photo" /> -->
             <img :src="fav.photo ? `${backendBaseUrl}/api/photo/${fav.photo}` : '/default-profile.png'" 
             alt="Favorite User Photo" class="profile-photo" />
        <h3>{{ fav.name }}</h3>
        <p><strong>Username:</strong> {{ fav.username }}</p>
        <p><strong>Email:</strong> {{ fav.email }}</p>
      </div>
    </div>
    <p v-else>No favorite users yet.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from '../stores/auth';

const backendBaseUrl = import.meta.env.VITE_BACKEND_URL;
const authStore = useAuthStore();
const token = authStore.token;
const router = useRouter();

const user = ref(null);
const profiles = ref([]);
const favorites = ref([]);
const error = ref("");
const warning = ref("");

async function fetchData(url, errorMessage) {
  try {
    const res = await fetch(`${backendBaseUrl}${url}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include'
    });
    if (!res.ok) throw new Error(errorMessage);
    return await res.json();
  } catch (err) {
    error.value = err.message;
  }
}

async function loadData() {
  const userId = authStore.user?.id ?? null;
  if (!userId || userId === "null") {
    error.value = "User ID is missing. Please log in again.";
    return;
  }

  user.value = await fetchData(`/api/users/${userId}`, "Failed to load user details.");
  profiles.value = await fetchData(`/api/profiles/user/${userId}`, "Failed to load profiles.");
  favorites.value = await fetchData(`/api/users/${userId}/favourites`, "Failed to load favorite users.");
}

onMounted(loadData);

function viewProfile(profileId) {
  if (!profileId || profileId === "null") {
    error.value = "Invalid profile ID.";
    return;
  }
  router.push(`/profiles/${profileId}`);
}

function editProfile(profileId) {
  if (!profileId) {
    error.value = "Invalid profile ID.";
    return;
  }
  router.push(`/edit-profile/${profileId}`);
}

function createProfile() {
  if (profiles.value.length >= 3) {
    warning.value = "You can only create up to 3 profiles.";
    return;
  }
  router.push('/create');
}

function editUserProfile(userId) {
  if (!userId) {
    error.value = "Invalid user ID.";
    return;
  }
  router.push(`/edit-user-profile/${userId}`);
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}


async function deleteProfile(profileId) {
  if (!profileId) {
    error.value = "Invalid profile ID.";
    return;
  }

  if (!confirm("Are you sure you want to delete this profile? This action cannot be undone.")) {
    return;
  }

  try {
    error.value = ""; // Clear previous errors
    warning.value = "";
    
    const response = await fetch(`${backendBaseUrl}/api/profiles/${profileId}`, {
      method: "DELETE",
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to delete profile');
    }

    // Success - update UI
    profiles.value = profiles.value.filter(profile => profile.id !== profileId);
    warning.value = "Profile deleted successfully";
    
    // Clear success message after 3 seconds
    setTimeout(() => warning.value = "", 3000);
    
  } catch (err) {
    error.value = err.message;
    console.error("Delete profile error:", err);
  }


  const deleting = ref(false);

async function deleteProfile(profileId) {
  if (deleting.value) return;
  
  // ... existing checks ...
  
  try {
    deleting.value = true;
    // ... existing delete logic ...
  } catch (err) {
    // ... existing error handling ...
  } finally {
    deleting.value = false;
  }
}
}
</script>

<style scoped>
.profile-container {
  max-width: 700px;
  margin: 50px auto;
  padding: 20px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
  text-align: center;
}

h1 {
  color: #333;
}

.user-photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
  border: 3px solid #333;
}

.profiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.profile-card {
  padding: 15px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.profile-photo {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
}

.warning-message {
  color: #dc3545;
}
</style>
