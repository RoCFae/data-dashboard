# Dynamic Dataset Dashboard

## Overview
This project is a dynamic data visualization dashboard built with Vue.js for the frontend and Flask for the backend. The dashboard allows users to upload CSV files, filter data, and visualize it through various types of plots, including scatter plots, contour plots, histograms, and box plots. The visualization is powered by Plotly, providing interactive and aesthetically pleasing charts.

## Features
- **File Upload**: Users can upload CSV files to load new datasets.
- **Data Filtering**: Filter data based on selected columns and value ranges.
- **Interactive Plots**: Visualize data through scatter plots, contour plots, histograms, and box plots.
- **Summary Statistics**: Display summary statistics for the filtered data.
- **Customizable Layout**: The layout is styled with a dark theme for better visual appeal.

## Project Structure

- **Backend (Flask)**: 
  - Handles file uploads, data processing, and generation of plot data.
  - Endpoints for retrieving column information, checking if a column is numeric, and fetching summary statistics.
  
- **Frontend (Vue.js)**:
  - Provides a user interface for uploading files, selecting plot types, filtering data, and viewing plots.
  - Components for file upload, plot rendering, and data filtering controls.

## Approach

1. **Data Handling**: 
   - The backend loads and processes CSV files using Pandas. It dynamically updates the dataset when a new file is uploaded.
   - Filters are applied to the dataset based on user inputs for the X and Y axes and any additional column filters.

2. **Plot Generation**:
   - The backend generates plot data using Plotly based on the selected plot type and filtered dataset.
   - Each plot type (scatter, contour, histogram, box) is handled separately, with specific configurations for each.
   - The title of each plot is dynamically generated based on the selected columns.

3. **Frontend Integration**:
   - The frontend uses Axios for API requests to fetch column information, check if columns are numeric, get summary statistics, and retrieve plot data.
   - Vue.js components handle the display and interaction of the file upload, plot controls, and rendering of plots using Plotly.

## Assumptions

- The CSV files uploaded have a consistent structure with a header row and data rows.
- Numeric columns are correctly identified by checking their data types using Pandas.
- The plots are rendered with a dark theme for visual consistency and appeal.
- The backend Flask application is running locally on `http://localhost:5000`.
- Users have basic knowledge of the types of plots and how to interpret them.

## Usage

1. **Run the Backend**:
   - Navigate to the backend directory and start the Flask application:
   - pip install -r requirements.txt
    #Create a virtual environment:
     ```bash
     py -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     py app.py
     ```

2. **Run the Frontend**:
   - Navigate to the frontend directory and start the Vue.js application:
     ```bash
     npm install
     npm run serve
     ```

## Dependencies

- **Backend**:
  - Flask
  - Flask-CORS
  - Pandas
  - Plotly

- **Frontend**:
  - Vue.js
  - Axios
  - vue3-slider
  - lodash.debounce

## License
This project is licensed under the MIT License.
