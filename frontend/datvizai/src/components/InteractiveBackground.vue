<template>
  <div id="background-container">
    <canvas id="canvas"></canvas>
  </div>
</template>

<script>
// Import the uploaded JavaScript logic directly
import { initInteractiveBackground } from "@/utils/interactiveBackground.js";

export default {
  name: "InteractiveBackground",
  mounted() {
    // Initialize the interactive background animation after the component is mounted
    const canvas = document.getElementById("canvas");
    initInteractiveBackground(canvas);
  },
};
</script>

<style scoped>
/* Ensure the canvas spans the entire background */
#background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1; /* Place behind content */
  overflow: hidden;
}

#canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
