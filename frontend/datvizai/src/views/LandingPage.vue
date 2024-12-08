<template>
  <div>
    <Header />
    <MainContent />
    <Footer />
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import MainContent from "@/components/MainContent.vue";
import Footer from "@/components/Footer.vue";

export default {
  name: "LandingPage",
  components: { Header, MainContent, Footer },
};
</script>
