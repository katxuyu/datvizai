<template>
  <div class="chat-page">

    <!-- Modal -->
    <UploadModal v-if="showModal" :close-button-disabled="closeButtonDisabled" :loading="loading" @close="closeModal"
      @upload-local-file="uploadLocalFile" @upload-google-sheet-data="uploadGoogleSheetData"
      @use-sample-data="useSampleData" />

    <!-- Moving Background -->
    <InteractiveBackground />

    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <img src="@/assets/logos/app-logo.png" alt="DatViz AI Logo" class="logo" />
        <h1 class="app-name">DatViz AI</h1>
      </div>
      <div class="header-line"></div>
    </header>


    <ChatBox :messages="messages" :files="files" :userMessage="userMessage" :graphs="graphs"
      @update:userMessage="userMessage = $event" :isProcessing="isProcessing" :isTextareaDisabled="textareaDisabled"
      :errorSuggestions="errorSuggestions" @send-message="sendMessage" @trigger-modal="triggerModal"
      @toggle-collapse="toggleCollapse">
      <!-- Floating Bubbles -->
      <template #bubbles>
        <div class="floating-bubbles">
          <div v-for="(bubble, index) in floatingBubbles" :key="index" class="bubble">
            {{ bubble }}
          </div>
        </div>
      </template>
    </ChatBox>



  </div>
</template>

<script>
import InteractiveBackground from "@/components/InteractiveBackground.vue";
import ChatBox from "@/components/ChatBox.vue";
import UploadModal from "@/components/UploadModal.vue";
import axios from "axios";
import Plotly from 'plotly.js-dist';

export default {
  name: "ChatPage",
  components: {
    InteractiveBackground,
    ChatBox,
    UploadModal,
  },
  data() {
    return {
      messages: [{ text: "Hello! How can I help you today?", type: "bot" }],
      userMessage: "",
      showModal: true,
      closeButtonDisabled: true,
      files: [],
      rowsPerPage: 10,
      loading: false,
      graphs: [],
      isProcessing: false,
      errorSuggestions: [],
      textareaDisabled: false,
      floatingBubbles: [],
    };
  },

  methods: {
    showFloatingBubble(content) {
      this.floatingBubbles.push(content);

      // Automatically remove the bubble after 1.5 seconds
      setTimeout(() => {
        this.floatingBubbles.shift();
      }, 1000000);
    },
    async sendMessage(message) {
      const userMessage = message || this.userMessage.trim();
      if (userMessage) {
        this.messages.push({ text: userMessage, type: "user" });
        this.isProcessing = true;
        const payload = {
          files: this.files,
          prompt: userMessage,
          uuid: localStorage.getItem("userUUID"),
        };

        try {
          const response = await axios.post(`${import.meta.env.VITE_API_HOST}/generate_graph`, payload);

          if (response.data.error && response.data.error === 'Insufficient credits. Subscribe to our Pro Version!') {
            this.textareaDisabled = true;
            // Display the error message
            this.messages.push({
              text: response.data.error,
              type: "bot",
            });

          } else if (response.data.status === "success") {
            this.errorSuggestions = [];
            const { available_credits, graphs } = response.data;
            this.showFloatingBubble(`Available Credits: ${response.data.available_credits}`);

            this.messages.push({
              text: `Available credits: ${available_credits}`,
              type: "bot",
            });

            graphs.forEach((graphObj, index) => {
              const uniqueId = `${Date.now()}-${index}`; // Generate unique ID

              this.messages.push({
                text: `Title: ${graphObj.title}\nDescription:${graphObj.description}`,
                type: "bot",
              });

              this.messages.push({
                id: uniqueId,
                type: "graph",
                graphData: graphObj.graph,
              });
            });
          } else if (response.data.status === "error") {
            // Handle error response
            this.messages.push({
              text: response.data.message,
              type: "bot",
            });

            if (response.data.suggestions && response.data.suggestions.length > 0) {
              this.errorSuggestions = response.data.suggestions;
            }
          }
        } catch (error) {
          console.error("Error communicating with the API:", error);
          this.messages.push({
            text: "An error occurred while processing your request. Please try again.",
            type: "bot",
          });
        } finally {
          this.userMessage = "";
          this.isProcessing = false;
        }
      }
    },

    triggerModal() {
      this.showModal = true;
      this.closeButtonDisabled = false;
    },
    closeModal() {
      this.showModal = false;
    },
    async uploadLocalFile(files) {
      if (!files || files.length === 0) {
        console.error("No files provided. Please select files to upload.");
        return;
      }
      this.loading = true; // Start loading
      this.files = [];
      try {
        const uploadedFiles = [];
        for (const file of files) {
          const response = await this.uploadData(file, {
            uuid: localStorage.getItem("userUUID"),
          });


          if (response.error && response.error === "Insufficient credits. Subscribe to our Pro Version!") {
            this.textareaDisabled = true; // Disable textarea
            this.messages.push({ text: response.error, type: "bot" });
            return; // Stop processing further files
          }



          const sanitizedResponse = response.replace(/NaN/g, "null");
          const data = JSON.parse(sanitizedResponse);
          if (data.available_credits) {
            // Show floating bubble for available credits
            this.showFloatingBubble(`Available Credits: ${data.available_credits}`);
          }

          if (data.files && Array.isArray(data.files)) {
            uploadedFiles.push(
              ...data.files.map((file) => ({
                fileName: file.file_name,
                data: file.data,
                collapsed: true,
                currentPage: 1,
                insights: file.insights,
                statistics: file.statistics,
                prompt_suggestions: file.prompt_suggestions,
              }))
            );
          }
        }

        this.files = [...this.files, ...uploadedFiles];
        this.messages.push({
          text: `${files.length} file(s) uploaded successfully!`,
          type: "bot",
        });
        this.showModal = false;
      } catch (error) {
        console.error("Error uploading local files:", error);
        this.messages.push({
          text: "An error occurred while uploading the files. Please try again.",
          type: "bot",
        });
      } finally {
        this.loading = false; // End loading
      }
    },



    async uploadGoogleSheetData(data) {

    },
    async useSampleData() {
      this.loading = true; // Start loading
      try {
        const sampleFile = await this.fetchSampleFile(); // Fetch the sample file
        const response = await this.uploadData(sampleFile, {
          uuid: localStorage.getItem("userUUID"),
        });

        if (response.error && response.error === "Insufficient credits. Subscribe to our Pro Version!") {
          this.textareaDisabled = true; // Disable textarea
          this.messages.push({ text: response.error, type: "bot" });
          return; // Stop processing further files
        }

        // Preprocess the response to replace invalid JSON values (like NaN)
        const sanitizedResponse = response.replace(/NaN/g, "null");

        // Parse the sanitized JSON response
        const data = JSON.parse(sanitizedResponse);
        if (data.available_credits) {
          // Show floating bubble for available credits
          this.showFloatingBubble(`Available Credits: ${data.available_credits}`);
        }

        // Check if files exist and are an array
        if (data.files && Array.isArray(data.files)) {
          this.files = data.files.map((file) => ({
            fileName: file.file_name,
            data: file.data,
            collapsed: true,
            currentPage: 1, // Initialize pagination
            insights: file.insights, // Add insights
            statistics: file.statistics, // Add statistics
            prompt_suggestions: file.prompt_suggestions,

          }));
        } else {
          console.error("Files property is missing or not an array:", data.files);
          this.messages.push({
            text: "No valid files found in the response. Please try again.",
            type: "bot",
          });
        }
      } catch (error) {
        console.error("Error uploading sample data:", error);
        this.messages.push({
          text: "An error occurred while processing the sample data. Please try again.",
          type: "bot",
        });
      } finally {

        this.loading = false; // End loading

        this.showModal = false;
      }
    },
    async fetchSampleFile() {
      try {
        const response = await fetch("/sample_data.csv");
        if (!response.ok) {
          throw new Error("Failed to fetch sample_data.csv");
        }
        const blob = await response.blob();
        return new File([blob], "sample_data.csv", { type: "text/csv" });
      } catch (error) {
        console.error("Error fetching sample file:", error);
        throw error;
      }
    },
    async uploadData(file, additionalData = {}) {
      try {
        const formData = new FormData();
        formData.append("files", file);
        for (const key in additionalData) {
          formData.append(key, additionalData[key]);
        }
        const response = await axios.post(`${import.meta.env.VITE_API_HOST}/upload`, formData);

        if (response.data.error) {
          return { error: response.data.error }; // Handle errors from the response
        }



        return response.data;
      } catch (error) {
        console.error("Error uploading data:", error);
        throw error;
      }
    },
    toggleCollapse(index) {
      this.files[index].collapsed = !this.files[index].collapsed;
    },
    paginatedData(data, currentPage) {
      const rowsPerPage = 5;
      const start = (currentPage - 1) * rowsPerPage;
      return data.slice(start, start + rowsPerPage);
    },
  },
};
</script>

<style scoped>
.floating-bubbles {
  position: absolute;
  top: 10px;
  /* Position at the top of the chatbox */
  left: 50%;
  transform: translateX(-50%);
  /* Center align */
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bubble {
  background-color: #56a3a6;
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  text-align: center;
  animation: bubble-appear 1.5s ease forwards;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
}

@keyframes bubble-appear {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }

  30% {
    opacity: 1;
    transform: translateY(0);
  }

  90% {
    opacity: 1;
    transform: translateY(-20px);
  }

  100% {
    opacity: 0;
    transform: translateY(-40px);
  }
}



/* Chat Page Layout */
.chat-page {
  position: relative;
  z-index: 1;
  height: 100vh;
  overflow: hidden;
  font-family: "Poppins", sans-serif;
  background-color: #d9e6e7;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  /* Blurred background */
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  animation: fadeIn 0.5s ease-in-out;
  position: relative;
}

.modal-title {
  font-size: 2rem;
  color: #102e4a;
  margin-bottom: 1.5rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.modal-description {
  font-size: 1rem;
  color: #555;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.note {
  color: #56a3a6;
  font-weight: bold;
}

.options {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f8fcfc;
  border: 2px dashed #aaa;
  border-radius: 15px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.option:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  background: #eaf7f7;
  border-color: #56a3a6;
}

.option img {
  width: 60px;
  margin-bottom: 1rem;
}

.option p {
  font-size: 1rem;
  font-weight: 600;
  color: #102e4a;
}

.link {
  color: #56a3a6;
  text-decoration: underline;
  cursor: pointer;
}

/* Header */
.header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem;
  background-color: transparent;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 70px;
}

.app-name {
  font-size: 2rem;
  font-weight: bold;
  color: #102e4a;
  margin: 0;
}

.header-line {
  width: 100%;
  height: 2px;
  background: linear-gradient(to right, #56a3a6, transparent);
  margin-top: 0.5rem;
}
</style>