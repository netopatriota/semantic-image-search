import os
import glob
import streamlit as st
import numpy as np
from PIL import Image
from script import (
    OpenAI,
    l2_normalize,
    get_cache_path,
    build_image_index,
    describe_image
)
from unsplash_search import search_and_download

st.set_page_config(
    page_title="🔍 Busca Semântica de Imagens",
    page_icon="🖼️",
    layout="wide"
)

def search_images(client: OpenAI, img_emb: np.ndarray, image_paths: list[str], 
                  descriptions: list[str], query: str, top_k: int = 3):
    """Busca as top K imagens mais relacionadas ao texto."""
    # Gera embedding da query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    
    txt_emb = np.array(response.data[0].embedding)
    txt_emb = l2_normalize(txt_emb.reshape(1, -1))[0]
    
    # Calcula similaridade
    scores = img_emb @ txt_emb
    
    # Top K resultados
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            'path': image_paths[idx],
            'score': float(scores[idx]),
            'description': descriptions[idx]
        })
    
    return results

@st.cache_resource
def load_client():
    """Carrega cliente OpenAI (cached)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY não configurada!")
        st.stop()
    return OpenAI(api_key=api_key)

@st.cache_data
def load_image_data(_client, images_dir: str):
    """Carrega embeddings das imagens (cached)."""
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp")
    image_paths = []
    for e in exts:
        image_paths.extend(glob.glob(os.path.join(images_dir, e)))
    image_paths = sorted(image_paths)
    
    if not image_paths:
        st.error("❌ Nenhuma imagem encontrada na pasta!")
        st.stop()
    
    cache_path = get_cache_path(images_dir)
    
    # Verifica se tem cache
    import pickle
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                cached_data = pickle.load(f)
                if cached_data["paths"] == image_paths:
                    st.success(f"⚡ Cache carregado! {len(image_paths)} imagens prontas.")
                    return cached_data["embeddings"], image_paths, cached_data["descriptions"]
        except:
            pass
    
    # Processa do zero com feedback visual
    st.warning(f"🔄 Processando {len(image_paths)} imagens pela primeira vez...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Gera descrições
    descriptions = []
    for i, path in enumerate(image_paths):
        status_text.text(f"📸 Analisando imagem {i+1}/{len(image_paths)}: {os.path.basename(path)}")
        progress_bar.progress((i) / (len(image_paths) * 2))  # Metade do progresso
        
        from script import describe_image
        desc = describe_image(_client, path)
        descriptions.append(desc)
    
    # Gera embeddings
    status_text.text("🔢 Gerando embeddings...")
    progress_bar.progress(0.5)
    
    response = _client.embeddings.create(
        model="text-embedding-3-small",
        input=descriptions
    )
    
    embeddings = np.array([item.embedding for item in response.data])
    embeddings = l2_normalize(embeddings)
    
    # Salva cache
    status_text.text("💾 Salvando cache...")
    progress_bar.progress(0.9)
    
    with open(cache_path, "wb") as f:
        import pickle
        pickle.dump({
            "paths": image_paths,
            "embeddings": embeddings,
            "descriptions": descriptions
        }, f)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Processamento concluído!")
    
    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    return embeddings, image_paths, descriptions

def load_unsplash_images(client: OpenAI, search_query: str, num_images: int = 15):
    """Busca e processa imagens do Unsplash."""
    try:
        # Busca e baixa imagens
        with st.spinner(f"🌐 Buscando {num_images} imagens no Unsplash..."):
            photos = search_and_download(search_query, num_images=num_images)
        
        if not photos:
            st.warning("Nenhuma imagem encontrada no Unsplash para este termo.")
            return None, None, None
        
        st.info(f"📥 {len(photos)} imagens baixadas do Unsplash")
        
        # Processa com GPT-4 Vision
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        descriptions = []
        image_paths = [p['path'] for p in photos]
        
        for i, photo in enumerate(photos):
            status_text.text(f"📸 Analisando {i+1}/{len(photos)}: {os.path.basename(photo['path'])}")
            progress_bar.progress((i) / (len(photos) * 2))
            
            desc = describe_image(client, photo['path'])
            descriptions.append(desc)
        
        # Gera embeddings
        status_text.text("🔢 Gerando embeddings...")
        progress_bar.progress(0.5)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=descriptions
        )
        
        embeddings = np.array([item.embedding for item in response.data])
        embeddings = l2_normalize(embeddings)
        
        progress_bar.progress(1.0)
        status_text.text("✅ Imagens do Unsplash prontas!")
        
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return embeddings, image_paths, descriptions
        
    except ValueError as e:
        # Erros da API do Unsplash (tratados em unsplash_search.py)
        st.error(str(e))
        
        # Dicas adicionais
        if "401" in str(e) or "inválida" in str(e):
            st.warning("🔧 Passos para corrigir:")
            st.code("1. Acesse: https://unsplash.com/developers\n2. Faça login\n3. Vá em 'Your apps'\n4. Copie o 'Access Key'\n5. Execute: export UNSPLASH_ACCESS_KEY=<sua_key>", language="bash")
        
        return None, None, None
        
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        st.exception(e)
        return None, None, None

def main():
    # Header
    st.title("🔍 Busca Semântica de Imagens")
    st.markdown("### Encontre imagens usando linguagem natural com **GPT-4 Vision** e **OpenAI Embeddings**")
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Modo de busca
        search_mode = st.radio(
            "🎯 Modo de busca",
            ["📂 Local (pasta)", "🌐 Unsplash Online"],
            help="Local: busca em imagens da pasta | Unsplash: busca em milhões de fotos profissionais"
        )
        
        st.divider()
        
        # Configurações específicas por modo
        if search_mode == "📂 Local (pasta)":
            images_dir = st.text_input(
                "📁 Pasta de imagens",
                value="./imagens",
                help="Caminho relativo ou absoluto"
            )
            
            st.caption("⚠️ Use apenas se adicionar novas imagens")
            if st.button("🔄 Reconstruir índice", help="Reprocessar todas as imagens com GPT-4 Vision"):
                cache_path = get_cache_path(images_dir)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    st.cache_data.clear()
                    st.success("✅ Cache removido! Recarregando...")
                    st.rerun()
                else:
                    st.info("Nenhum cache para limpar")
        
        else:  # Modo Unsplash
            unsplash_query = st.text_input(
                "🔎 Termo de busca no Unsplash",
                value="nature landscape",
                help="Ex: mountains, beach, cityscape, wildlife"
            )
            
            num_unsplash_images = st.slider(
                "📸 Imagens do Unsplash",
                min_value=5,
                max_value=30,
                value=15,
                help="Quantas imagens buscar (máx 30)"
            )
        
        st.divider()
        
        top_k = st.slider(
            "🎯 Número de resultados",
            min_value=1,
            max_value=10,
            value=3,
            help="Quantas imagens similares mostrar"
        )
        
        show_descriptions = st.checkbox(
            "📝 Mostrar descrições",
            value=True,
            help="Exibir análise GPT-4 das imagens"
        )
        
        show_scores = st.checkbox(
            "📊 Mostrar scores",
            value=True,
            help="Exibir similaridade coseno"
        )
    
    # Carrega cliente OpenAI
    client = load_client()
    
    # Carrega imagens baseado no modo
    img_emb = None
    image_paths = None
    descriptions = None
    
    if search_mode == "📂 Local (pasta)":
        if not os.path.exists(images_dir):
            st.error(f"❌ Pasta '{images_dir}' não encontrada!")
            st.stop()
        
        img_emb, image_paths, descriptions = load_image_data(client, images_dir)
        st.success(f"✅ {len(image_paths)} imagens locais indexadas!")
    
    else:  # Modo Unsplash
        # Verifica se tem API key do Unsplash
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not unsplash_key:
            st.error("❌ UNSPLASH_ACCESS_KEY não configurada!")
            st.info("👉 Configure com: `export UNSPLASH_ACCESS_KEY=sua_key`")
            st.info("🔗 Obtenha uma chave gratuita em: https://unsplash.com/developers")
            st.code("export UNSPLASH_ACCESS_KEY=sua_access_key_aqui", language="bash")
            st.stop()
        
        # Mostra informações da chave (primeiros/últimos caracteres)
        key_preview = f"{unsplash_key[:8]}...{unsplash_key[-4:]}" if len(unsplash_key) > 12 else "***"
        st.sidebar.caption(f"🔑 Unsplash: {key_preview}")
        
        if st.button("🌐 Buscar imagens no Unsplash", type="primary"):
            result = load_unsplash_images(client, unsplash_query, num_unsplash_images)
            if result[0] is not None:
                img_emb, image_paths, descriptions = result
                st.session_state['unsplash_data'] = (img_emb, image_paths, descriptions)
                st.success(f"✅ {len(image_paths)} imagens do Unsplash prontas!")
        
        # Carrega dados da sessão se existir
        if 'unsplash_data' in st.session_state:
            img_emb, image_paths, descriptions = st.session_state['unsplash_data']
            st.info(f"📸 {len(image_paths)} imagens do Unsplash em memória")
    
    # Interface de busca (só se tiver imagens carregadas)
    if img_emb is not None:
        st.divider()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "🔎 Digite sua busca:",
                placeholder="Ex: cachorro correndo na praia, paisagem urbana noturna, pessoa sorrindo...",
                help="Descreva o que você procura em linguagem natural"
            )
        
        with col2:
            search_button = st.button("🚀 Buscar", type="primary", use_container_width=True)
        
        # Busca
        if query and (search_button or query):
            with st.spinner("🔍 Buscando imagens similares..."):
                results = search_images(client, img_emb, image_paths, descriptions, query, top_k)
            
            st.divider()
            st.subheader(f"📸 Top {len(results)} Resultados")
            
            # Exibe resultados
            for i, result in enumerate(results, 1):
                with st.container():
                    col_img, col_info = st.columns([1, 2])
                    
                    with col_img:
                        img = Image.open(result['path'])
                        st.image(img, use_container_width=True)
                    
                    with col_info:
                        st.markdown(f"### {i}º - {os.path.basename(result['path'])}")
                        
                        if show_scores:
                            score_pct = result['score'] * 100
                            st.metric(
                                "Similaridade",
                                f"{score_pct:.1f}%",
                                help="Similaridade coseno entre query e imagem"
                            )
                        
                        if show_descriptions:
                            with st.expander("📝 Descrição da imagem (GPT-4 Vision)", expanded=(i==1)):
                                st.write(result['description'])
                        
                        st.markdown(f"**Caminho:** `{result['path']}`")
                    
                    if i < len(results):
                        st.divider()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🚀 Powered by <b>OpenAI GPT-4o-mini</b> + <b>text-embedding-3-small</b> + <b>Unsplash API</b></p>
            <p style='font-size: 0.9em;'>Embeddings em cache para busca instantânea ⚡</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
