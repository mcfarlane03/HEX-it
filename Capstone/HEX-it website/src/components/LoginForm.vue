<template>
    <form id="loginForm" @submit.prevent="handleLogin">
        <div class="login-container">
            <h1>Login</h1>
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" class="form-control" v-model="username" required placeholder="Enter your username" />
                <label for="password">Password:</label>
                <input type="password" id="password" class="form-control" v-model="password" placeholder="Enter your password" required/>
            </div>
            <button type="submit">Login</button>
            <div v-if="message" class="alert alert-success">{{ message }}</div>
            <div v-if="errors.length" class="alert alert-danger">
                <ul>
                <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
                </ul>
            </div>
        </div>
    </form>
</template>
<script setup>
    import { onMounted, ref } from 'vue';
    import { useRouter } from 'vue-router';
    import { useAuthStore } from '../stores/auth';

    const authStore = useAuthStore();

    const router = useRouter();
    const username = ref('');
    const password = ref('');
    const message = ref('');
    const csrf_token = ref('');
    const errors = ref([]);
    
    // Method to fetch CSRF token
    function getCsrfToken() {
    fetch("/api/v1/csrf-token")
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to get CSRF token");
        }
        return response.json();
    })
    .then(data => {
        csrf_token.value = data.csrf_token;
    })
    .catch(err => {
        console.error("Error fetching CSRF token", err);
    });
}

    
    // Fetch CSRF token when component is mounted
    onMounted(() => {
        getCsrfToken();
    });
    
    function handleLogin() {
        // Create the form data properly
        const formData = new FormData();
        formData.append('username', username.value);
        formData.append('password', password.value);
        
        fetch("/api/auth/login", {
            method: "POST",
            // Remove CSRF token header since backend login route is exempt
            // headers: {
            //     "X-CSRF-Token": csrf_token.value,
            // },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Handle HTTP errors properly
                return response.json().then(data => Promise.reject(data));
            }
            return response.json();
        })
        .then(data => {
            message.value = data.message || "Login successful!";
            errors.value = [];
            username.value = "";
            password.value = "";
            
            // Store the authentication token and user data
            authStore.login(data.user, data.token);
            console.log("Stored token:", data.token);
setTimeout(() => {
    router.push({ name: "home" });
}, 500);
        })
        .catch(error => {
            console.error("Login error:", error);
            if (error.errors) {
                errors.value = Array.isArray(error.errors) ? error.errors : [error.errors];
            } else {
                errors.value = ["Login failed. Please try again."];
            }
            message.value = "";
        });
    }
</script>
<style scoped>
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
h1 {
    text-align: center;
    margin-bottom: 20px;
}
.form-group {
    margin-bottom: 15px;
}
label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}
input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 4px;
}
button {
    width: 100%;
    padding: 10px;
    background-color: #ff789a;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
button:hover {
    background-color: #ff3d6d;
    transition: background-color 0.3s ease;
}
.alert {
    margin-top: 15px;
    padding: 10px;
    border-radius: 4px;
}
.alert-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.alert-danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
.alert-success {
    color: #155724;
    border: 1px solid #c3e6cb;
}
</style>