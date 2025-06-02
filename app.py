
import streamlit as st
import pandas as pd

# Cargar datos
@st.cache_data
def load_data():
    ventas = pd.read_excel("Base_Margenes.xlsx", sheet_name="LIBRO DE VENTAS")
    recetas = pd.read_excel("Base_Margenes.xlsx", sheet_name="RECETAS DE PRODUCTOS")
    insumos = pd.read_excel("Base_Margenes.xlsx", sheet_name="PRECIO DE INSUMOS")
    return ventas, recetas, insumos

ventas, recetas, insumos = load_data()

# Título
st.title("Consulta de Márgenes por Cliente y Producto")

# Filtros
ventas["MES"] = pd.to_datetime(ventas["FECHA"]).dt.to_period("M").astype(str)
meses = sorted(ventas["MES"].unique())
clientes = sorted(ventas["CLIENTE"].unique())
productos = sorted(ventas["CODIGO PRODUCTO"].unique())

mes_sel = st.selectbox("Selecciona el mes", ["Todos"] + meses)
cli_sel = st.selectbox("Selecciona el cliente", ["Todos"] + clientes)
prod_sel = st.selectbox("Selecciona el producto", ["Todos"] + productos)

# Aplicar filtros
df = ventas.copy()
if mes_sel != "Todos":
    df = df[df["MES"] == mes_sel]
if cli_sel != "Todos":
    df = df[df["CLIENTE"] == cli_sel]
if prod_sel != "Todos":
    df = df[df["CODIGO PRODUCTO"] == prod_sel]

# Calcular Costo Unitario por producto
recetas = recetas.merge(insumos, on="CODIGO INSUMO", how="left")
recetas["COSTO_UNITARIO"] = recetas["CANTIDAD"] * recetas["PRECIO"]
costos_prod = recetas.groupby("CODIGO PRODUCTO")["COSTO_UNITARIO"].sum().reset_index()

# Unir con ventas
df = df.merge(costos_prod, on="CODIGO PRODUCTO", how="left")
df["INGRESO TOTAL"] = df["CANTIDAD"] * df["PRECIO UNITARIO"]
df["COSTO TOTAL"] = df["CANTIDAD"] * df["COSTO_UNITARIO"]
df["MARGEN"] = df["INGRESO TOTAL"] - df["COSTO TOTAL"]

# KPIs
st.subheader("Indicadores")
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Netas", f"$ {df['INGRESO TOTAL'].sum():,.0f}")
col2.metric("Costo Total", f"$ {df['COSTO TOTAL'].sum():,.0f}")
col3.metric("Margen Total", f"$ {df['MARGEN'].sum():,.0f}")

# Mostrar tabla
st.subheader("Detalle por Factura")
st.dataframe(df[[
    "NÚMERO", "FECHA", "CLIENTE", "CODIGO PRODUCTO", "CANTIDAD",
    "PRECIO UNITARIO", "INGRESO TOTAL", "COSTO TOTAL", "MARGEN"
]])
