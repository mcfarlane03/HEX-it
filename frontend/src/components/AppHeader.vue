<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
      <div class="container-fluid">
        
        <RouterLink class="navbar-brand" to="">
          <!-- <img src="@/assets/image.png" alt="HEX-it Logo" style="height: 40px; margin-right: 10px;" /> -->
          HEX-it
        </RouterLink>
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
            
            <li v-if="authStore.isAuthenticated" class="nav-item">
              <RouterLink class="nav-link" to="/home">Home</RouterLink>
              <RouterLink class="nav-link" to="/about">About</RouterLink>
              <RouterLink class="nav-link" to="/matlab-control">MATLAB Control</RouterLink>
            </li>
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
  background-color: #001f4d; /* Navy blue */
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
  background-color: #ffffff; /* White */
  color: #001f4d; /* Navy blue */
}

.navbar-brand {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.btn {
  color: #ffffff;
  text-decoration: none;
  padding: 10px 15px;
  border-radius: 5px;
  background-color: #001f4d; /* Navy blue */
  transition: background-color 0.3s;
}
.btn:hover {
  background-color: #ffffff; /* White */
  color: #001f4d; /* Navy blue */
}
</style>
