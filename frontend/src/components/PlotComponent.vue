<template>
  <div ref="plotDiv"></div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  name: 'PlotComponent',
  props: ['plotData'],
  watch: {
    plotData: function(newPlotData) {
      this.renderPlot(newPlotData);
    }
  },
  methods: {
    renderPlot(data) {
      if (data) {
        Plotly.react(this.$refs.plotDiv, data.data, data.layout);
      }
    }
  },
  mounted() {
    this.renderPlot(this.plotData);
  }
};
</script>
