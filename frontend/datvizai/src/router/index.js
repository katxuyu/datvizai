import { createRouter, createWebHistory } from "vue-router";
import LandingPage from "@/views/LandingPage.vue";
import ChatPage from "@/views/ChatPage.vue";
import NotFound from "@/views/NotFound.vue"; // Import the 404 component

const routes = [
  {
    path: "/",
    name: "LandingPage",
    component: LandingPage,
  },
  {
    path: "/chat",
    name: "ChatPage",
    component: ChatPage,
    meta: {
      requiresAuth: true, // Protect this route
    },
  },
  {
    path: "/:catchAll(.*)", // Catch-all route for undefined paths
    name: "NotFound",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route Guard for Authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("userAuthenticated");
  const userStatus = localStorage.getItem("userStatus"); // "Existing" or "New"
  if (to.meta.requiresAuth) {
    if (!isAuthenticated || userStatus === "New") {
      // Redirect to Landing Page if not authenticated or new user
      next({ name: "LandingPage" });
    } else {
      next(); // Proceed to ChatPage if authenticated
    }
  } else {
    next(); // Allow access to non-authenticated routes
  }
});

export default router;
