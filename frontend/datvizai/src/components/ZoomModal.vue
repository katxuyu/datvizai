<template>
    <div class="zoom-modal-overlay">
        <div class="zoom-modal">
            <!-- Close Button -->
            <button class="close-button" @click="$emit('close')">&times;</button>

            <!-- Modal Title -->
            <h2 class="modal-title">{{ file.fileName }}</h2>

            <!-- Insights and Statistics -->
            <div class="info-section">
                <h3>Insights</h3>
                <p>{{ file.insights }}</p>

                <h3>Variable Types</h3>
                <ul class="variable-types-list">
                    <li v-for="(type, column) in file.statistics.variable_types" :key="column"
                        :title="`${column} : ${type}`">
                        <span class="variable-name">{{ column }}</span>
                        <span class="variable-type">{{ type }}</span>
                    </li>
                </ul>
                <!-- Statistics Section Wrapper -->
                <div class="statistics-section">
                    <h3>Statistics</h3>
                    <ul class="statistics-list">
                        <li><strong>Total Observations:</strong> {{ file.statistics.num_observations }}</li>
                        <li><strong>Total Columns:</strong> {{ file.statistics.num_columns }}</li>
                        <li><strong>Missing Values:</strong> {{ file.statistics.missing_values }}</li>
                    </ul>
                </div>
            </div>




            <!-- Filters Section -->
            <div class="filters-section">
                <div class="dynamic-filter-container">
                    <label class="filter-label">Filter:</label>
                    <select v-model="selectedColumn" class="column-selector" @change="applyFilters">
                        <option disabled value="">Select a column to filter</option>
                        <option v-for="(key, idx) in Object.keys(file.data[0])" :key="idx" :value="key">
                            {{ key }}
                        </option>
                    </select>

                    <select v-if="selectedColumn && conditions[variableTypes[selectedColumn]]"
                        v-model="selectedCondition" class="condition-selector" @change="applyFilters">
                        <option disabled value="">Select a condition</option>
                        <option v-for="condition in conditions[variableTypes[selectedColumn]]" :key="condition"
                            :value="condition">
                            {{ condition }}
                        </option>
                    </select>

                    <input v-if="selectedColumn && selectedCondition && variableTypes[selectedColumn] !== 'datetime'"
                        v-model="columnFilters[selectedColumn]" type="text" class="dynamic-filter-input"
                        @input="applyFilters" />

                    <VueDatePicker v-if="variableTypes[selectedColumn] === 'datetime'" v-model="dateFilterRange" range
                        @change="applyFilters" class="date-range-picker" />
                </div>
                <!-- Clear Filters Button -->
<div class="clear-filters-container" v-if="hasActiveFilters">
  <button class="clear-filters-button" @click="clearFilters">Clear Filters</button>
</div>

            </div>

            <!-- Floating Scrollbar -->
            <div class="scrollbar-container">
                <div class="floating-scrollbar" ref="scrollbar" @scroll="syncScroll">
                    <div class="scroll-content" ref="scrollContent"></div>
                </div>
            </div>

            <!-- Table -->
            <div class="table-container">
                <div class="table-scroll" ref="tableScroll" @scroll="syncScroll">
                    <table>
                        <thead>
                            <tr>
                                <th v-for="(key, idx) in Object.keys(file.data[0])" :key="idx">
                                    {{ key }}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, rowIndex) in filteredData" :key="rowIndex">
                                <td v-for="(value, colIndex) in Object.values(row)" :key="colIndex">
                                    {{ value }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

export default {
    name: "ZoomModal",
    components: {
        VueDatePicker,
    },
    props: {
        file: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            selectedColumn: "",
            selectedCondition: "",
            columnFilters: {},
            dateFilterRange: [],
            variableTypes: {},
            conditions: {
                string: ["contains", "equals", "starts with"],
                int64: ["equals", ">", "<"],
                float64: ["equals", ">", "<"],
                datetime: ["range"],
            },
        };
    },
    computed: {
        hasActiveFilters() {
    // Check if any column filter is active
    const isColumnFiltered = Object.keys(this.columnFilters).some(
      (key) => this.columnFilters[key]
    );

    // Check if date filter range is active
    const isDateRangeFiltered =
      Array.isArray(this.dateFilterRange) && this.dateFilterRange.length === 2;

    // Return true if any filter (column or date range) is active
    return (
      this.selectedColumn ||
      this.selectedCondition ||
      isColumnFiltered ||
      isDateRangeFiltered
    );
  },
        filteredData() {
            let data = this.file.data;

            // Apply Filters
            if (this.selectedColumn && this.selectedCondition) {
                data = data.filter((row) => {
                    const value = row[this.selectedColumn];
                    const filterValue = this.columnFilters[this.selectedColumn] || "";

                    switch (this.selectedCondition) {
                        case "contains":
                            return String(value).toLowerCase().includes(filterValue.toLowerCase());
                        case "equals":
                            return String(value).toLowerCase() === filterValue.toLowerCase();
                        case "starts with":
                            return String(value).toLowerCase().startsWith(filterValue.toLowerCase());
                        case ">":
                            return parseFloat(value) > parseFloat(filterValue);
                        case "<":
                            return parseFloat(value) < parseFloat(filterValue);
                        case "range":
                            if (Array.isArray(this.dateFilterRange) && this.dateFilterRange.length === 2) {
                                const [startDate, endDate] = this.dateFilterRange;
                                return (
                                    new Date(value) >= new Date(startDate) &&
                                    new Date(value) <= new Date(endDate)
                                );
                            }
                            return true;
                        default:
                            return true;
                    }
                });
            }

            return data;
        },
    },
    mounted() {
        if (this.file.statistics && this.file.statistics.variable_types) {
            this.variableTypes = this.file.statistics.variable_types;
        }
    },
    methods: {
        applyFilters() {
            this.filteredData;
        },
        clearFilters() {
            this.selectedColumn = "";
            this.selectedCondition = "";
            this.columnFilters = {};
            this.dateFilterRange = [];
        },
        syncScroll() {
            const tableScroll = this.$refs.tableScroll;
            const scrollbar = this.$refs.scrollbar;
            scrollbar.scrollLeft = tableScroll.scrollLeft;
            this.$refs.scrollContent.style.width = `${tableScroll.scrollWidth}px`;
        },
    },
};
</script>

<style scoped>
.clear-filters-container {
    margin-top: 1rem;
    display: flex;
    justify-content: flex-end;
}

.clear-filters-button {
    background-color: #ff4d4d;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

.clear-filters-button:hover {
    background-color: #ff1a1a;
}

/* Modal Overlay */
.zoom-modal-overlay {
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
}

/* Modal Container */
.zoom-modal {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    max-width: 90%;
    max-height: 90%;
    overflow-y: auto;
    position: relative;
    display: flex;
    flex-direction: column;
}

/* Close Button */
.close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #333;
}

/* Modal Title */
.modal-title {
    font-size: 1.8rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #102e4a;
}

/* Info Section */
.info-section {
    margin-bottom: 1.5rem;
    background: #f9fafb;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.info-section h3 {
    font-size: 1.2rem;
    font-weight: bold;
    color: #102e4a;
    margin-bottom: 0.5rem;
}

.info-section p {
    color: #555;
    font-size: 1rem;
    margin-bottom: 2rem;
    line-height: 1.5;
}

/* Statistics Section Styling */
.statistics-section {
    margin-top: 2rem;
    /* Adds spacing between the variable types and statistics */
}

.statistics-list {
    margin-top: 1rem;
    padding: 0;
    list-style: none;
}

.statistics-list li {
    font-size: 1rem;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.statistics-list li strong {
    color: #102e4a;
    font-weight: 600;
}


/* Filters Section */
.filters-section {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.dynamic-filter-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
}

.column-selector,
.condition-selector {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
    max-width: 150px;
}

/* Label for Filter Dropdown */
.filter-label {
  font-size: 1rem;
  color: #34495e;
  margin-right: 0.5rem;
  font-weight: bold;
  align-self: center;
}

.dynamic-filter-input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
}

.date-range-picker {
    max-width: 300px;
}

.column-selector {
    min-width: 150px;
    flex: 1;
}

/* Table Container */
.table-container {
    background: #f9fafb;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    position: relative;
}

.table-scroll {
    overflow-y: visible;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    color: #333;
}

th,
td {
    padding: 0.75rem;
    border: 1px solid #ddd;
    text-align: left;
}

th {
    background-color: #56a3a6;
    color: white;
    font-weight: bold;
}

td {
    background-color: #ffffff;
}

.variable-types-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, max-content));
    /* Dynamically adjust size */
    gap: 1rem;
    justify-content: center;
    /* Center the grid */
}

.variable-types-list li {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    background-color: #ffffff;
    border: 1px solid #dfe6e9;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    font-size: 0.85rem;
    color: #2d3436;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
    position: relative;
    white-space: nowrap;
    /* Prevent wrapping of text */
    text-align: center;
}

.variable-types-list li:hover {
    transform: scale(1.1);
    /* Slight zoom effect */
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    z-index: 10;
    background-color: #f7f7f7;
}

.variable-name,
.variable-type {
    font-size: 0.9rem;
    /* Adjust text size */
}

.variable-name {
    font-weight: bold;
    color: #34495e;
}

.variable-type {
    font-style: italic;
    color: #7f8c8d;
}

/* Tooltip for extra long content */
.variable-types-list li:hover::after {
    content: attr(title);
    position: absolute;
    bottom: -1.5rem;
    left: 50%;
    transform: translateX(-50%);
    background: #2d3436;
    color: white;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border-radius: 4px;
    white-space: nowrap;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    z-index: 15;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.variable-types-list li:hover::after {
    opacity: 1;
}
</style>
