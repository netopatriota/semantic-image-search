import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

class UnsplashAPI:
    """Cliente para API do Unsplash."""
    
    def __init__(self, access_key: str = None):
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("UNSPLASH_ACCESS_KEY não configurada")
        
        self.base_url = "https://api.unsplash.com"
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }
    
    def search_photos(self, query: str, per_page: int = 10, page: int = 1):
        """
        Busca fotos no Unsplash.
        
        Args:
            query: Termo de busca
            per_page: Número de resultados (max 30)
            page: Página de resultados
            
        Returns:
            Lista de dicionários com informações das fotos
        """
        endpoint = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "per_page": min(per_page, 30),  # Max 30 por página
            "page": page,
            "orientation": "landscape"  # Opcional: fotos horizontais
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            
            # Tratamento específico de erros
            if response.status_code == 401:
                raise ValueError(
                    "❌ API Key do Unsplash inválida ou expirada!\n"
                    "Verifique se UNSPLASH_ACCESS_KEY está correta.\n"
                    "Obtenha uma nova em: https://unsplash.com/developers"
                )
            elif response.status_code == 403:
                raise ValueError(
                    "❌ Limite de requisições do Unsplash atingido!\n"
                    "Aguarde 1 hora ou faça upgrade do plano."
                )
            
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            raise ValueError("⏱️ Timeout na conexão com Unsplash. Tente novamente.")
        except requests.exceptions.ConnectionError:
            raise ValueError("🌐 Erro de conexão. Verifique sua internet.")
        
        data = response.json()
        
        photos = []
        for result in data.get("results", []):
            photos.append({
                "id": result["id"],
                "description": result.get("description") or result.get("alt_description") or "Sem descrição",
                "url_regular": result["urls"]["regular"],  # 1080px
                "url_small": result["urls"]["small"],      # 400px
                "url_thumb": result["urls"]["thumb"],      # 200px
                "photographer": result["user"]["name"],
                "photographer_url": result["user"]["links"]["html"],
                "download_location": result["links"]["download_location"]
            })
        
        return photos
    
    def download_image(self, url: str, save_path: str) -> str:
        """
        Baixa uma imagem do Unsplash.
        
        Args:
            url: URL da imagem
            save_path: Caminho para salvar
            
        Returns:
            Caminho do arquivo salvo
        """
        # Cria diretório se não existir
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return save_path
    
    def trigger_download(self, download_location: str):
        """
        Registra download no Unsplash (obrigatório pela API).
        
        Args:
            download_location: URL do endpoint de download
        """
        try:
            requests.get(download_location, headers=self.headers)
        except:
            pass  # Não crítico se falhar


def search_and_download(query: str, num_images: int = 10, cache_dir: str = "./unsplash_cache"):
    """
    Busca e baixa imagens do Unsplash.
    
    Args:
        query: Termo de busca
        num_images: Número de imagens para baixar
        cache_dir: Diretório para cache
        
    Returns:
        Lista de caminhos das imagens baixadas e metadados
    """
    api = UnsplashAPI()
    
    # Busca fotos
    photos = api.search_photos(query, per_page=num_images)
    
    if not photos:
        return []
    
    # Cria diretório de cache
    cache_path = Path(cache_dir) / query.replace(" ", "_").lower()
    cache_path.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    for i, photo in enumerate(photos):
        # Define nome do arquivo
        filename = f"{photo['id']}.jpg"
        filepath = cache_path / filename
        
        # Baixa se não existir
        if not filepath.exists():
            api.download_image(photo['url_regular'], str(filepath))
            api.trigger_download(photo['download_location'])
        
        downloaded.append({
            'path': str(filepath),
            'id': photo['id'],
            'description': photo['description'],
            'photographer': photo['photographer'],
            'photographer_url': photo['photographer_url']
        })
    
    return downloaded
