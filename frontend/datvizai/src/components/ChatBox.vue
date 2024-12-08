<template>
    <div class="chat-container">
        <!-- Processing Spinner -->
        <div v-if="isProcessing" class="processing-overlay">
            <div class="spinner"></div>
            <p class="processing-text">Processing...</p>
        </div>
        <!-- Collapsible Tables Section -->
        <div class="collapsible-section">
            <div v-if="!containerCollapsed">
                <div v-for="(file, index) in files" :key="index" class="collapsible-table">
                    <button @click="handleTableClick(index, file)" class="collapsible-button">
                        <div class="collapsible-title">
                            <div class="title-and-info">
                                <span class="file-name">{{ file.fileName }}</span>
                                <div class="info-icon-container" @mouseover="hoveredIndex = index"
                                    @mouseleave="hoveredIndex = null">
                                    <v-icon class="info-icon">mdi-information</v-icon>
                                    <div v-if="hoveredIndex === index" class="tooltip">
                                        <div class="tooltip-content">
                                            <h3 class="tooltip-title">Insights</h3>
                                            <p class="tooltip-paragraph">{{ file.insights }}</p>
                                            <h3 class="tooltip-title">Statistics</h3>
                                            <ul class="statistics-list">
                                                <li>Total Observations: {{ file.statistics.num_observations }}</li>
                                                <li>Total Columns: {{ file.statistics.num_columns }}</li>
                                                <li>Missing Values: {{ file.statistics.missing_values }}</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <v-icon class="collapsible-icon">
                            {{ file.collapsed ? "mdi-chevron-down" : "mdi-chevron-up" }}
                        </v-icon>
                    </button>

                    <div v-if="!file.collapsed && file.data && file.data.length > 0" class="table-container">
                        <!-- Table Actions -->
                        <div class="table-actions">
                            <div class="spacer"></div>
                            <button @click="zoomTable(file)" class="table-action-button">
                                <v-icon>mdi-magnify</v-icon> Zoom
                            </button>
                            <button @click="downloadTable(file)" class="table-action-button">
                                <v-icon>mdi-download</v-icon> Download
                            </button>
                        </div>

                        <!-- Table Content -->
                        <table>
                            <thead>
                                <tr>
                                    <th v-for="(key, idx) in Object.keys(file.data[0])" :key="idx">
                                        {{ key }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(row, rowIndex) in paginatedData(file.data, file.currentPage)"
                                    :key="rowIndex">
                                    <td v-for="(value, colIndex) in Object.values(row)" :key="colIndex">
                                        {{ value }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                        <!-- Pagination -->
                        <Pagination v-if="file.currentPage" :totalItems="file.data.length" :rowsPerPage="5"
                            v-model:currentPage="file.currentPage" />
                    </div>
                </div>
            </div>
            <!-- Arrow Buttons -->
            <div class="arrow-buttons">
                <button @click="toggleContainerCollapse" @mouseover="showButtonTooltip = true"
                    @mouseleave="showButtonTooltip = false" class="floating-arrow-button">
                    <v-icon>{{ containerCollapsed ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
                </button>
                <div v-if="showButtonTooltip" class="button-tooltip">
                    {{ containerCollapsed ? "Show Tables" : "Hide Tables" }}
                </div>
            </div>



        </div>
        <!-- Render bubbles slot -->
  <slot name="bubbles"></slot>
        <!-- Chat Messages -->
        <div class="chat-messages" ref="chatMessages">


            <!-- Suggestion Bubbles -->
            <div class="prompt-suggestions">
                <div v-for="(suggestion, index) in suggestions" :key="index"
                    :class="['suggestion-bubble', { disappearing: clickedIndex === index }]"
                    @click="handleSuggestionClick(index)">
                    {{ suggestion }}
                </div>
            </div>

            <!-- Existing Chat Messages -->
            <div v-for="(message, index) in messages" :key="index" :class="['chat-message', message.type]">
                <div v-if="message.type === 'bot'" class="message-container bot">
                    <img src="@/assets/icons/bot-icon.gif" alt="Bot Icon" class="chat-icon bot-icon" />
                    <div class="chat-bubble bot">
                        <p>{{ message.text }}</p>
                    </div>
                </div>

                <div v-if="message.type === 'user'" class="message-container user">
                    <div class="chat-bubble user">
                        <p>{{ message.text }}</p>
                    </div>
                    <img src="@/assets/icons/user-icon.gif" alt="User Icon" class="chat-icon user-icon" />
                </div>
                <!-- Error Suggestions -->
                <div v-if="index === messages.length - 1 && errorSuggestions.length > 0" class="error-suggestions">
                    <div v-for="(suggestion, index) in errorSuggestions" :key="index"
                        :class="['suggestion-bubble', { disappearing: clickedErrorIndex === index }]"
                        @click="handleErrorSuggestionClick(index)">
                        {{ suggestion }}
                    </div>
                </div>
                <div v-if="message.type === 'graph'" class="graph-container">
                    <!-- Zoom Button -->
                    <button class="graph-zoom-button" @click="zoomGraph(message.id)">
                        <v-icon>mdi-fullscreen</v-icon>
                    </button>
                    <!-- Graph -->
                    <div :id="`graph-${message.id}`" class="graph" style="width: 100%; height: 350px;"></div>

                    <!-- Modal for Zoomed Graph -->
                    <div v-if="zoomedGraphId === message.id" class="zoom-modal">
                        <div class="zoom-content">
                            <button class="close-button" @click="zoomedGraphId = null">✕</button>
                            <div :id="`zoomed-graph-${message.id}`" class="graph" style="width: 100%; height: 500px;">
                            </div>
                        </div>
                    </div>
                </div>


            </div>

        </div>


        <!-- Chat Input -->
        <div class="chat-input">
            <v-textarea :model-value="userMessage" placeholder="Type your message..." outlined rows="1"
                :auto-grow="true" ref="messageInput" class="chat-textarea"
                :disabled="isProcessing || isTextareaDisabled" prepend-inner-icon="mdi-paperclip"
                append-inner-icon="mdi-send" @keydown="handleKeyDown" @click:prepend-inner="$emit('trigger-modal')"
                @click:append-inner="sendMessage"
                @update:model-value="$emit('update:userMessage', $event)"></v-textarea>
        </div>


        <!-- Zoom Modal -->
        <ZoomModal v-if="zoomedFile" :file="zoomedFile" @close="zoomedFile = null" />
    </div>
</template>

<script>
import Pagination from "@/components/Pagination.vue";
import ZoomModal from "@/components/ZoomModal.vue";
import Plotly from 'plotly.js-dist';


export default {
    components: {
        Pagination,
        ZoomModal,
    },
    name: "ChatBox",
    props: {
        messages: {
            type: Array,
            required: true,
            default: () => [], // Default value to ensure `messages` is always an array
        },
        files: {
            type: Array,
            required: true,
            default: () => [],
        },
        userMessage: {
            type: String,
            required: true,
        },
        graphs: { // Add this prop to receive the graphs
            type: Array,
            required: true,
            default: () => [],
        },
        isProcessing: { // Add this prop
            type: Boolean,
            required: true,
            default: false,
        },
        errorSuggestions: {
            type: Array,
            required: true,
            default: () => [], // Default empty array
        },
        isTextareaDisabled: {
            type: Boolean,
            required: true,
            default: false, // Default to false if not specified
        },
    },
    data() {
        return {
            containerCollapsed: false,
            hoveredIndex: null,
            zoomedFile: null,
            containerCollapsed: true,
            showButtonTooltip: false,
            clickedIndex: null,
            isFullScreen: {},
            zoomedGraphId: null,

        };
    },
    emits: ["trigger-modal", "send-message", "toggle-collapse", "update:userMessage"],
    computed: {
        suggestions() {
            return this.getPromptSuggestions();
        }
    },
    methods: {
        getPromptSuggestions() {
            // Collect all prompt suggestions from files
            return this.files.flatMap((file) => file.prompt_suggestions || []).slice(0, 5); // Limit to 5 suggestions
        },
        handleErrorSuggestionClick(index) {
            this.clickedErrorIndex = index; // Mark the bubble as clicked
            setTimeout(() => {
                this.errorSuggestions.splice(index, 1); // Remove the clicked suggestion
                this.clickedErrorIndex = null; // Reset after animation
            }, 200); // Match the duration of the pop animation
            this.sendErrorSuggestion(this.errorSuggestions[index]); // Emit the suggestion
        },
        sendErrorSuggestion(suggestion) {
            if (suggestion) {
                this.$emit("send-message", suggestion); // Emit the suggestion as a message
            }
        },
        handleSuggestionClick(index) {
            this.clickedIndex = index; // Mark the bubble as clicked
            setTimeout(() => {
                this.suggestions.splice(index, 1); // Remove the clicked suggestion
                this.clickedIndex = null; // Reset after animation
            }, 200); // Match the duration of the pop animation
            this.sendSuggestion(this.suggestions[index]); // Emit the suggestion
        },
        sendSuggestion(suggestion) {
            if (suggestion) {
                this.$emit("send-message", suggestion); // Emit the suggestion text
            }
        },
        paginatedData(data, currentPage) {
            const rowsPerPage = 5;
            const start = (currentPage - 1) * rowsPerPage;
            return data.slice(start, start + rowsPerPage);
        },
        toggleContainerCollapse() {
            this.containerCollapsed = !this.containerCollapsed;
        },
        handleKeyDown(event) {
            if (event.key === "Enter") {
                if (event.shiftKey) {
                    event.preventDefault();
                    // Add a new line while ensuring reactivity
                    const updatedMessage = `${this.userMessage}\n`;
                    this.$emit("update:userMessage", updatedMessage);
                } else {
                    event.preventDefault();
                    this.sendMessage();
                }
            }
        },
        sendMessage() {
            if (this.userMessage.trim() !== "") {
                this.$emit("send-message", this.userMessage);
                this.$emit("update:userMessage", ""); // Clear the input after sending
            }
        },
        handleTableClick(index, file) {
            if (this.files.length > 2) {
                this.zoomedFile = file; // Open zoom modal if more than 2 files
            } else {
                this.$emit("toggle-collapse", index); // Collapse or expand table
            }
        },
        zoomTable(file) {
            this.zoomedFile = file; // Open the zoom modal with the file data
        },
        downloadTable(file) {
            const csvContent = this.convertToCSV(file.data);
            const blob = new Blob([csvContent], { type: "text/csv" });
            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", `${file.fileName}`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },
        convertToCSV(data) {
            const headers = Object.keys(data[0]);
            const rows = data.map((row) => headers.map((header) => `"${row[header]}"`).join(","));
            return [headers.join(","), ...rows].join("\n");
        },
        sendPrompt(prompt) {
            // Sends the clicked prompt as a message
            this.$emit("send-message", prompt);
        },
        scrollToBottom() {
            const chatMessages = this.$refs.chatMessages;
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        },
        toggleFullScreen(graphId, buttonId) {
            const graphContainer = document.getElementById(graphId);
            const isFullScreenActive = this.isFullScreen[graphId];

            if (graphContainer) {
                if (!isFullScreenActive) {
                    // Enter full-screen mode
                    graphContainer.requestFullscreen()
                        .then(() => {
                            this.$set(this.isFullScreen, graphId, true); // Update state
                        })
                        .catch((err) => console.error(`Error entering full-screen mode: ${err.message}`));
                } else {
                    // Exit full-screen mode
                    document.exitFullscreen()
                        .then(() => {
                            this.$set(this.isFullScreen, graphId, false); // Update state
                        })
                        .catch((err) => console.error(`Error exiting full-screen mode: ${err.message}`));
                }
            } else {
                console.error(`Graph container with ID ${graphId} not found.`);
            }
        },
        zoomGraph(graphId) {
            this.zoomedGraphId = graphId; // Set the zoomed graph ID
            this.$nextTick(() => {
                const graphContainer = document.getElementById(`zoomed-graph-${graphId}`);
                const originalGraph = document.getElementById(`graph-${graphId}`);

                if (graphContainer && originalGraph) {
                    // Clone the graph data and layout
                    const graphData = originalGraph.data;
                    const graphLayout = {
                        ...originalGraph.layout,
                        autosize: true,
                        width: graphContainer.offsetWidth,
                        height: graphContainer.offsetHeight,
                    };

                    // Render in modal
                    Plotly.newPlot(graphContainer, graphData, graphLayout);
                }
            });
        },
    },
    watch: {
        messages: {
            deep: true,
            handler(newMessages) {
                this.$nextTick(() => {
                    newMessages.forEach((message) => {
                        if (message.type === 'graph' && message.graphData) {
                            const graphContainer = document.getElementById(`graph-${message.id}`);
                            if (graphContainer && !graphContainer.hasChildNodes()) {
                                // Define Plotly configuration
                                const config = {
                                    responsive: true, // Make the graph responsive
                                    displaylogo: false, // Hide the Plotly logo
                                    modeBarButtonsToAdd: ["toggleSpikelines", "resetViews", "zoom2d", "pan2d", "zoomIn2d", "zoomOut2d"],
                                    modeBarButtonsToRemove: ["lasso2d", "select2d"],
                                    displayModeBar: true, // Always show the mode bar
                                    modebar: {
                                        orientation: 'h', // Horizontal mode bar
                                        xanchor: 'right', // Align to right
                                        yanchor: 'top', // Align to bottom
                                        x: 1, // Full width
                                        y: 0 // Bottom position
                                    }
                                };

                                // Render the graph
                                Plotly.newPlot(graphContainer, message.graphData.data, message.graphData.layout, config);
                            }
                        }
                    });

                    // Scroll to the bottom after updating messages
                    this.scrollToBottom();
                });
            },
        },
    }


};
</script>




<style scoped>
.processing-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    /* Center vertically */
    z-index: 1000;
}

.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 5;
    /* Ensure it appears above other chatbox content */
    border-radius: inherit;
    /* Match the chatbox's border radius */
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #ccc;
    /* Light border */
    border-top: 5px solid #56a3a6;
    /* Highlighted spinning part */
    border-radius: 50%;
    animation: spin 1s linear infinite;
    /* Continuous rotation */
}

.processing-text {
    margin-top: 1rem;
    /* Space between spinner and text */
    font-size: 1.2rem;
    font-weight: bold;
    color: #555;
    /* Neutral gray */
    text-align: center;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.loading-text {
    margin-top: 1rem;
    font-size: 1.2rem;
    color: #555;
}

.processing-text {
    margin-top: 1rem;
    /* Space between spinner and text */
    font-size: 1.5rem;
    /* Larger font size */
    font-weight: bold;
    color: #555;
    /* Neutral gray color */
    text-align: center;
    /* Center text */
}

/* Full-Page Graph Container */
.full-page-graph {
    width: 100%;
    /* Full width */
    height: 100%;
    /* Full height */
    position: relative;
}



.fullscreen-toggle-button {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    border: none;
    border-radius: 50%;
    color: white;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.fullscreen-toggle-button:hover {
    background-color: rgba(0, 0, 0, 0.9);
    transform: scale(1.1);
}

.fullscreen-toggle-button:active {
    transform: scale(0.95);
}

.fullscreen-icon {
    font-size: 1.5rem;
    color: #56a3a6;
    cursor: pointer;
    margin-top: 10px;
    transition: color 0.3s ease;
}

.fullscreen-icon:hover {
    color: #469093;
}

.fullscreen-icon:active {
    color: #38787b;
}


/* Graph Container */
.graph-container {
    margin-top: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    /* For positioning zoom button */
}

/* Zoom Button */
.graph-zoom-button {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.graph-zoom-button:hover {
    background-color: rgba(0, 0, 0, 0.9);
    transform: scale(1.1);
}

/* Full-Page Modal Overlay */
.zoom-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.9);
    /* Darker background for focus */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 0;
    /* Remove padding for fullscreen effect */
}

/* Modal Content */
.zoom-content {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    max-width: 90%;
    width: 800px;
    position: relative;
}

.close-button {
    position: absolute;
    top: 20px;
    /* Adjust spacing */
    right: 20px;
    /* Adjust spacing */
    background: none;
    border: none;
    font-size: 2rem;
    /* Larger font size for visibility */
    color: white;
    /* White color to contrast with background */
    cursor: pointer;
    z-index: 1001;
    /* Ensure it stays above the graph */
    transition: color 0.3s ease;
}

.close-button:hover {
    color: #ff6666;
    /* Highlight on hover */
}



/* Suggestions Container */
.prompt-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    /* Space between bubbles */
    justify-content: center;
    margin-bottom: 1.5rem;
    padding: 0 1rem;
    /* Match chatbox padding */
    max-width: 100%;
    /* Ensure it doesn't exceed the container */
}

.error-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 1.5rem;
}

/* Rounded Box Bubble */
.suggestion-bubble {
    background-color: #d9f2f9;
    /* Light blue for a calm, modern theme */
    color: #004d66;
    /* Dark teal for readable contrast */
    padding: 0.4rem 1rem;
    /* Smaller padding for compact look */
    border-radius: 10px;
    /* Rounded corners for aesthetic effect */
    font-size: 0.85rem;
    /* Smaller font size */
    font-weight: 400;
    /* Slightly lighter font for cleaner look */
    cursor: pointer;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
    /* Subtle shadow */
    transition: transform 0.2s ease, background-color 0.2s ease;
    text-align: center;
    white-space: normal;
    /* Allow text to wrap */
    word-wrap: break-word;
    /* Ensure long words break */
    max-width: 90%;
    /* Limit bubble width to fit chatbox */
    line-height: 1.4;
    /* Adjust for smaller font size */
}

/* Hover Effect */
.suggestion-bubble:hover {
    background-color: #b3e3f2;
    /* Slightly darker blue on hover */
    transform: scale(1.03);
    /* Subtle hover effect */
}

/* Disappear Animation */
.suggestion-bubble.disappearing {
    animation: disappear 0.2s forwards;
    pointer-events: none;
    /* Disable interaction while animating */
}

/* Disappear Keyframes */
@keyframes disappear {
    0% {
        transform: scale(1);
        opacity: 1;
    }

    100% {
        transform: scale(0.9);
        opacity: 0;
    }
}



/* Floating Arrow Button */
.arrow-buttons {
    position: fixed;
    /* Floating at the bottom right */
    bottom: 15px;
    /* Spacing from the bottom */
    right: 15px;
    /* Spacing from the right */
    z-index: 1000;
    /* Ensure it's above all elements */
    display: flex;
    flex-direction: column-reverse;
    /* Tooltip will appear above the button */
    align-items: center;
}

/* Floating Button */
.floating-arrow-button {
    background: #56a3a6;
    /* Default color */
    border: none;
    border-radius: 50%;
    /* Circular shape */
    color: white;
    width: 45px;
    /* Compact size */
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1.2rem;
    /* Icon size */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    /* Subtle shadow */
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.floating-arrow-button:hover {
    background: #469093;
    /* Darker color on hover */
    transform: translateY(-3px);
    /* Upward motion on hover */
}

.floating-arrow-button:active {
    background: #38787b;
    /* Even darker on click */
    transform: scale(0.95);
    /* Slight shrink on click */
}

/* Tooltip for Floating Button */
.button-tooltip {
    margin-bottom: 8px;
    /* Space above the button */
    background-color: #333;
    /* Dark background */
    color: #fff;
    /* White text */
    padding: 5px 10px;
    /* Padding inside tooltip */
    font-size: 0.75rem;
    /* Smaller font size */
    border-radius: 4px;
    /* Rounded edges */
    white-space: nowrap;
    /* Prevent wrapping */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    /* Subtle shadow */
    opacity: 0.9;
    /* Slight transparency */
    text-align: center;
    transition: opacity 0.2s ease, visibility 0.2s ease;
}


.table-actions {
    display: flex;
    justify-content: flex-end;
    /* Align actions to the right */
    align-items: center;
    gap: 1rem;
    /* Spacing between buttons */
    margin-bottom: 1rem;
}

.table-action-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #56a3a6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s ease;
}

.table-action-button:hover {
    background-color: #469093;
}

.table-action-button v-icon {
    font-size: 1.2rem;
}

.spacer {
    flex-grow: 1;
    /* Push buttons to the right */
}

.collapsible-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 10px;
    /* Adjust spacing between title-and-info and collapsible-icon */
}

.title-and-info {
    display: flex;
    /* Group file name and info icon together */
    align-items: center;
    gap: 8px;
    /* Spacing between file name and info icon */
}

.file-name {
    font-weight: bold;
    font-size: 1rem;
    color: #ffffff;
    /* Ensure it matches the button's text color */
}

.info-icon-container {
    display: flex;
    align-items: center;
    position: relative;
}

.info-icon {
    font-size: 1.25rem;
    cursor: pointer;
    color: #ffffff;
}


.tooltip {
    position: absolute;
    top: 40px;
    /* Adjust this for vertical positioning */
    left: 0;
    /* Align to the very left of the screen */
    right: 0;
    /* Stretch the tooltip to the end of the screen */
    margin: 0 auto;
    /* Center the tooltip */
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    padding: 1rem;
    border-radius: 8px;
    width: 95vw;
    /* Take up 95% of the viewport width */
    max-width: 1000px;
    /* Prevent tooltip from being overly large */
    z-index: 1000;
    /* Ensure it stays above other elements */
    white-space: normal;
    /* Allow text wrapping */
    box-sizing: border-box;
}


/* Center the tooltip content */
.tooltip-content {
    max-width: 1200px;
    /* Optional: limit width for readability */
    font-size: 1rem;
    line-height: 1.6;
    color: #333;
    text-align: left;
}

.tooltip-title {
    font-weight: bold;
    color: #333;
    margin-bottom: 0.5rem;
}

.tooltip-paragraph {
    color: #555;
    margin-bottom: 1rem;
}

.statistics-list {
    list-style-type: none;
    padding-left: 0;
    margin: 0;
}

.statistics-list li {
    margin: 0.5rem 0;
    color: #666;
}

.collapsible-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 0px;
}

/* Pagination Controls */
.pagination-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
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

/* Chat Container */
.chat-container {
    max-width: 95%;
    height: 80vh;
    margin: 1rem auto 0 auto;
    display: flex;
    flex-direction: column;
    background: linear-gradient(to bottom, rgba(255, 255, 255, 0.9), white);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    border-top: 4px solid #56a3a6;
    position: relative
}

/* Collapsible Section */
.collapsible-section {
    position: sticky;
    top: 0;
    z-index: 10;
    background-color: #ffffff;
    border-bottom: 1px solid #ddd;
    padding: 0.5rem 1rem;
}

.collapsible-table {
    margin-bottom: 0.5rem;
    position: relative;
}

/* Collapsible Button */
.collapsible-button {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 4px;
    background-color: #56a3a6;
    color: white;
    cursor: pointer;
    position: relative;
    width: 100%;
    font-size: 1rem;
}


.collapsible-button:hover {
    background-color: #469093;
}

.collapsible-icon {
    font-size: 1.2rem;
}

.table-container {
    margin-top: 0.5rem;
    overflow-x: auto;
    background: #ffffff;
    border-radius: 4px;
    padding: 0.5rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.table-container table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.9rem;
}

.table-container th,
.table-container td {
    border: 1px solid #ddd;
    padding: 0.5rem;
}

.table-container th {
    background-color: #f4f4f4;
    font-weight: bold;
}

/* Chat Messages */
.chat-messages {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
    position: relative;
}

/* Chat Input */
.chat-input {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    background-color: #ffffff;
    border-top: 1px solid #e0e0e0;
}

.chat-input textarea {
    flex: 1;
    max-width: 50%;
    min-height: 40px;
    max-height: 80px;
    padding: 0.5rem;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    font-size: 0.9rem;
    font-family: "Poppins", sans-serif;
    resize: none;
    overflow: hidden;
    transition: all 0.3s ease;
}

.chat-input textarea:disabled {
    background: rgba(245, 245, 245, 0.7);
    color: #aaa;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
    cursor: not-allowed;
    filter: blur(1px);
    transition: all 0.3s ease;
}


/* Chat Bubbles */
.message-container {
    display: flex;
    align-items: flex-end;
    margin-bottom: 1rem;
}

.message-container.bot {
    flex-direction: row;
}

.chat-bubble.bot {
    background-color: white;
    color: #102e4a;
    text-align: left;
    border-radius: 12px;
    padding: 1rem;
    max-width: 75%;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    word-wrap: break-word;
    white-space: pre-wrap;
}

.chat-icon.bot-icon {
    margin-right: 0.5rem;
    width: 32px;
    height: 32px;
    border-radius: 50%;
}

.message-container.user {
    display: flex;
    flex-direction: row;
    /* Default direction: bubble on the left, icon on the right */
    justify-content: flex-end;
    /* Align content to the right */
    align-items: flex-end;
}

.chat-bubble.user {
    background: linear-gradient(90deg, rgba(229, 231, 235, 0.8), #e5e7eb);
    color: #102e4a;
    text-align: left;
    border-radius: 12px;
    padding: 1rem;
    max-width: 75%;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    word-wrap: break-word;
    white-space: pre-wrap;
    margin-right: 0.5rem;
    /* Add spacing between bubble and icon */
}

.chat-icon.user-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
    .tooltip {
        width: 55vw;
        /* Keep tooltip width as 85% of the viewport */
        max-width: calc(55vw);
        /* Dynamically adjust max width */
    }

    .tooltip-content {
        font-size: 0.95rem;
        /* Slightly smaller font size */
    }
}

@media (max-width: 900px) {
    .tooltip {
        width: 65vw;
        /* Tooltip width stays at 85% */
        max-width: calc(65vw);
        /* Adjust max width dynamically */
        padding: 0.8rem;
        /* Reduce padding */
    }

    .tooltip-content {
        font-size: 0.9rem;
        /* Reduce font size */
    }
}

@media (max-width: 600px) {
    .tooltip {
        width: 50vw;
        /* Expand width for smaller screens */
        max-width: calc(50vw);
        /* Adjust max width dynamically */
        padding: 0.6rem;
        /* Further reduce padding */
    }

    .tooltip-content {
        font-size: 0.85rem;
        /* Make font size smaller */
    }
}

@media (max-width: 400px) {
    .tooltip {
        width: 40vw;
        /* Tooltip takes up most of the viewport width */
        max-width: calc(40vw);
        /* Adjust max width dynamically */
        padding: 0.5rem;
        /* Minimal padding */
    }

    .tooltip-content {
        font-size: 0.8rem;
        /* Smallest font size */
    }
}

/* For extremely small screens (e.g., 320px and below) */
@media (max-width: 320px) {
    .tooltip {
        width: 30vw;
        /* Take up nearly the full width of the viewport */
        max-width: calc(30vw);
        /* Dynamic max width */
        padding: 0.4rem;
        /* Minimal padding */
    }

    .tooltip-content {
        font-size: 0.75rem;
        /* Smallest font size for ultra-small screens */
    }
}
</style>