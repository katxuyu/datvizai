<template>
  <div class="pagination-controls">
    <!-- First Page Button -->
    <button
      class="pagination-button"
      :disabled="currentPage === 1"
      @click="goToPage(1)"
    >
      «
    </button>

    <!-- Previous Page Button -->
    <button
      class="pagination-button"
      :disabled="currentPage === 1"
      @click="goToPage(currentPage - 1)"
    >
      ‹
    </button>

    <!-- Page Numbers -->
    <button
      v-for="page in visiblePages"
      :key="page"
      class="pagination-button"
      :class="{ active: page === currentPage }"
      @click="goToPage(page)"
    >
      {{ page }}
    </button>

    <!-- Next Page Button -->
    <button
      class="pagination-button"
      :disabled="currentPage === totalPages"
      @click="goToPage(currentPage + 1)"
    >
      ›
    </button>

    <!-- Last Page Button -->
    <button
      class="pagination-button"
      :disabled="currentPage === totalPages"
      @click="goToPage(totalPages)"
    >
      »
    </button>

    <!-- Total Items Display -->
    <span class="pagination-info">
      {{ startItem }}-{{ endItem }} of {{ totalItems }} items
    </span>
  </div>
</template>

<script>
export default {
  name: "Pagination",
  props: {
    totalItems: {
      type: Number,
      required: true,
    },
    rowsPerPage: {
      type: Number,
      default: 5,
    },
    currentPage: {
      type: Number,
      required: true,
    },
  },
  emits: ["update:currentPage"],
  computed: {
    totalPages() {
      return Math.ceil(this.totalItems / this.rowsPerPage);
    },
    visiblePages() {
      const delta = 2;
      const start = Math.max(1, this.currentPage - delta);
      const end = Math.min(this.totalPages, this.currentPage + delta);
      const pages = [];
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    },
    startItem() {
      return (this.currentPage - 1) * this.rowsPerPage + 1;
    },
    endItem() {
      return Math.min(this.currentPage * this.rowsPerPage, this.totalItems);
    },
  },
  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.$emit("update:currentPage", page);
      }
    },
  },
};
</script>

<style scoped>
.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-family: Arial, sans-serif;
}

.pagination-button {
  padding: 0.5rem 1rem;
  border: 1px solid #d0d0d0;
  background-color: #ffffff;
  color: #555;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.pagination-button:hover {
  background-color: #007bff;
  color: #ffffff;
}

.pagination-button:disabled {
  background-color: #f0f0f0;
  color: #999;
  cursor: not-allowed;
}

.pagination-button.active {
  background-color: #007bff;
  color: #ffffff;
  font-weight: bold;
}

.pagination-info {
  margin-left: 1rem;
  font-size: 0.9rem;
  color: #555;
}
</style>
