<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <!-- Close Button -->
      <button
        class="close-button"
        :disabled="loading || closeButtonDisabled"
        @click="$emit('close')"
      >
        &times;
      </button>

      <h2 class="modal-title">Get Started with Your Data</h2>
      <p class="modal-description">
        Please choose one of the following options to upload your data. <br />
        <span class="note">Only CSV files are allowed (Max: 500MB).</span>
      </p>

      <div class="options">
        <!-- Local File Upload -->
        <div class="option dashed" @click="triggerFileUpload" :class="{ disabled: loading }">
          <img v-if="!loading" src="@/assets/icons/folder-icon.gif" alt="Folder Icon" />
          <div v-else class="loading-spinner"></div>
          <p>Drop CSV here or <span class="link">browse</span></p>
        </div>

        <!-- Hidden File Input -->
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept=".csv"
          multiple
          @change="handleFileUpload"
        />

        <!-- Google Sheets Option -->
        <div class="option dashed" @click="handleGoogleSheet" :class="{ disabled: loading }">
          <img v-if="!loading" src="@/assets/icons/google-sheets-icon.gif" alt="Google Sheets Icon" />
          <div v-else class="loading-spinner"></div>
          <p>Use Google Sheets</p>
        </div>

        <!-- Sample Data Option -->
        <div class="option dashed" @click="handleSampleData" :class="{ disabled: loading }">
          <img v-if="!loading" src="@/assets/icons/sample-data-icon.gif" alt="Sample Data Icon" />
          <div v-else class="loading-spinner"></div>
          <p>Use Sample Data</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UploadModal",
  props: {
    closeButtonDisabled: {
      type: Boolean,
      default: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    triggerFileUpload() {
      if (!this.loading) {
        this.$refs.fileInput.click();
      }
    },
    handleFileUpload(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        this.$emit("upload-local-file", files);
      } else {
        console.error("No files selected.");
        alert("Please select valid CSV files to upload.");
      }
    },
    handleGoogleSheet() {
      if (!this.loading) {
        this.$emit("use-google-sheet");
      }
    },
    handleSampleData() {
      if (!this.loading) {
        this.$emit("use-sample-data");
      }
    },
  },
};
</script>

<style scoped>
/* Modal Overlay */
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
  backdrop-filter: blur(8px); /* Blurred background */
}

/* Modal Content */
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
  font-size: 1rem;
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

/* Close Button */
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #102e4a;
  cursor: pointer;
  transition: color 0.2s ease;
  opacity: 0.8;
}

.close-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.close-button:hover:enabled {
  color: #56a3a6;
}

/* Options */
.options {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap; /* Make buttons stack on small screens */
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
  min-width: 150px; /* Ensure buttons don’t shrink too small */
  max-width: 200px; /* Cap button width */
}

.option.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.option:hover:not(.disabled) {
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

/* Loading Spinner */
.loading-spinner {
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #56a3a6;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .modal-content {
    padding: 2rem;
    font-size: 0.9rem;
  }

  .modal-title {
    font-size: 1.5rem;
  }

  .modal-description {
    font-size: 0.85rem;
  }

  .option {
    padding: 1rem;
    max-width: 100%; /* Allow buttons to take full width */
  }

  .option p {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .modal-content {
    padding: 1rem;
    font-size: 0.8rem;
  }

  .modal-title {
    font-size: 1.2rem;
  }

  .modal-description {
    font-size: 0.75rem;
  }

  .option {
    padding: 0.75rem;
  }

  .option p {
    font-size: 0.75rem;
  }
}
</style>
