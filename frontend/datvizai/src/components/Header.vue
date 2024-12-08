<template>
  <header class="header">
    <div
      class="header-content hover-trigger"
      @mouseover="showGif"
      @mouseleave="showPng"
    >
      <!-- Logo -->
      <img
        :src="currentLogo"
        alt="DatViz AI Logo"
        class="logo"
      />

      <!-- App Name with Beating Animation -->
      <h1
        class="app-name"
        :class="{ beating: isHovered }"
      >
        DatViz AI
      </h1>
    </div>
    <div class="header-line"></div>
  </header>
</template>

<script>
import gifLogo from "@/assets/logos/app-logo.gif";
import pngLogo from "@/assets/logos/app-logo.png";

export default {
  name: "Header",
  data() {
    return {
      isHovered: false, // Tracks hover state
      isGifPlaying: true, // Tracks if the GIF is playing
      gifLogo,
      pngLogo,
    };
  },
  computed: {
    currentLogo() {
      // Use the GIF if it's playing, otherwise switch based on hover state
      return this.isGifPlaying
        ? this.gifLogo
        : this.isHovered
        ? this.gifLogo
        : this.pngLogo;
    },
  },
  mounted() {
    // Play the GIF on page load, then switch to PNG after 3 seconds (adjust time if needed)
    setTimeout(() => {
      this.isGifPlaying = false;
    }, 3000); // Adjust this value based on the duration of your GIF animation
  },
  methods: {
    showGif() {
      if (!this.isGifPlaying) {
        this.isHovered = true;
      }
    },
    showPng() {
      this.isHovered = false;
    },
  },
};
</script>

<style scoped>
/* Header Styling */
.header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 50px;
}

.app-name {
  font-size: 1.8rem;
  font-weight: 600;
  color: #102e4a;
  transition: transform 0.2s ease-in-out;
}

.app-name.beating {
  animation: beat 0.6s infinite;
}

@keyframes beat {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.header-line {
  width: 50%;
  height: 3px;
  background: linear-gradient(to right, #56a3a6, transparent);
  margin-top: 0.5rem;
}
</style>
