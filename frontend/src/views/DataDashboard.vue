<template>
  <div class="dashboard">
    <div class="left-panel">
      <h1>Dynamic Dataset Dashboard</h1>
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
      <div class="summary">
        <h2>Summary Statistics</h2>
        <table>
          <thead>
            <tr>
              <th>Group</th>
              <th>Count</th>
              <th v-for="(stat, index) in summaryHeaders" :key="index">{{ formattedHeader(stat) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in summaryStats" :key="index">
              <td>{{ row[colorColumn] }}</td>
              <td>{{ row.count }}</td>
              <td v-for="(stat, statIndex) in summaryHeaders" :key="statIndex">{{ formatNumber(row[stat]) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="right-panel">
      <div class="controls">
        <label for="plot-selector">Select Plot:</label>
        <select id="plot-selector" v-model="selectedPlot" @change="fetchPlot">
          <option value="scatter">Scatter Plot</option>
          <option value="contour">Contour Plot</option>
          <option value="histogram">Histogram</option>
          <option value="box">Box Plot</option>
          <option value="all">All</option>
        </select>
      </div>
      <div v-if="selectedPlot === 'scatter' || selectedPlot === 'contour' || selectedPlot === 'box'" class="controls">
        <label for="x-column">X-Axis:</label>
        <select id="x-column" v-model="xColumn" @change="updateRanges">
          <option v-for="col in filteredColumns" :key="col" :value="col">{{ col }}</option>
        </select>
        <label for="y-column">Y-Axis:</label>
        <select id="y-column" v-model="yColumn" @change="updateRanges">
          <option v-for="col in filteredColumns" :key="col" :value="col">{{ col }}</option>
        </select>
      </div>
      <div class="controls">
        <label for="color-column">Color By:</label>
        <select id="color-column" v-model="colorColumn" @change="fetchPlots">
          <option v-for="col in columns" :key="col" :value="col">{{ col }}</option>
        </select>
      </div>
      <div v-if="selectedPlot === 'scatter' || selectedPlot === 'contour' || selectedPlot === 'all' || selectedPlot === 'box'" class="controls">
        <div>
          <label for="min-x">Min X: {{ minX }}</label>
          <vue3-slider v-model="minX" :min="xRange[0]" :max="xRange[1]" @change="debouncedFetchPlots" :tooltip="true"></vue3-slider>
        </div>
        <div>
          <label for="max-x">Max X: {{ maxX }}</label>
          <vue3-slider v-model="maxX" :min="xRange[0]" :max="xRange[1]" @change="debouncedFetchPlots" :tooltip="true"></vue3-slider>
        </div>
        <div>
          <label for="min-y">Min Y: {{ minY }}</label>
          <vue3-slider v-model="minY" :min="yRange[0]" :max="yRange[1]" @change="debouncedFetchPlots" :tooltip="true"></vue3-slider>
        </div>
        <div>
          <label for="max-y">Max Y: {{ maxY }}</label>
          <vue3-slider v-model="maxY" :min="yRange[0]" :max="yRange[1]" @change="debouncedFetchPlots" :tooltip="true"></vue3-slider>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import PlotComponent from '../components/PlotComponent.vue';
import Vue3Slider from 'vue3-slider';
import debounce from 'lodash/debounce';

const API_BASE_URL = 'http://localhost:5000'; // URL base do backend

export default {
  name: 'DataDashboard',
  components: {
    PlotComponent,
    Vue3Slider
  },
  data() {
    return {
      selectedPlot: 'scatter',
      xColumn: 'bill_length_mm',
      yColumn: 'bill_depth_mm',
      colorColumn: 'species',
      minX: 0,
      maxX: 60,
      minY: 0,
      maxY: 21,
      scatterPlotData: null,
      contourPlotData: null,
      histogramPlotData: null,
      boxPlotData: null,
      summaryStats: [],
      summaryHeaders: [],
      columns: ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g', 'species', 'island'],
      filteredColumns: ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g'],
      xRange: [0, 60],
      yRange: [0, 21]
    };
  },
  methods: {
    async updateRanges() {
      try {
        const response = await axios.get(`${API_BASE_URL}/column_stats`, {
          params: {
            x_column: this.xColumn,
            y_column: this.yColumn
          }
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
        this.fetchSummary();
      } catch (error) {
        console.error("Error fetching column stats:", error);
      }
    },
    fetchPlots() {
      const params = {
        x_column: this.xColumn,
        y_column: this.yColumn,
        color_column: this.colorColumn,
        min_x: this.minX,
        max_x: this.maxX,
        min_y: this.minY,
        max_y: this.maxY
      };

      const plotTypes = ['scatter', 'contour', 'histogram', 'box'];

      plotTypes.forEach(plotType => {
        axios
          .get(`${API_BASE_URL}/plot`, { params: { ...params, plot_type: plotType } })
          .then(response => {
            if (plotType === 'scatter') {
              this.scatterPlotData = JSON.parse(response.data.scatter);
            } else if (plotType === 'contour') {
              this.contourPlotData = JSON.parse(response.data.contour);
            } else if (plotType === 'histogram') {
              this.histogramPlotData = JSON.parse(response.data.histogram);
            } else if (plotType === 'box') {
              this.boxPlotData = JSON.parse(response.data.box);
            }
          })
          .catch(error => {
            console.error(`There was an error fetching the ${plotType} plot!`, error);
          });
      });
    },
    fetchPlot() {
      this.fetchPlots();
      this.fetchSummary();
    },
    fetchSummary() {
      const params = {
        x_column: this.xColumn,
        y_column: this.yColumn,
        color_column: this.colorColumn,
        min_x: this.minX,
        max_x: this.maxX,
        min_y: this.minY,
        max_y: this.maxY
      };

      axios
        .get(`${API_BASE_URL}/summary`, { params })
        .then(response => {
          this.summaryStats = response.data;
          this.summaryHeaders = Object.keys(response.data[0]).filter(key => key !== this.colorColumn && key !== 'count');
        })
        .catch(error => {
          console.error("There was an error fetching the summary statistics!", error);
        });
    },
    formattedHeader(header) {
      const headerMapping = {
        'bill_length_mm_mean': 'Mean Bill Length',
        'bill_length_mm_std': 'Std Dev Bill Length',
        'bill_length_mm_min': 'Min Bill Length',
        'bill_length_mm_max': 'Max Bill Length',
        'bill_depth_mm_mean': 'Mean Bill Depth',
        'bill_depth_mm_std': 'Std Dev Bill Depth',
        'bill_depth_mm_min': 'Min Bill Depth',
        'bill_depth_mm_max': 'Max Bill Depth',
        'flipper_length_mm_mean': 'Mean Flipper Length',
        'flipper_length_mm_std': 'Std Dev Flipper Length',
        'flipper_length_mm_min': 'Min Flipper Length',
        'flipper_length_mm_max': 'Max Flipper Length',
        'body_mass_g_mean': 'Mean Body Mass',
        'body_mass_g_std': 'Std Dev Body Mass',
        'body_mass_g_min': 'Min Body Mass',
        'body_mass_g_max': 'Max Body Mass'
      };
      return headerMapping[header] || header;
    },
    formatNumber(value) {
      return Number(value).toFixed(2);
    },
    debouncedFetchPlots: debounce(function() {
      this.fetchPlots();
      this.fetchSummary();
    }, 500)
  },
  mounted() {
    this.updateRanges();
  }
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
  color: #FAF0E6;
  font-family: 'Arial', sans-serif;
}

.dashboard {
  display: flex;
  height: 100vh;
}

.left-panel {
  flex: 3;
  padding: 20px;
  background-color: #092635;
  border-right: 2px solid #1B4242;
}

.right-panel {
  flex: 1;
  padding: 20px;
  background-color: #1B4242;
}

.controls {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #9EC8B9;
}

select {
  background-color: #1B4242;
  color: #FAF0E6;
  border: 1px solid #5C8374;
  border-radius: 5px;
  padding: 5px;
  width: 100%;
  margin-bottom: 10px;
}

.vue3-slider {
  --vue-slider-main-color: #5C8374;
  --vue-slider-rail-background: #1B4242;
  --vue-slider-thumb-background: #9EC8B9;
}

.plot {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  background-color: #1B4242;
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

th, td {
  border: 1px solid #5C8374;
  padding: 10px;
  text-align: left;
}

th {
  background-color: #5C8374;
}

td {
  background-color: #1B4242;
}
</style>
