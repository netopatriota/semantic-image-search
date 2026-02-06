#!/usr/bin/env python3
"""
Script de teste para validar integração com Unsplash.
"""

import os
from unsplash_search import UnsplashAPI, search_and_download

def test_unsplash_connection():
    """Testa conexão com Unsplash API."""
    print("🧪 Testando conexão com Unsplash API...\n")
    
    # Verifica API key
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        print("❌ UNSPLASH_ACCESS_KEY não configurada!")
        print("💡 Configure com: export UNSPLASH_ACCESS_KEY=sua_key")
        print("🔗 Obtenha em: https://unsplash.com/developers\n")
        print("📋 Passos:")
        print("   1. Faça login no Unsplash")
        print("   2. Acesse https://unsplash.com/oauth/applications")
        print("   3. Clique em 'New Application'")
        print("   4. Aceite os termos e crie o app")
        print("   5. Copie o 'Access Key'")
        print("   6. Execute: export UNSPLASH_ACCESS_KEY=<access_key>")
        return False
    
    # Mostra preview da chave
    key_preview = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    print(f"🔑 Chave detectada: {key_preview}")
    print(f"📏 Tamanho da chave: {len(api_key)} caracteres\n")
    
    try:
        # Cria cliente
        client = UnsplashAPI(api_key)
        print("✅ Cliente Unsplash criado\n")
        
        # Busca fotos de teste
        print("🔍 Buscando fotos de 'mountain'...")
        photos = client.search_photos("mountain", per_page=3)
        
        print(f"✅ Encontradas {len(photos)} fotos!\n")
        
        # Mostra resultados
        for i, photo in enumerate(photos, 1):
            print(f"📸 Foto {i}:")
            print(f"   ID: {photo['id']}")
            print(f"   Descrição: {photo['description'][:60]}...")
            print(f"   Fotógrafo: {photo['photographer']}")
            print(f"   URL: {photo['url_small'][:50]}...")
            print()
        
        print("✅ Teste de conexão bem-sucedido!")
        return True
        
    except ValueError as e:
        print(f"❌ Erro de validação: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        return False

def test_download():
    """Testa download de imagens."""
    print("\n" + "="*60)
    print("🧪 Testando download de imagens...\n")
    
    try:
        results = search_and_download("nature", num_images=2, cache_dir="./test_cache")
        
        print(f"✅ Download concluído! {len(results)} imagens baixadas")
        
        for result in results:
            print(f"   📁 {result['path']}")
        
        print("\n✅ Teste de download bem-sucedido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no download: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🚀 TESTE DE INTEGRAÇÃO UNSPLASH")
    print("="*60 + "\n")
    
    success = True
    
    # Teste 1: Conexão
    if not test_unsplash_connection():
        success = False
    
    # Teste 2: Download
    if success and input("\n📥 Testar download de imagens? (s/n): ").lower() == 's':
        test_download()
    
    print("\n" + "="*60)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
    print("="*60)
