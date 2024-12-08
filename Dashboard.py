import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# Membuat data dummy untuk simulasi
def generate_dummy_data():
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    events = []
    
    for date in dates:
        severity = np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.3, 0.5])
        event_type = np.random.choice(['Malware', 'Intrusion', 'Authentication Failure', 'DDoS'])
        source_ip = f"192.168.{np.random.randint(1,255)}.{np.random.randint(1,255)}"
        
        events.append({
            'timestamp': date,
            'severity': severity,
            'event_type': event_type,
            'source_ip': source_ip
        })
    
    return pd.DataFrame(events)

df = generate_dummy_data()

# Layout dashboard
app.layout = html.Div([
    html.H1('Security Information and Event Management (SIEM) Dashboard',
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Ringkasan statistik
    html.Div([
        html.Div([
            html.H3('Total Events'),
            html.H4(id='total-events')
        ], className='stat-card'),
        html.Div([
            html.H3('High Severity Events'),
            html.H4(id='high-severity')
        ], className='stat-card'),
        html.Div([
            html.H3('Medium Severity Events'), 
            html.H4(id='medium-severity')
        ], className='stat-card'),
        html.Div([
            html.H3('Low Severity Events'),
            html.H4(id='low-severity')
        ], className='stat-card')
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px 0'}),
    
    # Filter waktu
    html.Div([
        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['timestamp'].min(),
            end_date=df['timestamp'].max(),
            style={'margin': '10px'}
        )
    ]),
    
    # Grafik
    html.Div([
        html.Div([
            dcc.Graph(id='events-timeline')
        ], style={'width': '100%', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='severity-pie'),
            dcc.Graph(id='event-type-bar')
        ], style={'display': 'flex'})
    ])
])

# Callbacks untuk update grafik dan statistik
@app.callback(
    [Output('total-events', 'children'),
     Output('high-severity', 'children'),
     Output('medium-severity', 'children'),
     Output('low-severity', 'children'),
     Output('events-timeline', 'figure'),
     Output('severity-pie', 'figure'),
     Output('event-type-bar', 'figure')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_dashboard(start_date, end_date):
    # Filter data berdasarkan rentang waktu
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Hitung statistik
    total = len(filtered_df)
    high = len(filtered_df[filtered_df['severity'] == 'High'])
    medium = len(filtered_df[filtered_df['severity'] == 'Medium'])
    low = len(filtered_df[filtered_df['severity'] == 'Low'])
    
    # Timeline events
    timeline = px.line(filtered_df.groupby('timestamp').size().reset_index(), 
                      x='timestamp', y=0, 
                      title='Event Timeline',
                      labels={'timestamp': 'Time', '0': 'Number of Events'})
    
    # Pie chart severity
    pie = px.pie(filtered_df, names='severity', 
                 title='Event Severity Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    # Bar chart event types
    bar = px.bar(filtered_df['event_type'].value_counts(), 
                 title='Event Types',
                 labels={'value': 'Count', 'index': 'Event Type'})
    
    return total, high, medium, low, timeline, pie, bar

# CSS untuk styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>SIEM Dashboard</title>
        <style>
            .stat-card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                width: 22%;
            }
            body {
                background-color: #f5f6fa;
                margin: 20px;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
