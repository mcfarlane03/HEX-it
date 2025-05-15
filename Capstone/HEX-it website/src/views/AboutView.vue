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
