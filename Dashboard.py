import streamlit as st                          # Streamlit - to build the web app
import pandas as pd                             # Pandas - to read and manage the data
import plotly.express as px                     # Plotly - to create graphs and charts

# Set wide page layout and title early
# This sets the title to the page and makes the layout wide so everything fits nicely on the screen
st.set_page_config(page_title="Dengue Dashboard", layout="wide")

# Load data
# This line loads our dengue data from a CSV file
# If there's an error (like missing file), the app shows a message
DATA_PATH = "ph_dengue_cases_cleaned_2016-2020.csv"
try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

# Month to number mapping
month_mapping = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# Create Month_Num column
# Adds a new column to the table called Month_Num, where each month name is replaced with its number (e.g., January → 1)
df['Month_Num'] = df['Month'].map(month_mapping)

# Title and Key Stats
# This part shows the title of our dashboard and the total dengue cases and total deaths
st.title("🦟 Dengue Cases and Deaths in the Philippines (2016–2020)")
total_cases = df['Dengue_Cases'].sum()
total_deaths = df['Dengue_Deaths'].sum()
col1, col2 = st.columns(2)
col1.metric("Total Cases", f"{total_cases:,}")
col2.metric("Total Deaths", f"{total_deaths:,}")

# --- Filters on main page ---
# This part users can choose which region, year, and month they want to see and choose/select what to display: Dengue Cases, Dengue Deaths, or both
st.markdown("### 🎯 Filter Data to View")
colf1, colf2, colf3 = st.columns(3)               #Adds a section heading and creates 3 columns for filters: region, year, and month.

selected_regions = colf1.multiselect("Select Region(s)", sorted(df['Region'].unique())) 
selected_years = colf2.multiselect("Select Year(s)", sorted(df['Year'].unique()))
selected_months = colf3.multiselect("Select Month(s)", list(month_mapping.keys())) # Lets the user choose one or more regions, years, and months to filter the data.

# Radio buttons to let the user choose whether to show cases, deaths, or both. Default is -- Select -- which means no chart is shown until user picks an option.
data_view_option = st.radio(
    "Choose what to display:",
    ['-- Select --', 'Dengue Cases', 'Dengue Deaths', 'Both'],
    index=0,
    horizontal=True
)

# --- Sidebar: Add New Data ---
# This part on the left sidebar of our dashboard lets users enter new data like Region, Year, Month, Number of Cases, and Number of Deaths
st.sidebar.header("➕ Add New Dengue Data") # Adds a sidebar title for the form to manually input new dengue data.

regions_with_empty = ["-- Select Region --"] + sorted(df['Region'].unique())
new_region = st.sidebar.selectbox("Region", regions_with_empty, index=0)  # Creates a dropdown in the sidebar for selecting a region.First option is a placeholder ("-- Select Region --").

years_with_empty = ["-- Select Year --"] + [str(y) for y in range(2010, 2031)]  # Year selector with options from 2010 to 2030 and a default empty option.
new_year = st.sidebar.selectbox("Year", years_with_empty, index=0)

months_with_empty = ["-- Select Month --"] + list(month_mapping.keys())  # Month selector with all month names and a default empty option.
new_month = st.sidebar.selectbox("Month", months_with_empty, index=0)

new_cases = st.sidebar.number_input("Cases", min_value=0, value=0)    
new_deaths = st.sidebar.number_input("Deaths", min_value=0, value=0) # Allows the user to type in the number of new cases and deaths.

if st.sidebar.button("Add Data"): # hen the "Add Data" button is clicked
    # If the user hasn't selected valid values, show an error in the sidebar.
    if new_region == "-- Select Region --" or new_month == "-- Select Month --" or new_year == "-- Select Year --":
        st.sidebar.error("Please select valid Region, Year, and Month before adding data.")
    else:
        # If valid inputs are given, build a dictionary with the new row of data.
        new_data = {
            "Region": new_region,
            "Year": int(new_year),
            "Month": new_month,
            "Dengue_Cases": new_cases,
            "Dengue_Deaths": new_deaths
        }
        # Converts the new data into a DataFrame, maps the month number, and adds it to the existing table (df)
        new_row = pd.DataFrame([new_data])
        new_row['Month_Num'] = new_row['Month'].map(month_mapping)
        df = pd.concat([df, new_row], ignore_index=True)
        st.sidebar.success("✅ New data added successfully! Please update filters to view.")

# --- Main Page Content ---
# This part shows graphs based on the data the user selects. It helps them clearly see trends and compare data easily.
if selected_regions and selected_years:
    filtered_df = df[df['Region'].isin(selected_regions) & df['Year'].isin(selected_years)]
    if selected_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]

    if data_view_option == '-- Select --':
        st.info("👉 Please select what to display: Dengue Cases, Deaths, or Both.") # If no display option is chosen, show a reminder to the user.
    else:
        # Groups the filtered data by year and region and sums the cases and deaths to prepare for plotting.
        yearly_grouped = filtered_df.groupby(['Year', 'Region'], as_index=False).agg({        
            'Dengue_Cases': 'sum',
            'Dengue_Deaths': 'sum'
        })

        # If the user wants to see cases (or both), this creates a bar chart showing dengue cases by year and region.
        if data_view_option in ['Dengue Cases', 'Both']:
            st.subheader("📈 Dengue Cases by Year and Region")
            fig_cases = px.bar(
                yearly_grouped,
                x='Year',
                y='Dengue_Cases',
                color='Region',
                barmode='group',
                labels={'Dengue_Cases': 'Cases', 'Year': 'Year'},
                title="Yearly Dengue Cases by Region"
            )
            fig_cases.update_xaxes(type='category')
            st.plotly_chart(fig_cases, use_container_width=True)

        # If the user wants to see deaths (or both), this creates a similar bar chart for dengue deaths.
        if data_view_option in ['Dengue Deaths', 'Both']:
            st.subheader("📉 Dengue Deaths by Year and Region")
            fig_deaths = px.bar(
                yearly_grouped,
                x='Year',
                y='Dengue_Deaths',
                color='Region',
                barmode='group',
                labels={'Dengue_Deaths': 'Deaths', 'Year': 'Year'},
                title="Yearly Dengue Deaths by Region"
            )
            fig_deaths.update_xaxes(type='category')
            st.plotly_chart(fig_deaths, use_container_width=True)
else:
    st.info("📊 Showing all data. Use filters above to narrow down.") #  If the user hasn’t selected region and year, remind them to use filters. Meanwhile, show the full table below.

# --- Dengue Data Table ---
# This displays the full dengue data table at the bottom of our dashboard, sorted first by year, then by month number, and removes the helper column Month_Num from display.
st.subheader("📋 Dengue Data Table")
sorted_df = df.sort_values(by=["Year", "Month_Num"]).drop(columns=["Month_Num"])
st.dataframe(sorted_df, use_container_width=True)