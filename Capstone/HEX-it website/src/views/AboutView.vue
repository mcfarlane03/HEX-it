<template>
  <div>
    <h1>About Us</h1>
    <p>This is the about page.</p>
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
