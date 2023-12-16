import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import numpy as np

with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
    dic_data = pickle.load(file)

def plot_zscores(dic_data, date, ls_zscores, leg):
    dic_asts_data = dic_data['dic_asts_data']
    df_zscores = dic_asts_data[date]
    df_zscores = df_zscores[['PERMNO', 'CONM', 'TIC'] + ls_zscores]
    ls_permnos = df_zscores['PERMNO'].unique().tolist()
    df_zscores['ZS_INT'] = df_zscores[ls_zscores].mean(axis=1, skipna=False)

    ascending = False
    if leg == 'L':
        ascending = False
    elif leg == 'S':
        ascending = True

    n_asts = 50
    dic_s_zscores = {}
    for i in range(len(ls_zscores)):
        dic_s_zscores[i] = pd.Series(list(df_zscores[ls_zscores[i]]), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=ascending)
    dic_s_zscores[len(ls_zscores)] = pd.Series(list(df_zscores['ZS_INT']), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=ascending)

    if len(ls_zscores) == 2:
        ls_asts_0 = sorted(dic_s_zscores[0].index.tolist())  # ZS_0
        ls_asts_1 = sorted(dic_s_zscores[1].index.tolist())  # ZS_1
        ls_asts_2 = sorted(dic_s_zscores[2].index.tolist())  # ZS_INT

        ls_asts_3 = [ast for ast in ls_asts_0 if ast not in ls_asts_2]  # Only ZS_0
        ls_asts_4 = [ast for ast in ls_asts_1 if ast not in ls_asts_2]  # Only ZS_1
        ls_asts_5 = [ast for ast in ls_permnos if (ast not in ls_asts_0) and (ast not in ls_asts_1) and (ast not in ls_asts_2)]  # All other

        # Create scatter plot traces
        trace_0 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='green'), name='All Points')
        trace_1 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='red'), name='All Points')
        trace_2 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='blue'), name='All Points')
        trace_3 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='black'), name='All Points')

        # Create layout
        layout = go.Layout(title='Interactive Scatter Plot with Highlighted Points',
                           xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))

        # Create figure with both traces
        fig = go.Figure(data=[trace_0, trace_1, trace_2, trace_3], layout=layout)

        # Save plot as an HTML file
        pyo.plot(fig, filename='scatter_plot_highlighted.html')

plot_zscores(dic_data, date=datetime(2000, 12, 31), ls_zscores=['ZS_VAL', 'ZS_QLT'], leg='L')

# %%







np.random.seed(0)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)

data = {'x': x, 'y': y}
df = pd.DataFrame(data)

# Create scatter plot trace
trace = go.Scatter(x=df['x'], y=df['y'], mode='markers', marker=dict(size=8, color='blue'), name='Scatter Plot')

# Create layout
layout = go.Layout(title='Interactive Scatter Plot', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))

# Create figure
fig = go.Figure(data=[trace], layout=layout)

# Save plot as an HTML file
pyo.plot(fig, filename='scatter_plot.html')




# Sample data for a 3D scatter plot
np.random.seed(0)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)
z = 3 * x - y + np.random.randn(100)  # Adding a third dimension 'z'

data = {'x': x, 'y': y, 'z': z}  # Including 'z' in the data
df = pd.DataFrame(data)

# Create 3D scatter plot trace
trace = go.Scatter3d(x=df['x'], y=df['y'], z=df['z'], mode='markers',
                      marker=dict(size=8, color='blue'), name='Scatter Plot')

# Create layout for 3D plot
layout = go.Layout(title='Interactive 3D Scatter Plot', scene=dict(xaxis=dict(title='X-axis'),
                                                                  yaxis=dict(title='Y-axis'),
                                                                  zaxis=dict(title='Z-axis')))

# Create figure
fig = go.Figure(data=[trace], layout=layout)

# Save 3D plot as an HTML file
pyo.plot(fig, filename='scatter_3d_plot.html')