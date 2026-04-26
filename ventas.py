import streamlit as st
import pandas as pd
import altair as alt

EXCEL_FILE_PATH = 'datos/SalidaVentas.xlsx'

# Load the dataset
@st.cache_data # Cache data to avoid reloading on every rerun
def load_data():
    try:
        # Assuming the Excel file will be accessible in the Streamlit environment
        df = pd.read_excel(EXCEL_FILE_PATH)
        # Ensure 'Order Date' is datetime for time-series plotting
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        return df
    except FileNotFoundError:
        st.error(f"Error: '{EXCEL_FILE_PATH}' not found. Please ensure the file exists in the deployment environment.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return pd.DataFrame()

df_sales = load_data()

# Streamlit app layout
st.set_page_config(layout='wide')
st.title('Análisis de Ventas por Región')

if not df_sales.empty:
    st.write('### Datos de Ventas - Resumen')
    st.dataframe(df_sales.head())

    # 1. Ventas Totales por Región
    st.write('---')
    st.write('### 1. Ventas Totales por Región')
    sales_by_region = df_sales.groupby('Region')['Sales'].sum().reset_index()
    chart_sales_region = alt.Chart(sales_by_region).mark_bar().encode(
        x=alt.X('Region', axis=alt.Axis(title='Región')),
        y=alt.Y('Sales', axis=alt.Axis(title='Ventas Totales (USD)')),
        tooltip=['Region', 'Sales']
    ).properties(title='Ventas Totales por Región').interactive()
    st.altair_chart(chart_sales_region, use_container_width=True)

    # 2. Ganancias Totales por Región
    st.write('---')
    st.write('### 2. Ganancias Totales por Región')
    profit_by_region = df_sales.groupby('Region')['Profit'].sum().reset_index()
    chart_profit_region = alt.Chart(profit_by_region).mark_bar().encode(
        x=alt.X('Region', axis=alt.Axis(title='Región')),
        y=alt.Y('Profit', axis=alt.Axis(title='Ganancias Totales (USD)')),
        color=alt.condition(alt.datum.Profit < 0, alt.value('red'), alt.value('green')), # Color negative profits red
        tooltip=['Region', 'Profit']
    ).properties(title='Ganancias Totales por Región').interactive()
    st.altair_chart(chart_profit_region, use_container_width=True)

    # 3. Ventas Diarias a lo Largo del Tiempo (Overall)
    st.write('---')
    st.write('### 3. Tendencia de Ventas Diarias')
    daily_sales = df_sales.groupby(pd.to_datetime(df_sales['Order Date']).dt.date)['Sales'].sum().reset_index()
    daily_sales['Order Date'] = pd.to_datetime(daily_sales['Order Date'])
    chart_daily_sales = alt.Chart(daily_sales).mark_line().encode(
        x=alt.X('Order Date', axis=alt.Axis(title='Fecha del Pedido')),
        y=alt.Y('Sales', axis=alt.Axis(title='Ventas Diarias (USD)')),
        tooltip=['Order Date', 'Sales']
    ).properties(title='Ventas Diarias a lo Largo del Tiempo').interactive()
    st.altair_chart(chart_daily_sales, use_container_width=True)

else:
    st.warning('No se pudieron cargar los datos. Por favor, revisa la ruta del archivo en el entorno de despliegue.')

# Save the Streamlit app to a Python file
streamlit_app_code = st.session_state.get('streamlit_app_code', '') # Get existing code if any
if not streamlit_app_code: # Only generate if not already set
    streamlit_app_code = '''
import streamlit as st
import pandas as pd
import altair as alt

EXCEL_FILE_PATH = 'SalidaVentas.xlsx' # User can modify this path, e.g., 'datos/SalidaVentas.xlsx'

# Load the dataset
@st.cache_data # Cache data to avoid reloading on every rerun
def load_data():
    try:
        # Assuming the Excel file will be accessible in the Streamlit environment
        df = pd.read_excel(EXCEL_FILE_PATH)
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        return df
    except FileNotFoundError:
        st.error(f"Error: '{EXCEL_FILE_PATH}' not found. Please ensure the file exists in the deployment environment.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return pd.DataFrame()

df_sales = load_data()

# Streamlit app layout
st.set_page_config(layout='wide')
st.title('Análisis de Ventas por Región')

if not df_sales.empty:
    st.write('### Datos de Ventas - Resumen')
    st.dataframe(df_sales.head())

    # 1. Ventas Totales por Región
    st.write('---')
    st.write('### 1. Ventas Totales por Región')
    sales_by_region = df_sales.groupby('Region')['Sales'].sum().reset_index()
    chart_sales_region = alt.Chart(sales_by_region).mark_bar().encode(
        x=alt.X('Region', axis=alt.Axis(title='Región')),
        y=alt.Y('Sales', axis=alt.Axis(title='Ventas Totales (USD)')),
        tooltip=['Region', 'Sales']
    ).properties(title='Ventas Totales por Región').interactive()
    st.altair_chart(chart_sales_region, use_container_width=True)

    # 2. Ganancias Totales por Región
    st.write('---')
    st.write('### 2. Ganancias Totales por Región')
    profit_by_region = df_sales.groupby('Region')['Profit'].sum().reset_index()
    chart_profit_region = alt.Chart(profit_by_region).mark_bar().encode(
        x=alt.X('Region', axis=alt.Axis(title='Región')),
        y=alt.Y('Profit', axis=alt.Axis(title='Ganancias Totales (USD)')),
        color=alt.condition(alt.datum.Profit < 0, alt.value('red'), alt.value('green')), # Color negative profits red
        tooltip=['Region', 'Profit']
    ).properties(title='Ganancias Totales por Región').interactive()
    st.altair_chart(chart_profit_region, use_container_width=True)

    # 3. Ventas Diarias a lo Largo del Tiempo (Overall)
    st.write('---')
    st.write('### 3. Tendencia de Ventas Diarias')
    daily_sales = df_sales.groupby(pd.to_datetime(df_sales['Order Date']).dt.date)['Sales'].sum().reset_index()
    daily_sales['Order Date'] = pd.to_datetime(daily_sales['Order Date'])
    chart_daily_sales = alt.Chart(daily_sales).mark_line().encode(
        x=alt.X('Order Date', axis=alt.Axis(title='Fecha del Pedido')),
        y=alt.Y('Sales', axis=alt.Axis(title='Ventas Diarias (USD)')),
        tooltip=['Order Date', 'Sales']
    ).properties(title='Ventas Diarias a lo Largo del Tiempo').interactive()
    st.altair_chart(chart_daily_sales, use_container_width=True)

else:
    st.warning('No se pudieron cargar los datos. Por favor, revisa la ruta del archivo en el entorno de despliegue.')
'''
    st.session_state['streamlit_app_code'] = streamlit_app_code

with open('sales_dashboard_app.py', 'w') as f:
    f.write(streamlit_app_code)

print('Streamlit app saved to sales_dashboard_app.py')
