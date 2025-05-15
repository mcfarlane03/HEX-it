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
      <h2>Legend</h2>
      <table id="fire-data-table" class="table table-striped">
        <thead>
          <tr>
            <th id="people">People - <span class="limegreen-line"></span></th>
            <th id="devicepath">Location of Device - <span class="red-line"></span></th>
            <th id="devicepath">Passable Space - <span class="white-line"></span></th>
            <th id="devicepath">Impassable Space - <span class="black-line"></span></th>
            <th id="devicepath">Computed Path - <span class="darkblue-line"></span></th>
            <th id="devicepath">Starting Position - <span class="skyblue-line"></span></th>
            <th id="devicepath">Goal - <span class="purple-line"></span></th>
            <th id="devicepath">Fire - <span class="red-X"></span></th>
          </tr>
        </thead>
        <!-- <tbody id="fire-data-body">
          <tr v-for="(fireData, index) in fireDataList" :key="index">
            <td>{{ fireData.temperature }}</td>
            <td>{{ fireData.location }}</td>
          </tr>
        </tbody> -->
      </table>
    </div>
  </div>
</template>

<script>
// /* import io from 'socket.io-client'; // Import the socket.io client */
import blueprintImage from '../assets/blueprint11.png';

export default {
  data() {
    return {
      blueprintImageUrl: blueprintImage,
      fireDataList: [],
      /* socket: null, */
    };
  },
  mounted() {
    /* this.connectSocket(); */
  },
  beforeUnmount() {
    /* this.disconnectSocket(); */
  },
  methods: {
    /* connectSocket() {
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
    }, */
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

.limegreen-line {
            border: none;
            height: 10px;
            background-color: limegreen;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.darkblue-line {
            border: none;
            height: 10px;
            background-color: darkblue;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.red-line {
            border: none;
            height: 10px;
            background-color: red;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.white-line {
            border: none;
            height: 10px;
            background-color: white;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.black-line {
            border: none;
            height: 10px;
            background-color: black;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }

.purple-line {
            border: none;
            height: 10px;
            background-color: purple;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.skyblue-line {
            border: none;
            height: 10px;
            background-color: skyblue;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }
.red-X {
            border: none;
            height: 10px;
            background-color: red;
            width: 100px; /* Adjust width as needed */
            display: inline-block;
        }


.dot {
  height: 100px;
  width: 100px;
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


#blueprint-container {
    /* The size and border are now in the HTML, but you can add other styles here */
    /* position: relative;  */
    /* width: 800px;  */
    /* height: 600px;  */
    /* border: 1px solid black;  */
    margin: 10px auto; /* Center the container */
    background-color: #f0f0f0; /* A light background */
}

.room {
    position: absolute;
    /* border: 1px solid rgb(255, 0, 0); */
}

.live-indicator {
    display: flex;
    align-items: center;
    font-weight: bold;
    color: black;
    /*background-color: #dc3545; /* Bootstrap danger red */
    padding: 5px 10px;
    border-radius: 5px;
    font-size: 14px;
}

.live-indicator .dot {
    height: 15px;
    width: 15px;
    background-color: #ff0000;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.3);
        opacity: 0.7;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

</style>