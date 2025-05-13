<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
      <div class="container-fluid">
        <RouterLink class="navbar-brand" to="/home">Jam-Date</RouterLink>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/about">About</RouterLink>
            </li>
            <li class="nav-item" v-if="authStore.isAuthenticated">
              <RouterLink class="nav-link" to="/profile">My Profiles</RouterLink>
            </li>
            <li class="nav-item" v-if="authStore.isAuthenticated">
              <RouterLink class="nav-link" to="/create">Create Profile</RouterLink>
            </li>
          </ul>
            
          <ul class="navbar-nav">
              <li v-if="authStore.isAuthenticated">
                <button @click="handleLogout" class="btn">Logout</button>              </li>
              <li v-else class="nav-item">
                <RouterLink class="btn" to="/login">Login</RouterLink>
                <RouterLink class="btn" to="/register">Register</RouterLink>
              </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink } from "vue-router";
import { useAuthStore } from '../stores/auth';
import { onMounted } from 'vue';
const authStore = useAuthStore();

onMounted(() => {
  authStore.checkAuth();
});

function handleLogout() {
  authStore.logout();
  window.location.href = '/';
}


</script>

<style>
.nav-item {
  margin-right: 20px;
  display: flex;
}

.navbar {
  background-color: #ff4362;
  padding: 10px;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  padding: 10px 15px;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: #faf5f6;
  color: #ff4362;
}

.navbar-brand {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.btn {
  color: #fff;
  text-decoration: none;
  padding: 10px 15px;
  border-radius: 5px;
  background-color: #ff4362;
  transition: background-color 0.3s;
}
.btn:hover {
  background-color: #faf5f6;
  color: #ff4362;
}
</style>