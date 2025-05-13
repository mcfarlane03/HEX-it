<template>
    <div class="signup-container">
        <form id="signupForm" @submit.prevent="handleRegister" enctype="multipart/form-data">
            <h1>Register</h1>
            <div class="form-group">
                <label for="username" class="form-label">Username:</label>
                <input type="text" id="username" class="form-control" v-model="user.username" placeholder="Enter your username" required />
                
                <label for="password" class="form-label">Password:</label>
                <input type="password" id="password" class="form-control" v-model="user.password" placeholder="Enter your password" required/>

                <label for="name" class="form-label">Name:</label>
                <input type="text" id="name" class="form-control" v-model="user.name" placeholder="Enter your full name" required />
                
                <label for="email" class="form-label">Email:</label>
                <input type="text" id="email" class="form-control" v-model="user.email" placeholder="Enter your email" required />
                
                <label for="photo" class="form-label">Profile Photo:</label>
                <input type="file" id="photo" class="form-control" @change="handlePhotoUpload"/>
                <small class="form-text text-muted">Please upload a JPG or PNG image for your profile picture.</small>
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
        username: "",
        password: "",
        name: "",
        email: "",
    });
    
    const photo = ref(null);
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
        
    // Method to handle photo upload
    function handlePhotoUpload(event) {
        photo.value = event.target.files[0];
    }

    function handleRegister() {
        errors.value = [];
        message.value = "";

        const signupForm = document.getElementById('signupForm');
        const form_data = new FormData(signupForm);

        form_data.append("username", user.value.username);
        form_data.append("password", user.value.password);
        form_data.append("name", user.value.name);
        form_data.append("email", user.value.email);
        form_data.append("photo", photo.value);
        form_data.append("csrf_token", csrf_token.value);

        console.log("Form data being sent:", form_data);
        
        fetch("/api/register", {
            method: "POST",
            body: form_data,
            headers: {
                "X-CSRF-Token": csrf_token.value,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
            errors.value = Object.values(data.errors).flat(); 
            message.value = "";
            } else {
                message.value = data.message;
                errors.value = [];
                user.username = "";
                user.password = "";
                user.name = "";
                user.email = "";
                photo.value = null;
                router.push({ name: 'login' });
            }
        })
        .catch(error => console.log(error));
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
</style>