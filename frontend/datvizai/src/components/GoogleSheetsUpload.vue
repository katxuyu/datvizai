<template>
    <div class="google-sheets-upload">
      <button class="auth-button" @click="handleGoogleAuth" :disabled="loading">
        <img src="@/assets/icons/google-sheets-icon.gif" alt="Google Sheets Icon" />
        <span>Authenticate Google Sheets</span>
      </button>
      <div v-if="authenticated" class="spreadsheet-actions">
        <input
          type="text"
          v-model="spreadsheetId"
          placeholder="Enter Spreadsheet ID"
          class="spreadsheet-input"
        />
        <button class="fetch-data-button" @click="fetchSpreadsheetData" :disabled="!spreadsheetId || loading">
          Fetch Data
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { gapi } from "gapi-script";
  
  export default {
    name: "GoogleSheetsUpload",
    props: {
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        authenticated: false,
        spreadsheetId: "",
        authInstance: null,
      };
    },
    methods: {
      initializeGapi() {
        gapi.load("client:auth2", () => {
          gapi.client
            .init({
              apiKey: "YOUR_API_KEY",
              clientId: "YOUR_CLIENT_ID.apps.googleusercontent.com",
              discoveryDocs: [
                "https://sheets.googleapis.com/$discovery/rest?version=v4",
              ],
              scope: "https://www.googleapis.com/auth/spreadsheets.readonly",
            })
            .then(() => {
              this.authInstance = gapi.auth2.getAuthInstance();
            })
            .catch((error) => console.error("Error initializing GAPI:", error));
        });
      },
      async handleGoogleAuth() {
        if (this.authInstance) {
          try {
            await this.authInstance.signIn();
            this.authenticated = true;
            this.$emit("auth-success");
          } catch (error) {
            console.error("Google authentication error:", error);
          }
        }
      },
      async fetchSpreadsheetData() {
        if (!this.authenticated || !this.spreadsheetId) {
          console.error("Not authenticated or spreadsheet ID missing");
          return;
        }
        this.$emit("loading", true);
        try {
          const response = await gapi.client.sheets.spreadsheets.values.get({
            spreadsheetId: this.spreadsheetId,
            range: "Sheet1!A1:D10", // Adjust range as needed
          });
          this.$emit("data-fetched", response.result.values);
        } catch (error) {
          console.error("Error fetching spreadsheet data:", error);
          this.$emit("fetch-error", error);
        } finally {
          this.$emit("loading", false);
        }
      },
    },
    mounted() {
      this.initializeGapi();
    },
  };
  </script>
  
  <style scoped>
  .google-sheets-upload {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  .auth-button {
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .auth-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .spreadsheet-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .spreadsheet-input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 5px;
    width: 100%;
    max-width: 300px;
  }
  .fetch-data-button {
    background-color: #34a853;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    cursor: pointer;
  }
  .fetch-data-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  </style>
  