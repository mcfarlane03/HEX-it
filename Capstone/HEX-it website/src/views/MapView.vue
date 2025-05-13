<template>
    <div>
      <h1 id="viz">Visualization</h1>
  
      <div class="live-indicator ms-auto">
        <div class="dot"></div>
        <h3>Live</h3>
      </div>
  
      <div
        id="blueprint-container"
        style="position: relative; width: 600px; height: 600px; border: 1px solid black;"
      >
        <img
          id="blueprint-image"
          :src="blueprintImageUrl"
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block;"
        />
        <div
          id="flame-layer"
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
        ></div>
        <div
          id="person-layer"
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
        ></div>
      </div>
  
      <div>
        <h2>Fire Data</h2>
        <table id="fire-data-table" class="table table-striped">
          <thead>
            <tr>
              <th>Temperature (°C)</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody id="fire-data-body">
            <tr v-for="(fireData, index) in fireDataList" :key="index">
              <td>{{ fireData.temperature }}</td>
              <td>{{ fireData.location }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <p>Note: Simulated data is being displayed. Connect your hardware for real-time updates.</p>
    </div>
  </template>
  
  <script>
  import io from 'socket.io-client'; // Import the socket.io client
  import blueprintImage from '../assets/blueprint1.jpg';
  
  export default {
    data() {
      return {
        blueprintImageUrl: blueprintImage,
        fireDataList: [],
        socket: null,
      };
    },
    mounted() {
      this.connectSocket();
    },
    beforeUnmount() {
      this.disconnectSocket();
    },
    methods: {
      connectSocket() {
        this.socket = io('http://localhost:5000'); // Replace with your backend SocketIO server URL
  
        this.socket.on('connect', () => {
          console.log('Connected to WebSocket');
        });
  
        this.socket.on('disconnect', () => {
          console.log('Disconnected from WebSocket');
        });
  
        this.socket.on('fire_data', (data) => {
          this.updateFireData(data);
        });
  
        this.socket.on('person_locations', (locations) => {
          this.updatePersonLayer(locations);
        });
  
        this.socket.on('flame_data', (flames) => {
          this.updateFlameLayer(flames);
        });
      },
      disconnectSocket() {
        if (this.socket) {
          this.socket.disconnect();
          this.socket = null;
        }
      },
      updateFireData(newData) {
        this.fireDataList = newData; // Assuming the backend sends an array of fire data objects
      },
      updatePersonLayer(locations) {
        const personLayer = document.getElementById('person-layer');
        personLayer.innerHTML = ''; // Clear previous locations
        locations.forEach((location) => {
          const person = document.createElement('div');
          person.className = 'person-marker';
          person.style.position = 'absolute';
          person.style.left = `${location.x}px`; // Adjust units as needed
          person.style.top = `${location.y}px`; // Adjust units as needed
          person.style.width = '20px'; // Example size
          person.style.height = '20px'; // Example size
          person.style.backgroundColor = 'blue';
          person.style.borderRadius = '50%';
          personLayer.appendChild(person);
        });
      },
      updateFlameLayer(flames) {
        const flameLayer = document.getElementById('flame-layer');
        flameLayer.innerHTML = ''; // Clear previous flames
        flames.forEach((flame) => {
          const flameElement = document.createElement('div');
          flameElement.className = 'flame-marker';
          flameElement.style.position = 'absolute';
          flameElement.style.left = `${flame.x}px`; // Adjust units as needed
          flameElement.style.top = `${flame.y}px`; // Adjust units as needed
          flameElement.style.width = '15px'; // Example size
          flameElement.style.height = '15px'; // Example size
          flameElement.style.backgroundColor = 'orange';
          flameElement.style.borderRadius = '50%';
          flameLayer.appendChild(flameElement);
        });
      },
    },
  };
  </script>
  
  <style scoped>
  .live-indicator {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .dot {
    height: 10px;
    width: 10px;
    background-color: red;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
  }
  
  /* Example styling for person and flame markers */
  .person-marker {
    /* Add your styling for person markers */
  }
  
  .flame-marker {
    /* Add your styling for flame markers */
  }
  </style>