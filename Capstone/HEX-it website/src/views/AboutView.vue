<template>
  <div class="about container">
    <h1>About Us</h1>
    <section>
      <h2>Highly Efficient X-it (HEX-it)</h2>
      <h3>Background</h3>
      <p>
        Jamaica has undergone rapid infrastructure modernization in recent years, marked by a significant increase in the construction of high-rise commercial and residential buildings. While this development brings economic and social benefits, it also introduces new challenges, particularly in the context of emergency preparedness. These structures are increasingly vulnerable to natural disasters such as earthquakes and fires, which have become more frequent and intense due to climate change. During emergencies, occupants often face confusion and fear, struggling to identify the shortest and safest evacuation routes. Simultaneously, emergency response teams are hindered by a lack of real-time information, such as the number of occupants still inside the building, their exact locations, and the most efficient paths to reach them. The rapid expansion of high-rise buildings has outpaced the capacity of the Jamaica Fire Brigade to respond effectively, creating an urgent need for advanced safety and response systems to protect lives and property.
      </p>
      <h3>Problem Statement</h3>
      <p>
        The problem lies with the fact that current emergency response systems in high-rise buildings lack real-time data and, in the event of a natural disaster, are unaware of possible obstacles that would change the layout of the building as well as identify the location of trapped individuals. This results in delayed evacuations, inefficient rescue operations, and increased risk to lives and property. There is a critical need for a system that can provide real-time situational awareness, including the location of trapped individuals, environmental conditions, and optimal evacuation routes, to enhance the safety of occupants and the effectiveness of emergency responders.
      </p>
      <h3>Problem Context</h3>
      <p>
        The project leverages the legal requirement for buildings in Jamaica to submit floor plans to municipal corporations for construction approval. The proposed solution involves developing an integrated hardware-software system that combines pre-loaded building blueprints with real-time sensor data. This system will capture real-time data to accurately map accessible and inaccessible areas within a building during emergencies, identify trapped individuals, and determine the safest evacuation routes. The collected data will be transmitted to a control centre, where an operator will analyze and relay critical information to search and rescue teams operating inside the building. This solution aims to enhance occupant safety and support emergency responders in making informed, life-saving decisions.
      </p>
      <h3>Computational Problem</h3>
      <p>
        Our project will take in as input, real-time sensor data, a pre-loaded building blueprint, and real-time location data from emergency response personnel within the building. The drone will not be built or present during the demonstration, instead the project will focus on constructing the integrated sensor module. Based on the sensor data, the hardware system will send actionable data to a control centre. This data will include environmental information (temperature and humidity via BMP sensors), spatial mapping (via LiDAR), and motion detection and human detection (via MPU modules and ESP32 Camera).
      </p>
      <p>
        The system will output to the control center a website displaying a generated map of the building, the location and path to identified victims, and compromised areas noted on the map.  The system will also track emergency personnel who will enter the building after the room visualization has been completed.
      </p>
      <p>
        The computational challenge of this project involves efficiently filtering noisy sensor data to produce the optimal system output. This includes generating dynamic obstacle maps, identifying safe evacuation routes, and tracking personnel positions—all within strict hardware limitations. To address these constraints, we’ve implemented several optimizations. To mitigate the limited battery capacity that would be associated with the average drone, we added an external battery to power the sensor unit. As stated before power is a major constraint and due to this the system was not able to provide the optimal 5V as required by the device specification  to the LiDAR sensor as this requires a heavier battery, instead we’ve chosen to operate them at 3.7V, which helps reduce weight and extend operation time.
      </p>
      <p>
        A constraint of our system is associated with the LoRa data transmission, as it is limited to 255 bytes of data. To overcome this, we structured the data using structs and split it into packets, which also assists in reducing power consumption while maintaining an acceptable emergency response latency. Current limitations include the inability to count the exact number of occupants (only detecting presence/absence) and classify obstacle types—both of which are areas for future development. Additionally, real-time data processing is affected by computational limits, which may impact the speed and accuracy of map updates and detection alerts.
      </p>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutView',
};
</script>

<style scoped>
.about.container {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
  background-color: #fff9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(255, 105, 97, 0.2);
  color: #333;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  color: #0080ff;
  margin-bottom: 20px;
}

h2 {
  color: #0080ff;
  margin-top: 30px;
  margin-bottom: 10px;
}

ul {
  list-style-type: disc;
  padding-left: 20px;
}
</style>
