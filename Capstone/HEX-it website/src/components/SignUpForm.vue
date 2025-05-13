<template>
    <div class="signup-container">
        <form id="signupForm" @submit.prevent="handleRegister">
            <h1>Register</h1>
            <div class="form-group">
                <label for="id" class="form-label">ID:</label>
                <input type="number" id="id" class="form-control" v-model="user.id" placeholder="Enter your ID" required />
                
                <label for="password" class="form-label">Password:</label>
                <input type="password" id="password" class="form-control" v-model="user.password" placeholder="Enter your password" required />
            </div>
            <button type="submit">Register</button>

            <div v-if="message" class="alert alert-success">{{ message }}</div>
            <div v-if="errors.length" class="alert alert-danger">
                <ul>
                    <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
                </ul>
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const csrf_token = ref("");
const user = ref({
    id: null, // ID field
    password: "", // Password field
});

const message = ref("");
const errors = ref([]);

// Fetch CSRF token when component is mounted
onMounted(() => {
    getCsrfToken();
});

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
            console.log(data);
            csrf_token.value = data.csrf_token;
        })
        .catch(err => {
            console.error("Error fetching CSRF token", err);
        });
}

// Method to handle registration
async function handleRegister() {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Specify JSON content type
                'X-CSRF-Token': csrf_token.value,  // Include CSRF token if required
            },
            body: JSON.stringify(user.value), // Convert the user object to JSON
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'An error occurred');
        }

        const data = await response.json();
        console.log('Registration successful:', data);
        message.value = data.message;
        router.push('/login'); // Redirect to login page after successful registration
    } catch (error) {
        console.error('Registration error:', error.message);
        errors.value = [error.message];
    }
}
</script>

<style scoped>
.signup-container {
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
    background-color: #001f4d; /* Navy blue */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #001a3c; /* Darker navy blue */
    transition: background-color 0.3s ease;
}
</style>