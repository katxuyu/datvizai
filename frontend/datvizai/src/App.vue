<template>
  <div id="app">
    <router-view />
    <InteractiveBackground />
  </div>
</template>

<script>
import InteractiveBackground from "@/components/InteractiveBackground.vue";
import LandingPage from "@/views/LandingPage.vue";

export default {
  name: "App",
  components: { InteractiveBackground, LandingPage },
};
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: "Poppins", sans-serif;
  color: #102e4a;
  background-color: #d9e6e7;
}

#app {
  position: relative;
}
</style>
