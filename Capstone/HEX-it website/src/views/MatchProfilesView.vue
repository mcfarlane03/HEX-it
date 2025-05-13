<template>
  <div class="match-report-container">
    <h1>Match Report</h1>
    <p class="report-description">
      View profiles that match your selected profile based on compatibility criteria.
    </p>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="loading" class="loading-message">Finding your matches...</div>

    <div v-if="matches.length > 0">
      <div class="sort-options">
        <label>Sort by:</label>
        <select v-model="sortBy" @change="sortMatches">
          <option value="name">Name</option>
          <option value="parish">Parish</option>
          <option value="age">Age</option>
        </select>
      </div>

      <div class="match-grid">
        <div v-for="match in matches" :key="match.profile_id" class="match-card">
          <div class="match-photo-container">
            <img 
              :src="match.photo || '/default-profile.png'" 
              alt="Profile Photo" 
              class="match-photo"
            />
            <button 
              class="favorite-btn" 
              @click="toggleFavorite(match.user_id)"
              :class="{ favorited: isFavorited(match.user_id) }"
            >
              ♥
            </button>
          </div>
          
          <div class="match-info">
            <h3>{{ match.name }}</h3>
            <p><strong>Age:</strong> {{ new Date().getFullYear() - match.birth_year }}</p>
            <p><strong>Parish:</strong> {{ match.parish }}</p>
            <p><strong>Height:</strong> {{ match.height }} inches</p>
            
            <div class="shared-traits">
              <h4>Shared Traits:</h4>
              <ul>
                <li v-if="currentProfile.fav_cuisine === match.fav_cuisine">
                  Favorite Cuisine: {{ match.fav_cuisine }}
                </li>
                <li v-if="currentProfile.fav_colour === match.fav_colour">
                  Favorite Color: {{ match.fav_colour }}
                </li>
                <li v-if="currentProfile.fav_school_subject === match.fav_school_subject">
                  Favorite Subject: {{ match.fav_school_subject }}
                </li>
                <li v-if="currentProfile.political === match.political">
                  Political: {{ match.political ? 'Yes' : 'No' }}
                </li>
                <li v-if="currentProfile.religious === match.religious">
                  Religious: {{ match.religious ? 'Yes' : 'No' }}
                </li>
                <li v-if="currentProfile.family_oriented === match.family_oriented">
                  Family Oriented: {{ match.family_oriented ? 'Yes' : 'No' }}
                </li>
              </ul>
            </div>

            <router-link 
              :to="`/profiles/${match.profile_id}`" 
              class="view-profile-btn"
            >
              View Full Profile
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="no-matches">
      <p>No matches found based on your profile criteria.</p>
      <button @click="goBack" class="back-btn">Back to Profile</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const matches = ref([]);
const currentProfile = ref(null);
const favorites = ref([]);
const error = ref('');
const loading = ref(false);
const sortBy = ref('name');

const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001';

async function fetchMatches() {
  loading.value = true;
  error.value = '';
  const profileId = route.params.id;
  
  try {
    // First get the current profile details
    const profileRes = await fetch(`${backendBaseUrl}/api/profiles/${profileId}`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      credentials: 'include'
    });
    
    if (!profileRes.ok) throw new Error('Failed to load profile details');
    currentProfile.value = await profileRes.json();

    // Then get matches for this profile
    const matchesRes = await fetch(`${backendBaseUrl}/api/profiles/matches/${profileId}`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      credentials: 'include'
    });
    
    if (!matchesRes.ok) throw new Error('Failed to load matches');
    const data = await matchesRes.json();
    matches.value = data.matching_profiles || [];
    
    // Load user's favorites
    await loadFavorites();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function loadFavorites() {
  if (!authStore.user?.id) return;
  
  try {
    const res = await fetch(`${backendBaseUrl}/api/users/${authStore.user.id}/favourites`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      credentials: 'include'
    });
    
    if (res.ok) {
      favorites.value = await res.json();
    }
  } catch (err) {
    console.error('Error loading favorites:', err);
  }
}

function isFavorited(userId) {
  return favorites.value.some(fav => fav.id === userId);
}

async function toggleFavorite(userId) {
  try {
    const method = isFavorited(userId) ? 'DELETE' : 'POST';
    const res = await fetch(`${backendBaseUrl}/api/profiles/${userId}/favourite`, {
      method,
      headers: { Authorization: `Bearer ${authStore.token}` },
      credentials: 'include'
    });
    
    if (res.ok) {
      await loadFavorites(); // Refresh favorites list
    }
  } catch (err) {
    console.error('Error toggling favorite:', err);
  }
}

function sortMatches() {
  matches.value.sort((a, b) => {
    if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name);
    } else if (sortBy.value === 'parish') {
      return a.parish.localeCompare(b.parish);
    } else if (sortBy.value === 'age') {
      return (new Date().getFullYear() - a.birth_year) - (new Date().getFullYear() - b.birth_year);
    }
    return 0;
  });
}

function goBack() {
  router.back();
}

onMounted(() => {
  fetchMatches();
});
</script>

<style scoped>
.match-report-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.report-description {
  color: #666;
  margin-bottom: 30px;
}

.sort-options {
  margin: 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-options select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.match-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.match-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s;
}

.match-card:hover {
  transform: translateY(-5px);
}

.match-photo-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.match-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.favorite-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  color: #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.favorite-btn:hover {
  color: pink;
}

.favorite-btn.favorited {
  color: red;
}

.match-info {
  padding: 15px;
}

.shared-traits {
  margin: 15px 0;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 4px;
}

.shared-traits h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #555;
}

.shared-traits ul {
  margin: 0;
  padding-left: 20px;
}

.shared-traits li {
  margin-bottom: 5px;
}

.view-profile-btn {
  display: inline-block;
  margin-top: 10px;
  padding: 8px 15px;
  background: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background 0.2s;
}

.view-profile-btn:hover {
  background: #3e8e41;
}

.no-matches {
  text-align: center;
  padding: 40px;
  background: #f8f8f8;
  border-radius: 8px;
}

.back-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-btn:hover {
  background: #0056b3;
}

.error-message {
  color: #dc3545;
  padding: 10px;
  background: #f8d7da;
  border-radius: 4px;
  margin-bottom: 20px;
}

.loading-message {
  color: #17a2b8;
  padding: 10px;
  background: #d1ecf1;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}
</style>