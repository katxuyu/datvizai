<template>
  <main class="main-content" :class="{ 'animate': hasLoaded }">
    <div class="center-content">
      <!-- Welcome Text -->
      <h1 class="welcome-text">
        Welcome to <span class="highlight">DatViz AI!</span>
      </h1>

      <!-- Simplified and Italicized Tagline -->
      <p class="tagline">Democratizing data analytics</p>

      <!-- Intro Section -->
      <div class="intro">
        <p>
          Discover a smarter way to analyze your data with <span class="highlight">DatViz AI</span>,
          powered by OpenAI's advanced <span class="highlight">ChatGPT-4</span> model. Using natural
          language, you can effortlessly simplify and summarize complex datasets, calculate key
          statistics, and generate intuitive, visually appealing graphs and charts.
        </p>
      </div>

      <!-- Email Input and Button Section -->
      <div class="email-input mt-8">
        <form @submit.prevent="handleSubmit" class="flex flex-col items-center">
          <!-- Conditionally Show Textbox -->
          <input
            v-if="userStatus === 'New'"
            type="email"
            v-model="email"
            placeholder="Enter your email address"
            class="w-full max-w-md px-4 py-2 mb-4 text-gray-800 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
            required
          />
          <!-- Always Show the Button -->
          <button
            type="submit"
            class="px-6 py-2 text-white bg-teal-500 rounded hover:bg-teal-600 focus:ring-2 focus:ring-teal-400"
          >
            Let’s Go!
          </button>
        </form>
      </div>
    </div>

    <!-- Notification Component -->
    <Notification
      v-if="notification.message"
      :message="notification.message"
      :type="notification.type"
      @dismiss="clearNotification"
    />
  </main>
</template>

<script>
import { getPublicIP } from "@/utils/getPublicIP"; // Utility to fetch public IP
import Notification from "@/components/Notification.vue";

export default {
  name: "MainContent",
  components: { Notification },
  data() {
    return {
      email: "",
      hasLoaded: false,
      userStatus: null,
      publicIP: null,
      userUUID: null,
      notification: { message: null, type: null }, 
    };
  },
  async mounted() {
    try {
      // Fetch public IP
      const publicIP = await getPublicIP();
      this.publicIP = publicIP;

      if (publicIP) {
        // Make POST request to check user status
        const response = await fetch(`${import.meta.env.VITE_API_HOST}/user/check`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ public_ip: publicIP }),
        });

        if (response.ok) {
          const data = await response.json();
          this.userStatus = data.status; // Save user status ("Existing" or "New")
          
          if (data.status === "Existing") {
            this.userUUID = data.uuid;
            localStorage.setItem("userAuthenticated", true);
            localStorage.setItem("userStatus", "Existing");
            localStorage.setItem("userUUID", this.userUUID);
          } else {
            // Reset localStorage for new users
            localStorage.removeItem("userAuthenticated");
            localStorage.removeItem("userStatus");
          }
        } else {
          console.error("Failed to check user status. Response not OK.");
          this.userStatus = "Unknown"; // Default to unknown
          localStorage.removeItem("userAuthenticated");
          localStorage.removeItem("userStatus");
        }
      }
    } catch (error) {
      console.error("Failed to fetch user status:", error);
      this.userStatus = "Unknown"; // Default to unknown
      localStorage.removeItem("userAuthenticated");
      localStorage.removeItem("userStatus");
    }

    // Trigger entrance animation
    setTimeout(() => {
      this.hasLoaded = true;
    }, 100); // Small delay to ensure smooth animation
  },
  methods: {
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },
    clearNotification() {
      this.notification = { message: null, type: null };
    },
    async handleSubmit() {
      if (this.userStatus === "New") {
        // Validate email
        if (!this.isValidEmail(this.email)) {
          this.notification = { message: "Please enter a valid email address.", type: "error" };
          return;
        }

        try {
          // Register user via POST request
          const response = await fetch(`${import.meta.env.VITE_API_HOST}/user/register`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: this.email,
              public_ip: this.publicIP,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            this.userUUID = data.uuid;
            localStorage.setItem("userAuthenticated", true);
            localStorage.setItem("userStatus", "Existing");
            localStorage.setItem("userUUID", this.userUUID);

            this.notification = {
              message: "Registration successful! Redirecting...",
              type: "success",
            };

            // Redirect to Chat Page
            this.$router.push({ name: "ChatPage" });
          } else {
            this.notification = { message: "Failed to register. Please try again later.", type: "error" };
          }
        } catch (error) {
          console.error("Failed to register user:", error);
          this.notification = { message: "Failed to register. Please check your connection.", type: "error" };
        }
      } else {
        // Existing user
        localStorage.setItem("userAuthenticated", true);
        localStorage.setItem("userStatus", "Existing");
        this.$router.push({ name: "ChatPage" });
      }
    },
  },
};
</script>

<style scoped>
/* Global Styling */
.main-content {
  text-align: center;
  padding: 2rem 1rem;
  font-family: "Poppins", sans-serif;
  color: #102e4a;
  background-color: #d9e6e7;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.main-content.animate {
  opacity: 1;
  transform: translateY(0);
}

.center-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.welcome-text {
  font-size: 2.5rem;
  font-weight: 700;
  color: #102e4a;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.highlight {
  color: #56a3a6;
  font-weight: 600;
}

.tagline {
  margin: 0;
  font-size: 1rem;
  font-style: italic;
  color: #30506a;
}

.intro {
  margin-top: 1.5rem;
  line-height: 1.8;
  font-size: 1.2rem;
  text-align: center;
}
</style>
