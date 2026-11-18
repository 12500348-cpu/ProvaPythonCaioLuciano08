import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Gráficos", page_icon="📊", layout="wide")
st.title("📊 Gerador de Gráficos")

# ---------- Dados ----------
arquivo = st.sidebar.file_uploader("bd_iqvu_1994_2016.csv)", type=["csv", "xlsx", "xls"])

df = pd.read_csv("bd_iqvu_1994_2016.csv", sep=";", encoding="latin-1",
decimal=",")
df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

@st.cache_data
def carregar(arq):
    if arq.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(arq, sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            arq.seek(0)
            return pd.read_csv(arq, sep=None, engine="python", encoding="latin-1")
    return pd.read_excel(arq)


def exemplo():
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return pd.DataFrame({
        "Mês": meses * 2,
        "Tipo": ["Receita"] * 12 + ["Despesa"] * 12,
        "Valor": [5200, 4800, 6100, 5900, 6500, 7000, 6800, 7200, 7500, 7100, 7900, 8400,
                  3100, 3300, 3500, 3200, 3600, 3900, 4100, 3800, 4000, 4200, 4300, 4600],
    })


if arquivo:
    df = carregar(arquivo)
    st.sidebar.success(f"{len(df)} linhas carregadas")
else:
    df = exemplo()
    st.info("Usando dados de exemplo. Envie sua planilha na barra lateral.")

# ---------- Configuração ----------
colunas = list(df.columns)
numericas = df.select_dtypes("number").columns.tolist()

if not numericas:
    st.error("A planilha precisa ter pelo menos uma coluna numérica.")
    st.stop()

st.sidebar.header("Configurar gráfico")
tipo = st.sidebar.selectbox("Tipo", ["Barras", "Linhas", "Área", "Pizza", "Dispersão"])
x = st.sidebar.selectbox("Eixo X / Categoria", colunas, index=0)
y = st.sidebar.selectbox("Valor (Y)", numericas, index=len(numericas) - 1)
opcoes_cor = ["(nenhuma)"] + [c for c in colunas if c not in (x, y)]
cor = st.sidebar.selectbox("Separar por (cor)", opcoes_cor)
cor = None if cor == "(nenhuma)" else cor
agregacao = st.sidebar.selectbox("Agregação", ["Soma", "Média", "Contagem", "Máximo", "Mínimo", "Nenhuma"])

# ---------- Agregar ----------
funcs = {"Soma": "sum", "Média": "mean", "Contagem": "count", "Máximo": "max", "Mínimo": "min"}
if agregacao != "Nenhuma" and tipo != "Dispersão":
    grupos = [x] + ([cor] if cor else [])
    dados = df.groupby(grupos, sort=False, as_index=False)[y].agg(funcs[agregacao])
else:
    dados = df

# ---------- Métricas ----------
c1, c2, c3 = st.columns(3)
c1.metric("Total", f"{df[y].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Média", f"{df[y].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Registros", len(df))

# ---------- Gráfico ----------
titulo = f"{y} por {x}"
if tipo == "Barras":
    fig = px.bar(dados, x=x, y=y, color=cor, barmode="group", title=titulo, text_auto=".2s")
elif tipo == "Linhas":
    fig = px.line(dados, x=x, y=y, color=cor, markers=True, title=titulo)
elif tipo == "Área":
    fig = px.area(dados, x=x, y=y, color=cor, title=titulo)
elif tipo == "Pizza":
    fig = px.pie(dados, names=x, values=y, title=titulo, hole=0.4)
else:
    fig = px.scatter(dados, x=x, y=y, color=cor, title=titulo)

fig.update_layout(height=520, margin=dict(t=60, l=20, r=20, b=20))
st.plotly_chart(fig, use_container_width=True)

# ---------- Tabela ----------
with st.expander("Ver dados"):
    st.dataframe(dados, use_container_width=True)
    st.download_button("Baixar CSV", dados.to_csv(index=False).encode("utf-8"),
                       "dados_grafico.csv", "text/csv")
