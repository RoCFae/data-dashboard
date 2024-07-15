<template>
  <div class="dashboard">
    <div class="header">
      <h1>Dynamic Dataset Dashboard</h1>
    </div>
    <div class="content">
      <div class="left-panel">
        <div class="sticky-container">
          <h2 class="controls_tittle">Plot Controls</h2>
          <div class="upload-wrapper">
            <UploadComponent @file-uploaded="handleFileUploaded" />
          </div>
          <div class="controls">
            <label for="plot-selector">Select Plot:</label>
            <select
              id="plot-selector"
              v-model="selectedPlot"
              @change="fetchPlot"
            >
              <option value="scatter">Scatter Plot</option>
              <option value="contour">Contour Plot</option>
              <option value="histogram">Histogram</option>
              <option value="box">Box Plot</option>
              <option value="all">All</option>
            </select>
          </div>
          <div
            v-if="
              selectedPlot === 'scatter' ||
              selectedPlot === 'contour' ||
              selectedPlot === 'box' ||
              selectedPlot === 'all'
            "
            class="controls"
          >
            <label for="x-column">X-Axis:</label>
            <select id="x-column" v-model="xColumn" @change="updateRanges">
              <option v-for="col in numericColumns" :key="col" :value="col">
                {{ col }}
              </option>
            </select>
            <label for="y-column" v-if="selectedPlot !== 'histogram'"
              >Y-Axis:</label
            >
            <select
              id="y-column"
              v-if="selectedPlot !== 'histogram'"
              v-model="yColumn"
              @change="updateRanges"
            >
              <option v-for="col in numericColumns" :key="col" :value="col">
                {{ col }}
              </option>
            </select>
          </div>
          <div class="controls">
            <label for="color-column">Color By:</label>
            <select
              id="color-column"
              v-model="colorColumn"
              @change="fetchPlots"
            >
              <option v-for="col in columns" :key="col" :value="col">
                {{ col }}
              </option>
            </select>
          </div>
          <div
            v-if="
              selectedPlot === 'scatter' ||
              selectedPlot === 'contour' ||
              selectedPlot === 'all' ||
              selectedPlot === 'box'
            "
            class="controls"
          >
            <div>
              <label for="min-x">Min X: {{ minX }}</label>
              <vue3-slider
                v-model="minX"
                :min="xRange[0]"
                :max="xRange[1]"
                @change="debouncedFetchPlots"
                :tooltip="true"
              ></vue3-slider>
            </div>
            <div>
              <label for="max-x">Max X: {{ maxX }}</label>
              <vue3-slider
                v-model="maxX"
                :min="xRange[0]"
                :max="xRange[1]"
                @change="debouncedFetchPlots"
                :tooltip="true"
              ></vue3-slider>
            </div>
            <div v-if="selectedPlot !== 'histogram'">
              <label for="min-y">Min Y: {{ minY }}</label>
              <vue3-slider
                v-model="minY"
                :min="yRange[0]"
                :max="yRange[1]"
                @change="debouncedFetchPlots"
                :tooltip="true"
              ></vue3-slider>
            </div>
            <div v-if="selectedPlot !== 'histogram'">
              <label for="max-y">Max Y: {{ maxY }}</label>
              <vue3-slider
                v-model="maxY"
                :min="yRange[0]"
                :max="yRange[1]"
                @change="debouncedFetchPlots"
                :tooltip="true"
              ></vue3-slider>
            </div>
          </div>
        </div>
      </div>
      <div class="right-panel">
        <div class="plot" v-if="selectedPlot === 'scatter'">
          <PlotComponent :plotData="scatterPlotData" />
        </div>
        <div class="plot" v-else-if="selectedPlot === 'contour'">
          <PlotComponent :plotData="contourPlotData" />
        </div>
        <div class="plot" v-else-if="selectedPlot === 'histogram'">
          <PlotComponent :plotData="histogramPlotData" />
        </div>
        <div class="plot" v-else-if="selectedPlot === 'box'">
          <PlotComponent :plotData="boxPlotData" />
        </div>
        <div v-if="selectedPlot === 'all'">
          <div class="plot">
            <PlotComponent :plotData="scatterPlotData" />
          </div>
          <div class="plot">
            <PlotComponent :plotData="contourPlotData" />
          </div>
          <div class="plot">
            <PlotComponent :plotData="histogramPlotData" />
          </div>
          <div class="plot">
            <PlotComponent :plotData="boxPlotData" />
          </div>
        </div>
        <div v-if="summaryStats.length > 0" class="summary">
          <h2>Summary Statistics</h2>
          <table>
            <thead>
              <tr>
                <th v-for="(header, index) in summaryHeaders" :key="index">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in summaryStats" :key="rowIndex">
                <td
                  v-for="(header, headerIndex) in summaryHeaders"
                  :key="headerIndex"
                >
                  {{ row[header] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div> 
        <div v-else-if="summaryStats.length === 0" class="summary">
          <p>No summary statistics available.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import PlotComponent from "../components/PlotComponent.vue";
import UploadComponent from "../components/UploadComponent.vue";
import Vue3Slider from "vue3-slider";
import debounce from "lodash/debounce";

const API_BASE_URL = "http://localhost:5000"; // URL base do backend

export default {
  name: "DataDashboard",
  components: {
    PlotComponent,
    UploadComponent,
    Vue3Slider,
  },
  data() {
    return {
      selectedPlot: "all",
      xColumn: "",
      yColumn: "",
      colorColumn: "",
      minX: 0,
      maxX: 100,
      minY: 0,
      maxY: 100,
      scatterPlotData: null,
      contourPlotData: null,
      histogramPlotData: null,
      boxPlotData: null,
      summaryStats: [],
      summaryHeaders: [],
      columns: [],
      numericColumns: [],
      xRange: [0, 100],
      yRange: [0, 100],
      showSummary: true,
    };
  },
  methods: {
    handleFileUploaded() {
      this.showSummary = false;
      this.fetchColumns();
    },
    async fetchColumns() {
      try {
        const response = await axios.get(`${API_BASE_URL}/columns`);
        this.columns = response.data;
        const numericCheckPromises = this.columns.map((col) =>
          this.isNumeric(col)
        );
        const numericResults = await Promise.all(numericCheckPromises);
        this.numericColumns = this.columns.filter(
          (col, index) => numericResults[index]
        );
        if (this.numericColumns.length >= 2) {
          this.xColumn = this.numericColumns[0];
          this.yColumn = this.numericColumns[1];
          this.colorColumn = this.columns.includes("species")
            ? "species"
            : this.numericColumns[0];
          this.updateRanges();
        }
      } catch (error) {
        console.error("Error fetching columns:", error);
      }
    },
    async isNumeric(column) {
      try {
        const response = await axios.get(`${API_BASE_URL}/is_numeric`, {
          params: { column },
        });
        return response.data.is_numeric;
      } catch (error) {
        console.error("Error checking if column is numeric:", error);
        return false;
      }
    },
    async updateRanges() {
      try {
        const response = await axios.get(`${API_BASE_URL}/column_stats`, {
          params: {
            x_column: this.xColumn,
            y_column: this.yColumn,
          },
        });
        const xStats = response.data.x_stats;
        const yStats = response.data.y_stats;
        this.xRange = [xStats.min, xStats.max];
        this.yRange = [yStats.min, yStats.max];
        this.minX = xStats.min;
        this.maxX = xStats.max;
        this.minY = yStats.min;
        this.maxY = yStats.max;
        this.fetchPlots();
      } catch (error) {
        console.error("Error fetching column stats:", error);
      }
    },
    fetchPlots() {
      const params = {
        x_column: this.xColumn,
        y_column: this.selectedPlot !== "histogram" ? this.yColumn : undefined,
        color_column: this.colorColumn,
        min_x: this.minX,
        max_x: this.maxX,
        min_y: this.selectedPlot !== "histogram" ? this.minY : undefined,
        max_y: this.selectedPlot !== "histogram" ? this.maxY : undefined,
      };
      const plotTypes = ["scatter", "contour", "histogram", "box"];
      plotTypes.forEach((plotType) => {
        axios
          .get(`${API_BASE_URL}/plot`, {
            params: { ...params, plot_type: plotType },
          })
          .then((response) => {
            if (plotType === "scatter") {
              this.scatterPlotData = JSON.parse(response.data.scatter);
            } else if (plotType === "contour") {
              this.contourPlotData = JSON.parse(response.data.contour);
            } else if (plotType === "histogram") {
              this.histogramPlotData = JSON.parse(response.data.histogram);
            } else if (plotType === "box") {
              this.boxPlotData = JSON.parse(response.data.box);
            }
          })
          .catch((error) => {
            console.error(
              `There was an error fetching the ${plotType} plot!`,
              error
            );
          });
      });
      this.fetchSummary(params); // Pass the same params to fetchSummary
    },
    fetchPlot() {
      this.fetchPlots();
    },
    async fetchSummary(params) {
      try {
        const response = await axios.get(`${API_BASE_URL}/summary`, { params });
        this.summaryStats = response.data || [];
        console.log("Summary stats from backend:", this.summaryStats);

        if (this.summaryStats.length > 0) {
          const sampleRow = this.summaryStats[0];
          console.log("Sample row:", sampleRow);
          this.summaryHeaders = Object.keys(sampleRow);
          console.log("Summary headers:", this.summaryHeaders);
        } else {
          this.summaryHeaders = [];
        }

        console.log("Summary headers after processing:", this.summaryHeaders);
        console.log("Summary stats being rendered:", this.summaryStats);
      } catch (error) {
        console.error(
          "There was an error fetching the summary statistics!",
          error
        );
        this.summaryStats = [];
        this.summaryHeaders = [];
      }
    },
    debouncedFetchPlots: debounce(function () {
      this.fetchPlots();
    }, 500),
    async loadInitialData() {
      try {
        await this.fetchColumns();
        this.selectedPlot = "all";
      } catch (error) {
        console.error("Error loading initial data:", error);
      }
    },
  },
  mounted() {
    this.loadInitialData();
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: #092635;
  color: #faf0e6;
  font-family: "Arial", sans-serif;
}

.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  text-align: center;
  padding: 20px;
  background-color: #1b4242;
  border-bottom: 2px solid #092635;
}

.content {
  display: flex;
  flex: 1;
}

.left-panel {
  flex: 1;
  padding: 20px;
  margin-top: 40px;
  background-color: #1b4242;
  border-right: 2px solid #092635;
}

.sticky-container {
  position: sticky;
  top: 20px;
}

.upload-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.right-panel {
  flex: 3;
  padding: 20px;
  background-color: #092635;
  overflow-y: auto;
}

.controls {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #9ec8b9;
}

select {
  background-color: #1b4242;
  color: #faf0e6;
  border: 1px solid #5c8374;
  border-radius: 5px;
  padding: 5px;
  width: 100%;
  margin-bottom: 10px;
}

.vue3-slider {
  --vue-slider-main-color: #5c8374;
  --vue-slider-rail-background: #1b4242;
  --vue-slider-thumb-background: #9ec8b9;
}

.plot {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  background-color: #1b4242;
  border-radius: 10px;
  padding: 20px;
}

.summary {
  margin-top: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th,
td {
  border: 1px solid #5c8374;
  padding: 10px;
  text-align: left;
}

th {
  background-color: #5c8374;
}

td {
  background-color: #1b4242;
}

@media (min-width: 768px) {
  .dashboard {
    flex-direction: column;
  }
  .content {
    flex-direction: row;
  }
}

@media (max-width: 767px) {
  .left-panel,
  .right-panel {
    width: 100%;
  }

  .sticky-container {
    position: relative;
  }
}
</style>
