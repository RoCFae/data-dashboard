from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
CORS(app)  #enable CORS for all origins

#initial dataset
data_path = 'data/penguins.csv'
df = pd.read_csv(data_path)

layout = {
    'paper_bgcolor': '#092635',
    'plot_bgcolor': '#1B4242',
    'font': {
        'color': '#FAF0E6'
    },
    'xaxis': {
        'gridcolor': '#5C8374',
        'zerolinecolor': '#5C8374'
    },
    'yaxis': {
        'gridcolor': '#5C8374',
        'zerolinecolor': '#5C8374'
    }
}

@app.route('/plot', methods=['GET'])
def plot():
    global df
    plot_type = request.args.get('plot_type', 'scatter')
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')
    color_column = request.args.get('color_column')
    filters = request.args.to_dict(flat=True)

    #set default filter values
    min_x = float(filters.pop('min_x', df[x_column].min()))
    max_x = float(filters.pop('max_x', df[x_column].max()))
    
    #only set min_y and max_y if y_column is provided
    if y_column:
        min_y = float(filters.pop('min_y', df[y_column].min()))
        max_y = float(filters.pop('max_y', df[y_column].max()))

    #apply additional filters
    filtered_df = df.copy()
    for column, value in filters.items():
        if column in df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]

    #convert columns to numeric
    filtered_df[x_column] = pd.to_numeric(filtered_df[x_column], errors='coerce')
    if y_column:
        filtered_df[y_column] = pd.to_numeric(filtered_df[y_column], errors='coerce')

    filtered_df = filtered_df[
        (filtered_df[x_column] >= min_x) &
        (filtered_df[x_column] <= max_x)
    ]
    if y_column:
        filtered_df = filtered_df[
            (filtered_df[y_column] >= min_y) &
            (filtered_df[y_column] <= max_y)
        ]

    #remove null values after conversion
    filtered_df = filtered_df.dropna(subset=[x_column])
    if y_column:
        filtered_df = filtered_df.dropna(subset=[y_column])

    #create plot based on the requested plot type
    if plot_type == 'scatter':
        fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column)
        title = f"Scatter Plot of {x_column} vs {y_column}"
    elif plot_type == 'contour':
        fig = px.density_contour(filtered_df, x=x_column, y=y_column, color=color_column)
        title = f"Contour Plot of {x_column} vs {y_column}"
    elif plot_type == 'histogram':
        fig = px.histogram(filtered_df, x=x_column, color=color_column)
        title = f"Histogram of {x_column}"
    elif plot_type == 'box':
        fig = px.box(filtered_df, x=color_column, y=x_column)
        title = f"Box Plot of {x_column} by {color_column}"
    else:
        return jsonify({'error': 'Invalid plot'}), 400

    fig.update_layout(layout, title=title)
    graph_json = fig.to_json()
    return jsonify({plot_type: graph_json})

@app.route('/column_stats', methods=['GET'])
def column_stats():
    #get statitics for the selected columns
    global df
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')

    #check if columns exist in the DataFrame
    if x_column not in df.columns or y_column not in df.columns:
        return jsonify({'error': 'One or both columns not found in the DataFrame'}), 400

    #check if columns are numeric
    x_is_numeric = pd.api.types.is_numeric_dtype(df[x_column])
    y_is_numeric = pd.api.types.is_numeric_dtype(df[y_column])
    if not x_is_numeric or not y_is_numeric:
        return jsonify({'error': 'One or both columns are not numeric'}), 400

    x_stats = {
        'min': float(df[x_column].min()),
        'max': float(df[x_column].max())
    }
    y_stats = {
        'min': float(df[y_column].min()),
        'max': float(df[y_column].max())
    }

    return jsonify({'x_stats': x_stats, 'y_stats': y_stats})

@app.route('/summary', methods=['GET'])
def summary():
    global df
    color_column = request.args.get('color_column')
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')
    min_x = float(request.args.get('min_x', df[x_column].min()))
    max_x = float(request.args.get('max_x', df[x_column].max()))

    filtered_df = df[
        (df[x_column] >= min_x) &
        (df[x_column] <= max_x)
    ]

    if y_column:
        min_y = float(request.args.get('min_y', df[y_column].min()))
        max_y = float(request.args.get('max_y', df[y_column].max()))
        filtered_df = filtered_df[
            (filtered_df[y_column] >= min_y) &
            (filtered_df[y_column] <= max_y)
        ]

    if color_column not in df.columns:
        return jsonify({'error': 'Color column not found in the DataFrame'}), 400

    numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
    agg_funcs = {col: ['mean', 'std', 'min', 'max'] for col in numeric_cols}

    try:
        if pd.api.types.is_numeric_dtype(df[color_column]):
            bins = pd.cut(filtered_df[color_column], bins=10)
            grouped_df = filtered_df.groupby(bins).agg(agg_funcs)
            grouped_df['count'] = filtered_df.groupby(bins).size()
            grouped_df = grouped_df.reset_index()
            grouped_df.rename(columns={bins.name: 'bin'}, inplace=True)
            grouped_df['bin'] = grouped_df['bin'].astype(str)
        else:
            grouped_df = filtered_df.groupby(color_column).agg(agg_funcs)
            grouped_df['count'] = filtered_df.groupby(color_column).size()
            grouped_df = grouped_df.reset_index()

        grouped_df.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in grouped_df.columns.values]
        grouped_df = grouped_df.round(2)

        return jsonify(grouped_df.to_dict(orient='records'))
    except KeyError as e:
        return jsonify({'error': f"Column {e} do not exist"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/columns', methods=['GET'])
def get_columns():
    #get the list of columns in the dataset
    global df
    return jsonify(df.columns.tolist())

@app.route('/is_numeric', methods=['GET'])
def is_numeric():
    #check if a column is numeric
    global df
    column = request.args.get('column')
    is_numeric = pd.api.types.is_numeric_dtype(df[column])
    return jsonify({'is_numeric': is_numeric})

@app.route('/upload', methods=['POST'])
def upload_file():
    #upload a csv to replace the current dataset
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        global df
        df = pd.read_csv(file)
        return jsonify({'message': 'File successfully uploaded!'}), 200
    return jsonify({'error': 'File upload failed'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
