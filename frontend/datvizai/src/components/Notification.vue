<template>
    <div v-if="visible" class="notification" :class="[type]">
      <div class="notification-content">
        <p>{{ message }}</p>
        <button class="close-btn" @click="closeNotification">×</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "Notification",
    props: {
      message: {
        type: String,
        required: true,
      },
      type: {
        type: String,
        default: "success", // Types: success, error
      },
      duration: {
        type: Number,
        default: 5000, // Duration in milliseconds
      },
    },
    data() {
      return {
        visible: false,
      };
    },
    mounted() {
      this.showNotification();
    },
    methods: {
      showNotification() {
        this.visible = true;
        setTimeout(() => {
          this.closeNotification();
        }, this.duration);
      },
      closeNotification() {
        this.visible = false;
        this.$emit("dismiss");
      },
    },
  };
  </script>
  
  <style scoped>
  .notification {
    position: fixed;
    top: 1.5rem;
    right: 1.5rem;
    z-index: 1000;
    max-width: 350px;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    color: #fff;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.4s ease-out, fadeOut 0.5s ease-in 4.5s;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .notification.success {
    background-color: #56a3a6; /* Teal Theme Color */
  }
  
  .notification.error {
    background-color: #f44336; /* Error Red */
  }
  
  .notification-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    width: 100%;
  }
  
  .close-btn {
    background: transparent;
    border: none;
    font-size: 1.4rem;
    font-weight: bold;
    color: #fff;
    cursor: pointer;
    padding: 0.2rem;
  }
  
  .close-btn:hover {
    color: #d9e6e7; /* Lighter color on hover */
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes fadeOut {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }
  </style>
  