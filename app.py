import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
local_arquivo = st.secrets["LOCAL_ARQUIVO_DADOS"]
df = pd.read_csv(local_arquivo)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# Filtro por Cargo
cargos_disponiveis = sorted(df['cargo'].unique())
cargos_selecionados = st.sidebar.multiselect("Cargo", cargos_disponiveis, default=cargos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados)) &
    (df['cargo'].isin(cargos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_minimo = df_filtrado['usd'].min()
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_minimo, salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, 0, ""

# Função para criar um "metric" customizado
def custom_metric(column, label, value):
    column.markdown(f'<p style="font-size: 14px; color: grey;">{label}</p>', unsafe_allow_html=True)
    column.markdown(f'<p style="font-size: 24px; font-weight: bold;">{value}</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
# Aplica a função para cada coluna
custom_metric(col1, "Salário mínimo", f"${salario_minimo:,.0f}")
custom_metric(col2, "Salário médio", f"${salario_medio:,.0f}")
custom_metric(col3, "Salário máximo", f"${salario_maximo:,.0f}")
custom_metric(col4, "Total de registros", f"{total_registros:,}")

# Para o cargo, o tamanho da fonte precisa ser dinâmico
cargo = cargo_mais_frequente
font_size = 24  # Tamanho da fonte padrão
if len(cargo) > 15: # Exemplo de lógica para diminuir a fonte
    font_size = 18

col5.markdown(f'<p style="font-size: 14px; color: grey;">Cargo mais frequente</p>', unsafe_allow_html=True)
col5.markdown(f'<p style="font-size: {font_size}px; font-weight: bold;">{cargo}</p>', unsafe_allow_html=True)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('pais_empresa_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='pais_empresa_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país da empresa',
            labels={'usd': 'Salário médio (USD)', 'pais_empresa_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

#col_graf5 = st.columns(2)

#ith col_graf5:
if not df_filtrado.empty:
    top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
    # Título longo
    titulo_do_grafico = "Top 10 cargos por salário médio (com ajuste dinâmico do tamanho da fonte)"

    # Lógica para ajustar o tamanho da fonte dinamicamente
    font_size = 20  # Tamanho padrão
    if len(titulo_do_grafico) > 50:
        font_size = 14

    grafico_cargos = px.bar(
        top_cargos,
        x='usd',
        y='cargo',
        orientation='h',
        labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
    )
    grafico_cargos.update_layout(
        title_x=0.1,
        yaxis={'categoryorder':'total ascending'},
        title={
            'text': titulo_do_grafico,
            'font': {'size': font_size}
        }
    )
    st.plotly_chart(grafico_cargos)
else:
    st.warning("Nenhum dado para exibir no gráfico de cargos.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)