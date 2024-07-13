const resizeObserverLoopErr = () => {
  let resizeObserverErr;
  const resizeObserverErrHandler = (err) => {
    if (err.message === "ResizeObserver loop limit exceeded") {
      resizeObserverErr = err;
      window.addEventListener("unhandledrejection", (event) => {
        if (event.reason === resizeObserverErr) {
          event.stopImmediatePropagation();
        }
      });
    }
  };
  window.addEventListener("error", resizeObserverErrHandler);
};

resizeObserverLoopErr();

import { createApp } from "vue";
import App from "./App.vue";
import "./global.css";

createApp(App).mount("#app");
