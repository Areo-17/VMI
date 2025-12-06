import os
import pandas as pd
from flask import Flask, render_template
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Spectral5, Spectral6

app = Flask(__name__)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.abspath(os.path.join(BASE_PATH, "..", "data"))

def load_data():
    """Loads and processes the transportation data."""
    try:
        # UPDATED: Loading the new processed file
        df = pd.read_csv(f'{FILE_PATH}/processed_big.csv')
        
        # Convert transaction_date to datetime objects
        # The new file uses standard YYYY-MM-DD format which pandas handles automatically
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame() # Return empty DF on error
    
def load_urban_data():
    """Loads urban sensor data for the new dashboard."""
    try:
        df = pd.read_csv(f'{FILE_PATH}/processed/urban_sensors_processed.csv')
        df['ts'] = pd.to_datetime(df['ts'])
        return df
    except Exception as e:
        print(f"Error loading urban data: {e}")
        return pd.DataFrame()

@app.route('/')
def u3_project():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    df = load_data()
    
    if df.empty:
        return "Error: Could not load 'processed_big.csv'. Please check the file path."

    # ---------------------------------------------------------
    # 1. KPI Calculation: Total Revenue
    # ---------------------------------------------------------
    total_revenue = df['fare_amount_mxn'].sum()
    kpi_revenue_display = f"${total_revenue:,.2f} MXN"

    # ---------------------------------------------------------
    # 2. Time Series Chart: Daily Passengers
    # ---------------------------------------------------------
    daily_stats = df.groupby('transaction_date')['passenger_count'].sum().reset_index()
    source_ts = ColumnDataSource(daily_stats)

    p_ts = figure(title="Daily Passenger Trends", x_axis_type='datetime', 
                  height=350, sizing_mode="stretch_width",
                  tools="pan,wheel_zoom,box_zoom,reset,save")
    
    p_ts.line(x='transaction_date', y='passenger_count', source=source_ts, 
              line_width=3, color="#007AFF", legend_label="Passengers")
    
    p_ts.circle(x='transaction_date', y='passenger_count', source=source_ts, 
                size=6, color="white", line_color="#007AFF", line_width=2)

    p_ts.add_tools(HoverTool(
        tooltips=[("Date", "@transaction_date{%F}"), ("Passengers", "@passenger_count")],
        formatters={"@transaction_date": "datetime"}
    ))
    
    p_ts.toolbar.logo = None
    p_ts.border_fill_color = None
    p_ts.outline_line_color = None
    p_ts.legend.location = "top_left"
    p_ts.legend.background_fill_alpha = 0.5

    # ---------------------------------------------------------
    # 3. Bar Chart: Top 5 Boarding Areas (FIXED)
    # ---------------------------------------------------------
    top_areas = df['boarding_area'].value_counts().head(5).reset_index()
    top_areas.columns = ['area', 'count']
    
    # FIX START: Create a 'color' column in the DataFrame and assign the palette.
    colors_list = Spectral5[:len(top_areas)] 
    top_areas['color'] = colors_list 
    
    # Update the ColumnDataSource with the new color column
    source_bar = ColumnDataSource(top_areas)
    # FIX END

    p_bar = figure(x_range=top_areas['area'], title="Top 5 Busiest Boarding Areas",
                   height=350, sizing_mode="stretch_width",
                   tools="hover,reset,save", tooltips=[("Area", "@area"), ("Trips", "@count")])

    # Reference the new 'color' column in fill_color
    p_bar.vbar(x='area', top='count', width=0.6, source=source_bar, 
               line_color='white', fill_color='color')

    p_bar.y_range.start = 0
    p_bar.xgrid.grid_line_color = None
    p_bar.toolbar.logo = None
    p_bar.border_fill_color = None
    p_bar.outline_line_color = None
    p_bar.xaxis.major_label_orientation = 0.5 

    # ---------------------------------------------------------
    # Embed Components
    # ---------------------------------------------------------
    script, div_dict = components({'time_series': p_ts, 'bar_chart': p_bar})

    return render_template('main.html', 
                           bokeh_script=script, 
                           div_ts=div_dict['time_series'], 
                           div_bar=div_dict['bar_chart'],
                           kpi_value=kpi_revenue_display)

@app.route('/urban')
def urban_dashboard():
    """New Urban Sensors Dashboard."""
    df = load_urban_data()
    if df.empty: return "Error: Could not load urban data."

    # ---------------------------------------------------------
    # 1. KPI: Average Pollution Index (Social/Health Impact)
    # ---------------------------------------------------------
    avg_pollution = df['pollution_idx'].mean()
    kpi_display = f"{avg_pollution:.1f} AQI"

    # Insight Generation
    # Find the location with the highest noise
    noise_by_loc = df.groupby('location')['noise_db'].mean().sort_values(ascending=False)
    loudest_loc = noise_by_loc.index[0]
    loudest_val = noise_by_loc.iloc[0]
    
    insight_text = (f"The <strong>{loudest_loc}</strong> zone reports the highest noise pollution levels "
                    f"(avg {loudest_val:.1f} dB). Correlation analysis suggests a link between "
                    f"traffic density and local air quality variations.")

    # ---------------------------------------------------------
    # 2. Chart 1: Scatter Plot (Traffic vs Pollution)
    # ---------------------------------------------------------
    # Create a color map based on location
    locations = df['location'].unique().tolist()
    # Assign colors to rows
    palette = Spectral6
    color_map = {loc: palette[i % len(palette)] for i, loc in enumerate(locations)}
    df['color'] = df['location'].map(color_map)

    source_scatter = ColumnDataSource(df)

    p_scatter = figure(title="Impact of Traffic on Air Quality", height=350, sizing_mode="stretch_width",
                       tools="pan,wheel_zoom,box_zoom,reset,save",
                       x_axis_label="Vehicle Count (per hour)", y_axis_label="Pollution Index")
    
    p_scatter.circle(x='vehicle_count', y='pollution_idx', source=source_scatter,
                     size=8, fill_color='color', line_color='white', fill_alpha=0.6,
                     legend_group='location')
    
    p_scatter.add_tools(HoverTool(tooltips=[
        ("Location", "@location"),
        ("Traffic", "@vehicle_count vehicles"),
        ("Pollution", "@pollution_idx"),
        ("Time", "@ts{%H:%M}")
    ], formatters={"@ts": "datetime"}))
    
    p_scatter.toolbar.logo = None
    p_scatter.legend.title = "Zone"
    p_scatter.legend.location = "top_left"
    p_scatter.legend.background_fill_alpha = 0.4

    # ---------------------------------------------------------
    # 3. Chart 2: Bar Chart (Noise Levels by Zone)
    # ---------------------------------------------------------
    # Re-using the noise_by_loc series calculated earlier
    noise_df = noise_by_loc.reset_index()
    noise_df.columns = ['location', 'avg_noise']
    noise_df['color'] = noise_df['location'].map(color_map) # Keep consistent colors
    
    source_bar = ColumnDataSource(noise_df)

    p_bar = figure(x_range=noise_df['location'], title="Average Noise Pollution by Zone",
                   height=350, sizing_mode="stretch_width", tools="hover,save",
                   tooltips=[("Zone", "@location"), ("Avg Noise", "@avg_noise{0.1f} dB")],
                   y_axis_label="Decibels (dB)")

    p_bar.vbar(x='location', top='avg_noise', width=0.5, source=source_bar,
               line_color='white', fill_color='color')

    p_bar.y_range.start = 0
    p_bar.toolbar.logo = None
    p_bar.xgrid.grid_line_color = None

    # Embed
    script, div_dict = components({'scatter': p_scatter, 'bar': p_bar})

    return render_template('urban.html', bokeh_script=script,
                           div_scatter=div_dict['scatter'],
                           div_bar=div_dict['bar'],
                           kpi_value=kpi_display,
                           insight_text=insight_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=False)