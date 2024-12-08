<template>
    <div class="relative h-screen flex items-center justify-center bg-[#d9e6e7] overflow-hidden">
  
      <!-- Centered Content -->
      <div
        class="relative z-10 max-w-lg p-8 bg-white bg-opacity-90 rounded-lg shadow-lg text-center animate-fade-in"
      >
        <!-- Interactive Background -->
        <InteractiveBackground />
        <h1 class="text-6xl font-bold text-[#56a3a6] mb-4">404</h1>
        <p class="text-lg text-[#30506a] mb-6">
          Oops! The page you're looking for doesn't exist.
        </p>
        <router-link
          to="/"
          class="inline-block px-6 py-3 text-white bg-[#56a3a6] rounded-md font-medium shadow-md hover:bg-[#469093] hover:scale-105 transition duration-300"
        >
          Back to Home
        </router-link>
      </div>
    </div>
  </template>
  
  <script>
  import InteractiveBackground from "@/components/InteractiveBackground.vue";
  
  export default {
    name: "NotFoundPage",
    components: {
      InteractiveBackground,
    },
  };
  </script>
  
  <style>
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .animate-fade-in {
    animation: fade-in 1s ease-out;
  }
  </style>
  