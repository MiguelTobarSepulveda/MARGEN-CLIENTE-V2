
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

# Unir código y descripción para mostrar en el filtro de producto
ventas["PRODUCTO COMPLETO"] = ventas["CODIGO PRODUCTO"] + " - " + ventas["PRODUCTO"]
productos = sorted(ventas["PRODUCTO COMPLETO"].unique())

mes_sel = st.selectbox("Selecciona el mes", ["Todos"] + meses)
cli_sel = st.selectbox("Selecciona el cliente", ["Todos"] + clientes)
prod_sel = st.selectbox("Selecciona el producto", ["Todos"] + productos)

# Extraer código producto desde el combinado si se selecciona uno
if prod_sel != "Todos":
    prod_sel_codigo = prod_sel.split(" - ")[0]
else:
    prod_sel_codigo = "Todos"

# Aplicar filtros
df = ventas.copy()
if mes_sel != "Todos":
    df = df[df["MES"] == mes_sel]
if cli_sel != "Todos":
    df = df[df["CLIENTE"] == cli_sel]
if prod_sel_codigo != "Todos":
    df = df[df["CODIGO PRODUCTO"] == prod_sel_codigo]

# Preparar insumos con precio 0 si falta, insumo faltante = 0
recetas = recetas.merge(insumos, on="CODIGO INSUMO", how="left")
recetas["PRECIO"] = recetas["PRECIO"].fillna(0)
recetas["COSTO_UNITARIO"] = recetas["CANTIDAD"] * recetas["PRECIO"]
costos_prod = recetas.groupby("CODIGO PRODUCTO")["COSTO_UNITARIO"].sum().reset_index()

# Unir con ventas
df = df.merge(costos_prod, on="CODIGO PRODUCTO", how="left")
df["COSTO_UNITARIO"] = df["COSTO_UNITARIO"].fillna(0)
df["INGRESO TOTAL"] = df["CANTIDAD"] * df["PRECIO UNITARIO"]
df["COSTO TOTAL"] = df["CANTIDAD"] * df["COSTO_UNITARIO"]
df["MARGEN $"] = df["INGRESO TOTAL"] - df["COSTO TOTAL"]
df["MARGEN %"] = df["MARGEN $"] / df["INGRESO TOTAL"]
df["MARGEN %"] = df["MARGEN %"].fillna(0)

# KPIs
st.subheader("Indicadores")
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Netas", f"$ {df['INGRESO TOTAL'].sum():,.0f}")
col2.metric("Costo Total", f"$ {df['COSTO TOTAL'].sum():,.0f}")
col3.metric("Margen Promedio", f"{(df['MARGEN %'].mean()*100):.1f} %")

# Mostrar tabla
st.subheader("Detalle por Factura")
st.dataframe(df[[
    "NÚMERO", "FECHA", "CLIENTE", "PRODUCTO", "CANTIDAD",
    "PRECIO UNITARIO", "INGRESO TOTAL", "COSTO TOTAL", "MARGEN $", "MARGEN %"
]])
