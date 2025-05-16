<template>
  <div class="matlab-control">
    <h2>MATLAB Control</h2>
    <button @click="startMatlab" :disabled="running">Start MATLAB Script</button>
    <button @click="stopMatlab" :disabled="!running">Stop MATLAB Script</button>
    <p v-if="message">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const running = ref(false)
const message = ref('')
const error = ref('')

async function startMatlab() {
  try {
    const response = await axios.post('/api/matlab/start')
    message.value = response.data.message || 'MATLAB script started'
    error.value = ''
    running.value = true
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to start MATLAB script'
    message.value = ''
  }
}

async function stopMatlab() {
  try {
    const response = await axios.post('/api/matlab/stop')
    message.value = response.data.message || 'MATLAB script stopped'
    error.value = ''
    running.value = false
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to stop MATLAB script'
    message.value = ''
  }
}
</script>

<style scoped>
.matlab-control {
  max-width: 400px;
  margin: 20px auto;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  text-align: center;
}

button {
  margin: 10px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
