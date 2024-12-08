import './assets/main.css';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all.js';



import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // Import the router

// Vuetify imports
import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // Import Vuetify styles
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// Create Vuetify instance with Material Design Icons
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi', // Use Material Design Icons
  },
});

createApp(App).use(router).use(vuetify).mount('#app');
