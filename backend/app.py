from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
CORS(app)

# Carregar o conjunto de dados
data_path = 'data/penguins.csv'
df = pd.read_csv(data_path)

# Remover valores nulos
df = df.dropna(subset=['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g', 'species', 'island'])

# Definir layout padrão com tema escuro
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
    plot_type = request.args.get('plot_type', 'scatter')
    x_column = request.args.get('x_column', 'bill_length_mm')
    y_column = request.args.get('y_column', 'bill_depth_mm')
    color_column = request.args.get('color_column', 'species')
    filters = request.args.to_dict(flat=True)

    min_x = float(filters.pop('min_x', df[x_column].min()))
    max_x = float(filters.pop('max_x', df[x_column].max()))
    min_y = float(filters.pop('min_y', df[y_column].min()))
    max_y = float(filters.pop('max_y', df[y_column].max()))

    # Aplicar filtros adicionais
    filtered_df = df.copy()
    for column, value in filters.items():
        if column in df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]

    filtered_df = filtered_df[
        (filtered_df[x_column] >= min_x) &
        (filtered_df[x_column] <= max_x) &
        (filtered_df[y_column] >= min_y) &
        (filtered_df[y_column] <= max_y)
    ]

    # Criar o gráfico com base no tipo de gráfico solicitado
    if plot_type == 'scatter':
        fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column)
    elif plot_type == 'contour':
        fig = px.density_contour(filtered_df, x=x_column, y=y_column, color=color_column)
    elif plot_type == 'histogram':
        fig = px.histogram(filtered_df, x=x_column, color=color_column)
    elif plot_type == 'box':
        fig = px.box(filtered_df, x=color_column, y=x_column)
    else:
        return jsonify({'error': 'Invalid plot type'}), 400

    fig.update_layout(layout)
    graph_json = fig.to_json()
    return jsonify({plot_type: graph_json})

@app.route('/column_stats', methods=['GET'])
def column_stats():
    x_column = request.args.get('x_column', 'bill_length_mm')
    y_column = request.args.get('y_column', 'bill_depth_mm')

    x_stats = {'min': df[x_column].min(), 'max': df[x_column].max()}
    y_stats = {'min': df[y_column].min(), 'max': df[y_column].max()}

    return jsonify({'x_stats': x_stats, 'y_stats': y_stats})

@app.route('/summary', methods=['GET'])
def summary():
    color_column = request.args.get('color_column', 'species')
    filters = request.args.to_dict(flat=True)
    
    filtered_df = df.copy()
    for column, value in filters.items():
        if column in df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]

    summary_stats = filtered_df.groupby(color_column).agg(
        bill_length_mm_mean=('bill_length_mm', 'mean'),
        bill_length_mm_std=('bill_length_mm', 'std'),
        bill_length_mm_min=('bill_length_mm', 'min'),
        bill_length_mm_max=('bill_length_mm', 'max'),
        bill_depth_mm_mean=('bill_depth_mm', 'mean'),
        bill_depth_mm_std=('bill_depth_mm', 'std'),
        bill_depth_mm_min=('bill_depth_mm', 'min'),
        bill_depth_mm_max=('bill_depth_mm', 'max'),
        flipper_length_mm_mean=('flipper_length_mm', 'mean'),
        flipper_length_mm_std=('flipper_length_mm', 'std'),
        flipper_length_mm_min=('flipper_length_mm', 'min'),
        flipper_length_mm_max=('flipper_length_mm', 'max'),
        body_mass_g_mean=('body_mass_g', 'mean'),
        body_mass_g_std=('body_mass_g', 'std'),
        body_mass_g_min=('body_mass_g', 'min'),
        body_mass_g_max=('body_mass_g', 'max'),
        count=('species', 'count')
    ).reset_index().to_dict(orient='records')

    return jsonify(summary_stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
