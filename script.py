import os
import glob
import argparse
import pickle
import base64
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

def l2_normalize(x: np.ndarray, axis: int = -1, eps: float = 1e-12) -> np.ndarray:
    """L2 normaliza um array numpy ao longo de um eixo específico."""
    norm = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.clip(norm, eps, None)

def encode_image(image_path: str) -> str:
    """Codifica imagem em base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_cache_path(images_dir: str) -> str:
    """Gera caminho para arquivo de cache."""
    return os.path.join(images_dir, ".embeddings_cache_openai.pkl")

def describe_image(client: OpenAI, image_path: str) -> str:
    """Gera descrição detalhada da imagem usando GPT-4 Vision."""
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Descreva esta imagem em detalhes, incluindo objetos, ações, ambiente, cores e atmosfera. Seja específico e descritivo."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def build_image_index(client: OpenAI, image_paths: list[str], cache_path: str) -> tuple[np.ndarray, list[str]]:
    """Gera embeddings das imagens com cache."""
    # Verifica se existe cache válido
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                cached_data = pickle.load(f)
                if cached_data["paths"] == image_paths:
                    print("✓ Cache encontrado - carregando embeddings salvos")
                    return cached_data["embeddings"], cached_data["descriptions"]
        except Exception as e:
            print(f"⚠ Falha ao ler cache: {e}")
    
    # Gera descrições das imagens
    print(f"📸 Analisando {len(image_paths)} imagens com GPT-4 Vision...")
    descriptions = []
    for i, path in enumerate(image_paths, 1):
        print(f"  [{i}/{len(image_paths)}] {os.path.basename(path)}")
        desc = describe_image(client, path)
        descriptions.append(desc)
    
    # Gera embeddings das descrições
    print("\n🔢 Gerando embeddings...")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=descriptions
    )
    
    embeddings = np.array([item.embedding for item in response.data])
    embeddings = l2_normalize(embeddings)
    
    # Salva cache
    try:
        with open(cache_path, "wb") as f:
            pickle.dump({
                "paths": image_paths,
                "embeddings": embeddings,
                "descriptions": descriptions
            }, f)
        print(f"✓ Cache salvo em {cache_path}")
    except Exception as e:
        print(f"⚠ Não foi possível salvar cache: {e}")
    
    return embeddings, descriptions

def search_best(client: OpenAI, img_emb: np.ndarray, image_paths: list[str], descriptions: list[str], query: str):
    """Busca a imagem mais relacionada ao texto."""
    # Gera embedding da query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    
    txt_emb = np.array(response.data[0].embedding)
    txt_emb = l2_normalize(txt_emb.reshape(1, -1))[0]
    
    # Calcula similaridade
    scores = img_emb @ txt_emb
    best_idx = int(np.argmax(scores))
    
    return image_paths[best_idx], float(scores[best_idx]), descriptions[best_idx]

def main():
    """Busca a imagem mais relacionada ao texto em uma pasta usando OpenAI."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", required=True, help="Pasta com imagens")
    parser.add_argument("--query", required=True, help="Texto digitado")
    parser.add_argument("--rebuild-cache", action="store_true", help="Força reconstrução do cache")
    parser.add_argument("--show-description", action="store_true", help="Mostra descrição da imagem")
    args = parser.parse_args()

    # Verifica API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("❌ OPENAI_API_KEY não configurada. Use: export OPENAI_API_KEY=sua_key")
    
    client = OpenAI(api_key=api_key)

    # Coleta imagens
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp")
    image_paths = []
    for e in exts:
        image_paths.extend(glob.glob(os.path.join(args.images_dir, e)))
    image_paths = sorted(image_paths)

    if not image_paths:
        raise SystemExit("Nenhuma imagem encontrada na pasta.")

    print(f"🔍 Encontradas {len(image_paths)} imagens")

    # Indexa imagens (com cache!)
    cache_path = get_cache_path(args.images_dir)
    if args.rebuild_cache and os.path.exists(cache_path):
        os.remove(cache_path)
        print("Cache removido - será reconstruído")
    
    img_emb, descriptions = build_image_index(client, image_paths, cache_path)

    # Busca
    print(f"\n🔎 Buscando: '{args.query}'")
    best_path, best_score, best_desc = search_best(client, img_emb, image_paths, descriptions, args.query)

    print("\n" + "="*60)
    print("✅ Imagem mais relacionada:", best_path)
    print("📊 Score (cosine similarity):", round(best_score, 4))
    if args.show_description:
        print("\n📝 Descrição da imagem:")
        print(best_desc)
    print("="*60)

if __name__ == "__main__":
    main()
