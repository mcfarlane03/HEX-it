<template>
  <div class="container">
    <main class="main-layout">
      <!-- Search Form -->
      <div class="search-container">
        <h1 class="title">Search</h1>
        <form @submit.prevent="handleSearch" class="search-form">
          <input v-model="search.name" type="text" placeholder="Name" />
          <input v-model="search.birthYear" type="number" placeholder="Birth Year" />
          <select v-model="search.sex">
            <option value="">Select Sex</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
          <input v-model="search.race" type="text" placeholder="Race" />

          <button type="submit">Search</button>
        </form>
      </div>

      <!-- Right-side content -->
      <div class="content-panel">
        <div class="filters">
          <span class="filter-title">Filter by:</span>
          <button class="btn" @click="applyFilter('name')">Name</button>
          <button class="btn" @click="applyFilter('birth')">Birth</button>
          <button class="btn" @click="applyFilter('sex')">Sex</button>
          <button class="btn" @click="applyFilter('race')">Race</button>
        </div>

        <section class="profiles">
      <div class="profile-card" v-for="profile in profiles" :key="profile.id">
        <img :src="profile.photo ? `http://localhost:5001/api/photo/${profile.photo}` : '/default-profile.png'" alt="Profile" class="profile-image">
        
        <div class="profile-info">
          <div class="profile-name">
            {{ profile.name }}
            <!-- <button class="heart" v-if="authStore.isLoggedIn" @click="toggleFavorite(profile)">
              <span :class="{ favorited: profile.favorited }">♥</span>
            </button> -->
          </div>
          <div class="actions">
            <router-link :to="{ name: 'profileDetail', params: { id: profile.id } }" class="view-more" replace>View more details</router-link>
          </div>
        </div>
      </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const search = reactive({
  name: '',
  birthYear: '',
  sex: '',
  race: ''
})
const activeFilter = ref('')
const selectedProfile = ref(null)
const showModal = ref(false)
const error = ref(null)

const allProfiles = ref([])

const profiles = computed(() => {
  let filtered = [...allProfiles.value]

  if (search.name) {
    filtered = filtered.filter(p => p.name.toLowerCase().includes(search.name.toLowerCase()))
  } else if (search.birthYear) {
    filtered = filtered.filter(p => p.birthYear === Number(search.birthYear))
  } else if (search.sex) {
    filtered = filtered.filter(p => p.sex === search.sex)
  } else if (search.race) {
    filtered = filtered.filter(p => p.race.toLowerCase().includes(search.race.toLowerCase()))
  }

  switch (activeFilter.value) {
    case 'name':
      filtered.sort((a, b) => a.name.localeCompare(b.name))
      break
    case 'birth':
      filtered.sort((a, b) => a.birthYear - b.birthYear)
      break
    case 'sex':
      filtered.sort((a, b) => a.sex.localeCompare(b.sex))
      break
    case 'race':
      filtered.sort((a, b) => a.race.localeCompare(b.race))
      break
  }

  return filtered
})

const handleSearch = () => {
  // Build query parameters from search object
  const params = new URLSearchParams()
  if (search.name) params.append('name', search.name)
  if (search.birthYear) params.append('birth_year', search.birthYear)
  if (search.sex) params.append('sex', search.sex)
  if (search.race) params.append('race', search.race)

  fetch(`/api/search?${params.toString()}`, {
    credentials: 'include'
  })
    .then(res => {
      if (!res.ok) {
        throw new Error('Failed to search profiles')
      }
      return res.json()
    })
      .then(data => {
        console.log('Search results:', data)
        allProfiles.value = data.map(p => {
          const { _sa_instance_state, ...cleaned } = p
          cleaned.image = `http://localhost:5001/api/photo/${cleaned.photo}`
          return cleaned
        })
      })
    .catch(err => {
      console.error('Error searching profiles:', err)
      error.value = err.message
    })
}

const applyFilter = (filterType) => {
  activeFilter.value = filterType
}

function fetchProfiles() {
  fetch('/api/profiles?limit=4', {
    credentials: 'include'
  })
    .then(res => {
      if (!res.ok) {
        throw new Error('Failed to fetch profiles')
      }
      return res.json()
    })
    .then(data => {
      console.log('Fetched profiles:', data)
        allProfiles.value = data.map(p => {
          const { _sa_instance_state, ...cleaned } = p
          cleaned.image = `http://localhost:5001/api/photo/${cleaned.photo}`
          return cleaned
        })
    })
    .catch(err => {
      console.error('Error fetching profiles:', err)
      error.value = err.message
    })
}

onMounted(() => {
  fetchProfiles()
})

function viewProfile(profileId) {
  fetch(`http://localhost:8080/api/profiles/${profileId}`, {
    credentials: 'include'
  })
    .then(res => {
      if (!res.ok) throw new Error('Profile not found')
      return res.json()
    })
    .then(data => {
      const { _sa_instance_state, ...cleaned } = data
      selectedProfile.value = cleaned
      showModal.value = true
    })
    .catch(err => {
      console.error(err)
      error.value = err.message
    })
}
</script>

  
<style scoped>
  .container {
    min-height: 100vh;
    padding: 1rem;
    max-width: 100%;
  }

  .main-layout {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
  }

  
  /* Search Form Styles */
  .search-container {
    background-color: white;
    padding: 1.5rem;
    border-radius: 1rem;
    width: 350px;
    box-shadow: 0 0 10px black;
  }

  .title {
    text-align: center;
    color: red;
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }

  .search-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .search-form input,
  .search-form select {
    padding: 0.5rem;
    border: 2px solid orange;
    border-radius: 0.5rem;
    font-size: 0.95rem;
  }

  .search-form input:focus,
  .search-form select:focus {
    outline: none;
    border-color: pink;
  }

  .search-form button {
    padding: 0.5rem;
    background: linear-gradient(90deg, pink, rgb(255, 0, 85), rgb(255, 123, 0));
    border: none;
    border-radius: 0.5rem;
    color: white;
    font-weight: bold;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .search-form button:hover {
    background: linear-gradient(90deg, rgb(255, 128, 0), rgb(255, 0, 102), pink);
  }

  /* Right Side Content */
  .content-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* Filters */
  .filters {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .filter-title {
    text-align: center;
    color: rgb(255, 162, 0);
    font-size: 1.4rem;
    font-style: italic;
    margin-bottom: 1rem;
  }

  .btn {
    background-color: pink;
    color: black;
    padding: 0.5rem 1.2rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .btn:hover {
    background-color: rgb(255, 0, 72);
    color: white;
  }

  /* Profiles */
  .profiles {
    background-color: white;
    padding: 1rem;
    border-radius: 1rem;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  }

  .profile-info {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex: 1;
  }
  .profile-name {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .heart {
    background: none;
    border: none;
    cursor: pointer;
    color: pink;
    font-size: 1.5rem;
  }
  .heart.favorited {
    color: red;
  }

  .profile-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .profile-image {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border-radius: 50%;
    border: 2px solid pink;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .view-more {
    color: orange;
    text-decoration: underline;
    font-weight: bold;
    font-size: 0.9rem;
    cursor: pointer;
  }
</style>
