###   IMPORTACION DE LIBRERIAS Y CONFIGURACION DE LA APLICACION###
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

# Configuramos los gráficos
pio.templates.default = "plotly_white"

### PREPROCESAMIENTO DE DATOS ###

# Importamos los datos
df = pd.read_csv(".\housing_data_CDMX_v2.csv")

# Calculamos tipo de cambio MXN a USD
tipo_cambio = (df['price_aprox_local_currency'] / df['price_aprox_usd']).mean()

# Convertimos a pesos mexicanos los precios en USD
df['price'] = df['price'].where(
    df['currency'] == 'MXN', df['price'] * tipo_cambio)
df['price_per_m2'] = df['price_per_m2'].where(
    df['currency'] == 'MXN', df['price_per_m2'] * tipo_cambio)

# Borramos las columnas lat, lon y lat-lon
df = df.drop(columns=['lat', 'lon', 'lat-lon'])

# Borramos las columnas con datos en USD
df = df.drop(columns=['price_aprox_usd', 'price_usd_per_m2'])

# Eliminamos los outliers de las columnas precio por metro cuadrado y superficie total
# Hacemos esto para mejorar la visualización de los datos
numeric_cols = ['price_per_m2', 'surface_total_in_m2']
for col in numeric_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


### INTERFAZ DE LA APLICACION ###

st.title("Análisis de Precios de Viviendas en la Ciudad de México")

menu = {
    "Distribución de Precios por Tipo de Vivienda": 1,
    "Precio Promedio por Tipo de Vivienda": 2,
    "Precio Promedio por Delegación": 3,
    "Distribución de Precios por Delegación": 4,
    "Relación entre Superficie Total y Precio": 5,
    "Relación entre Superficie Total y Precio por Metro Cuadrado": 6
}

grafico = st.sidebar.radio(
    "Selecciona el gráfico que deseas ver:", menu.keys())

seleccion = menu[grafico]

if seleccion == 1:
    st.subheader("Distribución de Precios por Tipo de Vivienda")
    # Determinamos el precio máximo y mínimo para el slider
    min_price = int(df['price'].min())
    max_price = int(df['price'].max())
    rango = st.slider("Selecciona el rango de precios (MXN)",
                      min_price, max_price, (min_price, max_price), step=1000, format="$%d")
    df_filtered = df[(df['price'] >= rango[0]) & (df['price'] <= rango[1])]
    # Histograma de precios por tipo de vivienda
    fig = px.histogram(df_filtered, x='price', nbins=50,
                       title='Distribución de Precios por Tipo de Vivienda en CDMX',
                       labels={'price': 'Precio (MXN)'}, range_x=[rango[0], rango[1]], color='property_type')
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Cantidad de Propiedades')
    # Cambiamos el nombre de las leyendas
    fig.update_layout(legend_title_text='Tipo de Vivienda')
    st.plotly_chart(fig)

elif seleccion == 2:
    st.subheader("Precio Promedio por Tipo de Vivienda")
    # Cremaos una gráfico para mostrar el precio promedio por tipo de vivienda
    avg_price_by_type = df.groupby(
        'property_type')['price_aprox_local_currency'].mean().reset_index()
    fig = px.bar(avg_price_by_type, x='property_type', y='price_aprox_local_currency',
                 title='Precio Promedio por Tipo de Vivienda en CDMX',
                 labels={'property_type': 'Tipo de Vivienda', 'price_aprox_local_currency': 'Precio Promedio (MXN)'})
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Precio Promedio (MXN)')
    st.plotly_chart(fig)


elif seleccion == 3:
    st.subheader("Precio Promedio por Delegación")
    # Grafico precio promedio por delegación
    avg_price_by_place = df.groupby(
        'places')['price_aprox_local_currency'].mean().reset_index()
    fig = px.bar(avg_price_by_place, x='places', y='price_aprox_local_currency',
                 title='Precio Promedio por Delegación en CDMX',
                 labels={'places': 'Delegación', 'price_aprox_local_currency': 'Precio Promedio (MXN)'})
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Precio Promedio (MXN)')
    st.plotly_chart(fig)


elif seleccion == 4:
    st.subheader("Distribución de Precios por Delegación")
    # Determinamos el precio máximo y mínimo para el slider
    min_price = int(df['price'].min())
    max_price = int(df['price'].max())
    rango = st.slider("Selecciona el rango de precios (MXN)",
                      min_price, max_price, (min_price, max_price), step=1000, format="$%d")
    df_filtered = df[(df['price'] >= rango[0]) & (df['price'] <= rango[1])]
    # Histograma de precios por delegación
    fig = px.histogram(df_filtered, x='price_aprox_local_currency', nbins=50, title='Distribución de Precios por Delegación en CDMX',
                       labels={'price_aprox_local_currency': 'Precio (MXN)'}, range_x=[rango[0], rango[1]], color='places')
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Cantidad de Propiedades')
    # Cambiamos el nombre de las leyendas
    fig.update_layout(legend_title_text='Delegación')
    st.plotly_chart(fig)


elif seleccion == 5:
    st.subheader("Relación entre Superficie Total y Precio")
    # Diagrama de dispersion entre precio y superficie total
    fig = px.scatter(df, x='surface_total_in_m2', y='price_aprox_local_currency',
                     title='Relación entre Superficie Total y Precio en CDMX',
                     labels={'surface_total_in_m2': 'Superficie Total (m²)', 'price_aprox_local_currency': 'Precio (MXN)'})
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Precio (MXN)')
    # Cambiamos el nombre del eje x
    fig.update_layout(xaxis_title='Superficie Total (m²)')
    fig.update_layout(width=600, height=700)
    st.plotly_chart(fig)


elif seleccion == 6:
    st.subheader("Relación entre Superficie Total y Precio por Metro Cuadrado")
    # Diagrama de dispersion entre precio por metro cuadrado y superficie total
    fig = px.scatter(df, x='surface_total_in_m2', y='price_per_m2',
                     title='Relación entre Superficie Total y Precio por Metro Cuadrado en CDMX',
                     labels={'surface_total_in_m2': 'Superficie Total (m²)', 'price_per_m2': 'Precio por Metro Cuadrado (MXN)'})
    # Cambiamos el nombre del eje y
    fig.update_layout(yaxis_title='Precio por Metro Cuadrado (MXN)')
    # Cambiamos el nombre del eje x
    fig.update_layout(xaxis_title='Superficie Total (m²)')
    fig.update_layout(width=600, height=700)
    st.plotly_chart(fig)

### FIN DE LA APLICACION ###
