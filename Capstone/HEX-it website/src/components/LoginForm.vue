<template>
    <form id="loginForm" @submit.prevent="handleLogin">
        <div class="login-container">
            <h1>Login</h1>
            <div class="form-group">
                <label for="id">ID:</label>
                <input
                    type="number"
                    id="id"
                    class="form-control"
                    v-model="user.id"
                    placeholder="Enter your ID"
                    required
                />

                <label for="password">Password:</label>
                <input
                    type="password"
                    id="password"
                    class="form-control"
                    v-model="user.password"
                    placeholder="Enter your password"
                    required
                />
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
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const user = ref({
    id: null, // ID field
    password: "", // Password field
});

const message = ref("");
const errors = ref([]);

// Method to handle login
async function handleLogin() {
    try {
        // Log the payload being sent to the backend
        console.log("Payload being sent:", user.value);

        const response = await fetch("http://localhost:5000/api/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(user.value),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Login failed");
        }

        const data = await response.json();
        message.value = data.message || "Login successful!";
        errors.value = [];
        user.value.id = null;
        user.value.password = "";

        // Store the authentication token and user data
        authStore.login(data.user, data.token);
        console.log("Stored token:", data.token);

        // Redirect to the home page
        setTimeout(() => {
            router.push({ name: "Home" });
        }, 500);
    } catch (error) {
        console.error("Login error:", error.message);
        errors.value = [error.message];
        message.value = "";
    }
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
    background-color: #0080ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
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
</style>