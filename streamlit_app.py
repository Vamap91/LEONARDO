import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Dashboard CEFET-MG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores personalizadas
CEFET_BLUE = "#003366"
CEFET_DARK_BLUE = "#001a33"
CEFET_LIGHT_BLUE = "#4A90E2"
CEFET_GREEN = "#28A745"
CEFET_YELLOW = "#FFC107"
CEFET_ORANGE = "#FD7E14"
CEFET_RED = "#DC3545"
CEFET_PURPLE = "#6B5B95"
CEFET_GRAY = "#6C757D"

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: #F5F7FA;
    }
    
    .header-gradient {
        background: linear-gradient(135deg, """ + CEFET_BLUE + """ 0%, """ + CEFET_DARK_BLUE + """ 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    
    .header-gradient::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }
    
    .header-gradient h1 {
        color: white;
        margin: 0;
        font-size: 42px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-gradient p {
        color: rgba(255,255,255,0.95);
        font-size: 18px;
        margin-top: 10px;
        font-weight: 400;
    }
    
    .kpi-card-modern {
        background: linear-gradient(135deg, """ + CEFET_PURPLE + """ 0%, #8B7AB8 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .kpi-card-modern::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
    }
    
    .kpi-card-modern:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }
    
    .content-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .content-card h3 {
        color: """ + CEFET_DARK_BLUE + """;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, """ + CEFET_BLUE + """ 0%, """ + CEFET_DARK_BLUE + """ 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, """ + CEFET_BLUE + """ 0%, """ + CEFET_DARK_BLUE + """ 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    """Carrega e processa os dados do CEFET-MG"""
    try:
        df = pd.read_excel(file)
        
        # Converter colunas de data
        if 'DATA CRIAÇÃO' in df.columns:
            df['DATA CRIAÇÃO'] = pd.to_datetime(df['DATA CRIAÇÃO'], errors='coerce')
        if 'date_modified' in df.columns:
            df['date_modified'] = pd.to_datetime(df['date_modified'], errors='coerce')
        if 'Quando você ingressou na graduação?' in df.columns:
            df['Quando você ingressou na graduação?'] = pd.to_datetime(df['Quando você ingressou na graduação?'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def extract_likert_value(text):
    """Extrai o valor numérico de uma resposta Likert"""
    if pd.isna(text):
        return None
    text_str = str(text).strip()
    if text_str.startswith('1 -'):
        return 1
    elif text_str.startswith('2 -'):
        return 2
    elif text_str.startswith('3 -'):
        return 3
    elif text_str.startswith('4 -'):
        return 4
    elif text_str.startswith('5 -'):
        return 5
    return None

def get_likert_columns(df):
    """Identifica colunas com escala Likert"""
    likert_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().astype(str).head(100)
            if any('CONCORDO' in str(val).upper() or 'DISCORDO' in str(val).upper() for val in sample):
                likert_cols.append(col)
    return likert_cols

def create_likert_chart(df, column, title):
    """Cria gráfico de barras para questões Likert"""
    df_temp = df.copy()
    df_temp['valor_numerico'] = df_temp[column].apply(extract_likert_value)
    df_temp = df_temp[df_temp['valor_numerico'].notna()]
    
    counts = df_temp['valor_numerico'].value_counts().sort_index()
    
    labels_map = {
        1: '1 - Discordo Totalmente',
        2: '2 - Discordo Parcialmente',
        3: '3 - Neutro',
        4: '4 - Concordo Parcialmente',
        5: '5 - Concordo Totalmente'
    }
    
    colors_map = {
        1: CEFET_RED,
        2: CEFET_ORANGE,
        3: CEFET_YELLOW,
        4: CEFET_LIGHT_BLUE,
        5: CEFET_GREEN
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=[labels_map.get(i, str(i)) for i in counts.index],
            y=counts.values,
            marker_color=[colors_map.get(i, CEFET_GRAY) for i in counts.index],
            text=counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="Avaliação",
        yaxis_title="Quantidade de Respostas",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    return fig

def create_infrastructure_chart(df, infrastructure_cols):
    """Cria gráfico de infraestrutura"""
    infra_data = []
    
    for col in infrastructure_cols:
        values = df[col].value_counts()
        for val, count in values.items():
            if 'EXCELENTE' in str(val).upper():
                infra_data.append({'Item': col.split('?')[-1][:30], 'Avaliação': 'Excelente', 'Quantidade': count})
            elif 'BOA' in str(val).upper():
                infra_data.append({'Item': col.split('?')[-1][:30], 'Avaliação': 'Boa', 'Quantidade': count})
            elif 'RAZOÁVEL' in str(val).upper():
                infra_data.append({'Item': col.split('?')[-1][:30], 'Avaliação': 'Razoável', 'Quantidade': count})
            elif 'RUIM' in str(val).upper():
                infra_data.append({'Item': col.split('?')[-1][:30], 'Avaliação': 'Ruim', 'Quantidade': count})
            elif 'PÉSSIMA' in str(val).upper():
                infra_data.append({'Item': col.split('?')[-1][:30], 'Avaliação': 'Péssima', 'Quantidade': count})
    
    if infra_data:
        df_infra = pd.DataFrame(infra_data)
        fig = px.bar(df_infra, x='Item', y='Quantidade', color='Avaliação',
                     title='Avaliação da Infraestrutura',
                     color_discrete_map={
                         'Excelente': CEFET_GREEN,
                         'Boa': CEFET_LIGHT_BLUE,
                         'Razoável': CEFET_YELLOW,
                         'Ruim': CEFET_ORANGE,
                         'Péssima': CEFET_RED
                     },
                     barmode='stack')
        fig.update_layout(height=500, template="plotly_white")
        return fig
    return None

# Header
st.markdown("""
<div class="header-gradient">
    <h1>🎓 Dashboard CEFET-MG</h1>
    <p>Análise de Dados de Pesquisa Institucional</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📁 Upload de Dados")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel",
        type=['xlsx', 'xls'],
        help="Faça upload do arquivo de dados do CEFET-MG"
    )
    
    if uploaded_file:
        st.success("✅ Arquivo carregado com sucesso!")

# Main content
if uploaded_file is None:
    st.markdown("""
    <div class="content-card">
        <h3>👋 Bem-vindo ao Dashboard CEFET-MG</h3>
        <p>Este dashboard permite visualizar e analisar os dados da pesquisa institucional do CEFET-MG.</p>
        <p><strong>Para começar:</strong></p>
        <ol>
            <li>Faça upload do arquivo Excel na barra lateral</li>
            <li>Explore os gráficos e análises gerados automaticamente</li>
            <li>Use os filtros para segmentar os dados</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
else:
    df = load_data(uploaded_file)
    
    if df is not None:
        # KPIs principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="kpi-card-modern">', unsafe_allow_html=True)
            st.metric("Total de Respostas", f"{len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="kpi-card-modern">', unsafe_allow_html=True)
            if 'IDADE' in df.columns:
                idade_media = df['IDADE'].mean()
                st.metric("Idade Média", f"{idade_media:.1f} anos")
            else:
                st.metric("Idade Média", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="kpi-card-modern">', unsafe_allow_html=True)
            if 'CURSO DE GRADUAÇÃO OF' in df.columns:
                cursos_unicos = df['CURSO DE GRADUAÇÃO OF'].nunique()
                st.metric("Cursos Diferentes", f"{cursos_unicos}")
            else:
                st.metric("Cursos Diferentes", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="kpi-card-modern">', unsafe_allow_html=True)
            if 'DATA CRIAÇÃO' in df.columns:
                periodo = f"{df['DATA CRIAÇÃO'].min().strftime('%m/%Y')} - {df['DATA CRIAÇÃO'].max().strftime('%m/%Y')}"
                st.metric("Período", periodo)
            else:
                st.metric("Período", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabs para diferentes análises
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Visão Geral",
            "🎯 Empreendedorismo",
            "👥 Perfil dos Alunos",
            "🏢 Infraestrutura",
            "📈 Análises Detalhadas"
        ])
        
        with tab1:
            st.markdown('<div class="content-card"><h3>Distribuição por Curso</h3></div>', unsafe_allow_html=True)
            if 'CURSO DE GRADUAÇÃO OF' in df.columns:
                curso_counts = df['CURSO DE GRADUAÇÃO OF'].value_counts().head(15)
                fig = px.bar(
                    x=curso_counts.values,
                    y=curso_counts.index,
                    orientation='h',
                    title='Top 15 Cursos com Mais Respostas',
                    labels={'x': 'Quantidade', 'y': 'Curso'},
                    color=curso_counts.values,
                    color_continuous_scale=['#003366', '#4A90E2']
                )
                fig.update_layout(height=500, template="plotly_white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="content-card"><h3>Distribuição por Idade</h3></div>', unsafe_allow_html=True)
                if 'IDADE' in df.columns:
                    idade_counts = df['IDADE'].value_counts().sort_index()
                    fig = px.bar(
                        x=idade_counts.index,
                        y=idade_counts.values,
                        title='Distribuição de Idade dos Respondentes',
                        labels={'x': 'Idade', 'y': 'Quantidade'},
                        color=idade_counts.values,
                        color_continuous_scale=['#003366', '#4A90E2']
                    )
                    fig.update_layout(height=400, template="plotly_white", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown('<div class="content-card"><h3>Tipo de Ensino Vivenciado</h3></div>', unsafe_allow_html=True)
                if 'Qual(is) o(s) tipos de modelos de ensino você já vivenciou na sua Instituição de Ensino Superior?' in df.columns:
                    ensino_col = 'Qual(is) o(s) tipos de modelos de ensino você já vivenciou na sua Instituição de Ensino Superior?'
                    ensino_counts = df[ensino_col].value_counts()
                    fig = px.pie(
                        values=ensino_counts.values,
                        names=ensino_counts.index,
                        title='Modelos de Ensino',
                        color_discrete_sequence=[CEFET_BLUE, CEFET_LIGHT_BLUE, CEFET_PURPLE, CEFET_GREEN]
                    )
                    fig.update_layout(height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown('<div class="content-card"><h3>Percepções sobre Empreendedorismo</h3></div>', unsafe_allow_html=True)
            
            empreend_cols = [
                '"O modelo/metodologia de ensino da minha Instituição de Ensino Superior contribui para que eu desenvolva postura empreendedora."',
                '"A matriz curricular do curso contribui para o desenvolvimento da minha postura empreendedora."',
                '"A minha Instituição de Ensino Superior oferece uma matriz curricular flexível para que eu possa me engajar em atividades extra-curriculares."'
            ]
            
            for col in empreend_cols:
                if col in df.columns:
                    fig = create_likert_chart(df, col, col.replace('"', ''))
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Entendimento sobre Empreendedorismo</h3></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'O que você entende como empreendedorismo?Empreendedorismo é abrir o próprio negócio (empresa)' in df.columns:
                    col_name = 'O que você entende como empreendedorismo?Empreendedorismo é abrir o próprio negócio (empresa)'
                    counts = df[col_name].value_counts()
                    fig = px.pie(
                        values=counts.values,
                        names=counts.index,
                        title='Empreendedorismo é abrir o próprio negócio?',
                        color_discrete_sequence=[CEFET_GREEN, CEFET_RED]
                    )
                    fig.update_layout(height=350, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Você é sócio(a) ou fundador(a) de alguma empresa?Response' in df.columns:
                    col_name = 'Você é sócio(a) ou fundador(a) de alguma empresa?Response'
                    counts = df[col_name].value_counts()
                    fig = px.pie(
                        values=counts.values,
                        names=counts.index,
                        title='É sócio ou fundador de empresa?',
                        color_discrete_sequence=[CEFET_BLUE, CEFET_LIGHT_BLUE, CEFET_PURPLE, CEFET_ORANGE]
                    )
                    fig.update_layout(height=350, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown('<div class="content-card"><h3>Características dos Alunos</h3></div>', unsafe_allow_html=True)
            
            alunos_cols = [col for col in df.columns if 'O quanto as seguintes características estão presentes nos(as) ALUNOS(AS)' in col]
            
            if alunos_cols:
                selected_aluno_col = st.selectbox(
                    'Selecione a característica para visualizar:',
                    alunos_cols,
                    format_func=lambda x: x.split('?')[-1] if '?' in x else x
                )
                
                fig = create_likert_chart(df, selected_aluno_col, selected_aluno_col.split('?')[-1])
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Participação em Projetos</h3></div>', unsafe_allow_html=True)
            
            if 'Ao longo da sua graduação, quais projetos você já participou ou participa?' in df.columns:
                projetos_col = 'Ao longo da sua graduação, quais projetos você já participou ou participa?'
                projetos_counts = df[projetos_col].value_counts().head(10)
                fig = px.bar(
                    x=projetos_counts.values,
                    y=projetos_counts.index,
                    orientation='h',
                    title='Top 10 Projetos com Maior Participação',
                    labels={'x': 'Quantidade', 'y': 'Projeto'},
                    color=projetos_counts.values,
                    color_continuous_scale=['#003366', '#28A745']
                )
                fig.update_layout(height=400, template="plotly_white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.markdown('<div class="content-card"><h3>Avaliação da Infraestrutura</h3></div>', unsafe_allow_html=True)
            
            infra_cols = [col for col in df.columns if 'Como você avalia a qualidade da infraestrutura oferecida' in col and 'Caso não saiba' in col]
            
            if infra_cols:
                fig = create_infrastructure_chart(df, infra_cols[:8])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Acessibilidade</h3></div>', unsafe_allow_html=True)
            
            acess_cols = [col for col in df.columns if 'destinada à pessoas com deficiência' in col]
            
            if acess_cols:
                fig = create_infrastructure_chart(df, acess_cols[:7])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Qualidade da Internet</h3></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                internet_disp_col = 'Como você avalia a qualidade da internet oferecida pela sua Instituição de Ensino Superior? (no ambiente presencial)Caso não saiba avaliar algum deles (seja por desconhecer ou por não ter experienciado ensino presencial), marcar a opção "Não observado"Disponibilidade de acesso a internet (Wi-Fi e/ou por cabo)'
                if internet_disp_col in df.columns:
                    fig = create_likert_chart(df, internet_disp_col, 'Disponibilidade de Internet')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                internet_vel_col = 'Como você avalia a qualidade da internet oferecida pela sua Instituição de Ensino Superior? (no ambiente presencial)Caso não saiba avaliar algum deles (seja por desconhecer ou por não ter experienciado ensino presencial), marcar a opção "Não observado"Velocidade do acesso sem fio (Wi-Fi)'
                if internet_vel_col in df.columns:
                    fig = create_likert_chart(df, internet_vel_col, 'Velocidade da Internet')
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            st.markdown('<div class="content-card"><h3>Motivos de Permanência e Evasão</h3></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Quais motivos você considera que te fazem permanecer na sua Instituição de Ensino Superior?' in df.columns:
                    perm_col = 'Quais motivos você considera que te fazem permanecer na sua Instituição de Ensino Superior?'
                    perm_counts = df[perm_col].value_counts().head(10)
                    fig = px.bar(
                        x=perm_counts.values,
                        y=perm_counts.index,
                        orientation='h',
                        title='Motivos de Permanência',
                        labels={'x': 'Quantidade', 'y': 'Motivo'},
                        color=perm_counts.values,
                        color_continuous_scale=['#003366', '#28A745']
                    )
                    fig.update_layout(height=500, template="plotly_white", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Quais motivos você considera que te fariam deixar (sair/transferir) a sua Instituição de Ensino Superior?' in df.columns:
                    evasao_col = 'Quais motivos você considera que te fariam deixar (sair/transferir) a sua Instituição de Ensino Superior?'
                    evasao_counts = df[evasao_col].value_counts().head(10)
                    fig = px.bar(
                        x=evasao_counts.values,
                        y=evasao_counts.index,
                        orientation='h',
                        title='Motivos de Evasão',
                        labels={'x': 'Quantidade', 'y': 'Motivo'},
                        color=evasao_counts.values,
                        color_continuous_scale=['#DC3545', '#FD7E14']
                    )
                    fig.update_layout(height=500, template="plotly_white", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Características dos Professores</h3></div>', unsafe_allow_html=True)
            
            prof_cols = [col for col in df.columns if 'O quanto as seguintes características estão presentes nos(as) PROFESSORES(AS)' in col and 'Caso não saiba' in col]
            
            if prof_cols:
                selected_prof_col = st.selectbox(
                    'Selecione a característica dos professores para visualizar:',
                    prof_cols,
                    format_func=lambda x: x.split('"')[-1] if '"' in x else x.split('?')[-1]
                )
                
                fig = create_likert_chart(df, selected_prof_col, selected_prof_col.split('"')[-1] if '"' in selected_prof_col else selected_prof_col.split('?')[-1])
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="content-card"><h3>Dados Brutos</h3></div>', unsafe_allow_html=True)
            
            if st.checkbox('Mostrar dados brutos'):
                st.dataframe(df, use_container_width=True)
                
                # Botão de download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar dados em CSV",
                    data=csv,
                    file_name='dados_cefet_mg.csv',
                    mime='text/csv',
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6C757D; padding: 20px;'>
    <p>Dashboard CEFET-MG | Desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)
