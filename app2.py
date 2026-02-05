import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Energy Consumption Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #667eea;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>⚡ Energy Consumption Dashboard</h1>", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    """Load and process energy consumption data"""
    try:
        df = pd.read_csv('data.csv')
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df['Date'] = df['DateTime'].dt.date
        df['Hour'] = df['DateTime'].dt.hour
        df['Month'] = df['DateTime'].dt.to_period('M').astype(str)
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Week'] = df['DateTime'].dt.isocalendar().week
        return df
    except FileNotFoundError:
        st.error("❌ Error: data.csv file not found. Please ensure it's in the same directory as this script.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("📊 Filters & Options")

# Customer selection
customers = ['Customer_1', 'Customer_2', 'Customer_3', 'Customer_4']
selected_customers = st.sidebar.multiselect(
    "Select Customers",
    customers,
    default=customers,
    help="Choose which customers to display"
)

# Date range filter
min_date = df['Date'].min()
max_date = df['Date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Filter data by date range"
)

# Apply filters
if len(date_range) == 2:
    filtered_df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]
else:
    filtered_df = df

# Visualization options
st.sidebar.header("🎨 Visualization Options")
show_raw_data = st.sidebar.checkbox("Show Raw Data", value=False)
chart_theme = st.sidebar.selectbox("Chart Theme", ["plotly", "plotly_dark", "plotly_white"])

# Color scheme for customers
colors = {
    'Customer_1': '#FF6384',
    'Customer_2': '#36A2EB',
    'Customer_3': '#FFCE56',
    'Customer_4': '#4BC0C0'
}

# Summary Statistics Section
st.header("📈 Summary Statistics")

if selected_customers:
    cols = st.columns(len(selected_customers))
    
    for idx, customer in enumerate(selected_customers):
        with cols[idx]:
            total = filtered_df[customer].sum()
            avg = filtered_df[customer].mean()
            max_val = filtered_df[customer].max()
            min_val = filtered_df[customer].min()
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {colors[customer]} 0%, {colors[customer]}CC 100%); 
                            padding: 20px; border-radius: 10px; color: white; margin: 5px;'>
                    <h3 style='margin: 0; color: white;'>{customer.replace('_', ' ')}</h3>
                    <h2 style='margin: 10px 0; color: white;'>{total:,.2f} kWh</h2>
                    <p style='margin: 5px 0;'><strong>Avg:</strong> {avg:.2f} kWh</p>
                    <p style='margin: 5px 0;'><strong>Max:</strong> {max_val:.2f} kWh</p>
                    <p style='margin: 5px 0;'><strong>Min:</strong> {min_val:.2f} kWh</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Key Metrics Row
    st.header("🔑 Key Insights")
    
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        total_consumption = filtered_df[selected_customers].sum().sum()
        st.metric("Total Consumption", f"{total_consumption:,.2f} kWh", 
                 help="Total energy consumed by all selected customers")
    
    with metric_cols[1]:
        avg_hourly = filtered_df[selected_customers].mean().mean()
        st.metric("Average Hourly", f"{avg_hourly:.2f} kWh",
                 help="Average hourly consumption across all customers")
    
    with metric_cols[2]:
        peak_hour = filtered_df.groupby('Hour')[selected_customers].sum().sum(axis=1).idxmax()
        st.metric("Peak Hour", f"{peak_hour}:00",
                 help="Hour with highest consumption")
    
    with metric_cols[3]:
        peak_customer = filtered_df[selected_customers].sum().idxmax()
        st.metric("Top Consumer", peak_customer.replace('_', ' '),
                 help="Customer with highest total consumption")

    st.markdown("---")

    # Visualization Section
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Comparison", 
        "🕐 Hourly Pattern", 
        "📅 Daily Trends",
        "📆 Monthly Analysis",
        "📈 Weekly Pattern",
        "🔥 Heatmap"
    ])

    with tab1:
        st.subheader("Total Consumption Comparison")
        
        # Bar chart
        comparison_data = filtered_df[selected_customers].sum().reset_index()
        comparison_data.columns = ['Customer', 'Total Consumption (kWh)']
        comparison_data['Customer'] = comparison_data['Customer'].str.replace('_', ' ')
        
        fig_comparison = px.bar(
            comparison_data,
            x='Customer',
            y='Total Consumption (kWh)',
            color='Customer',
            color_discrete_map={c.replace('_', ' '): colors[c] for c in selected_customers},
            template=chart_theme,
            title="Total Energy Consumption by Customer"
        )
        fig_comparison.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Pie chart
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(
                comparison_data,
                values='Total Consumption (kWh)',
                names='Customer',
                color='Customer',
                color_discrete_map={c.replace('_', ' '): colors[c] for c in selected_customers},
                template=chart_theme,
                title="Consumption Share"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Statistics table
            stats_df = filtered_df[selected_customers].agg(['sum', 'mean', 'std', 'min', 'max']).T
            stats_df.columns = ['Total', 'Average', 'Std Dev', 'Min', 'Max']
            stats_df.index = stats_df.index.str.replace('_', ' ')
            st.dataframe(stats_df.style.format("{:.2f}"), use_container_width=True)

    with tab2:
        st.subheader("Average Hourly Consumption Pattern")
        
        hourly_data = filtered_df.groupby('Hour')[selected_customers].mean().reset_index()
        
        fig_hourly = go.Figure()
        for customer in selected_customers:
            fig_hourly.add_trace(go.Scatter(
                x=hourly_data['Hour'],
                y=hourly_data[customer],
                name=customer.replace('_', ' '),
                mode='lines+markers',
                line=dict(color=colors[customer], width=3),
                marker=dict(size=8)
            ))
        
        fig_hourly.update_layout(
            template=chart_theme,
            title="24-Hour Consumption Pattern",
            xaxis_title="Hour of Day",
            yaxis_title="Average Consumption (kWh)",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Peak hours for each customer
        st.subheader("Peak Consumption Hours")
        peak_cols = st.columns(len(selected_customers))
        for idx, customer in enumerate(selected_customers):
            with peak_cols[idx]:
                peak_hour = hourly_data.loc[hourly_data[customer].idxmax(), 'Hour']
                peak_value = hourly_data[customer].max()
                st.metric(
                    customer.replace('_', ' '),
                    f"{int(peak_hour)}:00",
                    f"{peak_value:.2f} kWh"
                )

    with tab3:
        st.subheader("Daily Consumption Trends")
        
        daily_data = filtered_df.groupby('Date')[selected_customers].sum().reset_index()
        
        fig_daily = go.Figure()
        for customer in selected_customers:
            fig_daily.add_trace(go.Scatter(
                x=daily_data['Date'],
                y=daily_data[customer],
                name=customer.replace('_', ' '),
                mode='lines',
                line=dict(color=colors[customer], width=2),
                fill='tonexty' if customer != selected_customers[0] else None
            ))
        
        fig_daily.update_layout(
            template=chart_theme,
            title="Daily Energy Consumption Over Time",
            xaxis_title="Date",
            yaxis_title="Daily Consumption (kWh)",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Rolling average
        st.subheader("7-Day Rolling Average")
        daily_data_rolling = daily_data.copy()
        for customer in selected_customers:
            daily_data_rolling[f'{customer}_rolling'] = daily_data_rolling[customer].rolling(window=7).mean()
        
        fig_rolling = go.Figure()
        for customer in selected_customers:
            fig_rolling.add_trace(go.Scatter(
                x=daily_data_rolling['Date'],
                y=daily_data_rolling[f'{customer}_rolling'],
                name=customer.replace('_', ' '),
                mode='lines',
                line=dict(color=colors[customer], width=2)
            ))
        
        fig_rolling.update_layout(
            template=chart_theme,
            xaxis_title="Date",
            yaxis_title="7-Day Avg Consumption (kWh)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_rolling, use_container_width=True)

    with tab4:
        st.subheader("Monthly Consumption Analysis")
        
        monthly_data = filtered_df.groupby('Month')[selected_customers].sum().reset_index()
        
        # Stacked bar chart
        fig_monthly = go.Figure()
        for customer in selected_customers:
            fig_monthly.add_trace(go.Bar(
                x=monthly_data['Month'],
                y=monthly_data[customer],
                name=customer.replace('_', ' '),
                marker_color=colors[customer]
            ))
        
        fig_monthly.update_layout(
            template=chart_theme,
            title="Monthly Energy Consumption",
            xaxis_title="Month",
            yaxis_title="Total Consumption (kWh)",
            barmode='group',
            height=500
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Month-over-month growth
        st.subheader("Month-over-Month Change (%)")
        monthly_pct_change = monthly_data[selected_customers].pct_change() * 100
        monthly_pct_change['Month'] = monthly_data['Month']
        
        fig_mom = px.line(
            monthly_pct_change,
            x='Month',
            y=selected_customers,
            template=chart_theme,
            markers=True
        )
        fig_mom.update_layout(
            yaxis_title="Change (%)",
            height=400
        )
        st.plotly_chart(fig_mom, use_container_width=True)

    with tab5:
        st.subheader("Weekly Pattern Analysis")
        
        # Day of week pattern
        dow_data = filtered_df.groupby('DayOfWeek')[selected_customers].mean()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data = dow_data.reindex(dow_order).reset_index()
        
        fig_dow = px.bar(
            dow_data,
            x='DayOfWeek',
            y=selected_customers,
            template=chart_theme,
            title="Average Consumption by Day of Week",
            barmode='group',
            color_discrete_map=colors
        )
        fig_dow.update_layout(height=500)
        st.plotly_chart(fig_dow, use_container_width=True)
        
        # Weekly totals
        weekly_data = filtered_df.groupby('Week')[selected_customers].sum().reset_index()
        
        fig_weekly = go.Figure()
        for customer in selected_customers:
            fig_weekly.add_trace(go.Scatter(
                x=weekly_data['Week'],
                y=weekly_data[customer],
                name=customer.replace('_', ' '),
                mode='lines',
                line=dict(color=colors[customer], width=2)
            ))
        
        fig_weekly.update_layout(
            template=chart_theme,
            title="Weekly Consumption Trends",
            xaxis_title="Week Number",
            yaxis_title="Weekly Consumption (kWh)",
            height=400
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

    with tab6:
        st.subheader("Consumption Heatmap")
        
        # Select customer for heatmap
        heatmap_customer = st.selectbox("Select Customer for Heatmap", selected_customers)
        
        # Create pivot table for heatmap
        heatmap_data = filtered_df.pivot_table(
            values=heatmap_customer,
            index=filtered_df['DateTime'].dt.hour,
            columns=filtered_df['DateTime'].dt.day_name(),
            aggfunc='mean'
        )
        
        # Reorder columns
        heatmap_data = heatmap_data[dow_order]
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Day of Week", y="Hour of Day", color="Consumption (kWh)"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="RdYlBu_r",
            template=chart_theme,
            title=f"{heatmap_customer.replace('_', ' ')} - Hour vs Day Heatmap"
        )
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Monthly heatmap
        st.subheader("Monthly-Hour Heatmap")
        monthly_hour_data = filtered_df.pivot_table(
            values=heatmap_customer,
            index=filtered_df['DateTime'].dt.hour,
            columns=filtered_df['DateTime'].dt.month,
            aggfunc='mean'
        )
        
        fig_monthly_heatmap = px.imshow(
            monthly_hour_data,
            labels=dict(x="Month", y="Hour of Day", color="Consumption (kWh)"),
            color_continuous_scale="Viridis",
            template=chart_theme,
            title=f"{heatmap_customer.replace('_', ' ')} - Monthly Pattern"
        )
        fig_monthly_heatmap.update_layout(height=600)
        st.plotly_chart(fig_monthly_heatmap, use_container_width=True)

    # Raw data display
    if show_raw_data:
        st.markdown("---")
        st.header("📋 Raw Data")
        
        display_columns = ['DateTime'] + selected_customers
        st.dataframe(
            filtered_df[display_columns].style.format({
                customer: "{:.2f}" for customer in selected_customers
            }),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df[display_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"energy_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    st.warning("⚠️ Please select at least one customer from the sidebar to view data.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>⚡ Energy Consumption Dashboard | Built with Streamlit</p>
        <p>Data updated in real-time | Interactive visualizations with Plotly</p>
    </div>
""", unsafe_allow_html=True)