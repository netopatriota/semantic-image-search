# 🔍 Busca Semântica de Imagens - Multimodal

Sistema inteligente de busca semântica em imagens usando GPT-4 Vision e OpenAI Embeddings.

## ✨ Recursos

- 📂 **Modo Local**: Busca em imagens da sua pasta
- 🌐 **Modo Unsplash**: Busca em milhões de fotos profissionais
- 🧠 **GPT-4 Vision**: Análise inteligente de imagens
- ⚡ **Cache**: Embeddings salvos para busca instantânea
- 📊 **Scores de similaridade**: Métrica precisa (cosine similarity)
- 🎨 **Interface Streamlit**: Visual e interativa

## 🚀 Setup

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar API Keys

#### OpenAI (obrigatória)

```bash
export OPENAI_API_KEY=sua_key_aqui
```

Obtenha em: https://platform.openai.com/api-keys

#### Unsplash (opcional - só para modo online)

```bash
export UNSPLASH_ACCESS_KEY=sua_key_aqui
```

**📖 [Guia completo: Como obter chave do Unsplash](UNSPLASH_SETUP.md)**

**Resumo rápido:**
1. Acesse: https://unsplash.com/developers
2. Clique em "Register as a developer"
3. Crie um "New Application"
4. Aceite os termos
5. Copie o "Access Key"
6. Limite gratuito: **50 requisições/hora**

### 3. Executar

#### Interface Streamlit (recomendado)

```bash
streamlit run app.py
```

#### Linha de comando

```bash
python script.py --images_dir ./imagens --query "cachorro na praia" --show-description
```

## 📖 Como usar

### Modo Local

1. Coloque suas imagens na pasta `./imagens`
2. Execute `streamlit run app.py`
3. Selecione "📂 Local (pasta)"
4. Digite sua busca e clique em "🚀 Buscar"

### Modo Unsplash

1. Configure `UNSPLASH_ACCESS_KEY`
2. Execute `streamlit run app.py`
3. Selecione "🌐 Unsplash Online"
4. Digite o termo de busca (em inglês funciona melhor)
5. Clique em "🌐 Buscar imagens no Unsplash"
6. Digite sua query semântica para filtrar

## 🛠 Tecnologias

- **OpenAI GPT-4o-mini**: Análise de imagens
- **OpenAI text-embedding-3-small**: Embeddings semânticos
- **Unsplash API**: Banco de imagens profissionais
- **Streamlit**: Interface web
- **NumPy**: Cálculos de similaridade

## 📊 Como funciona

```
Imagem → GPT-4 Vision → Descrição textual → Embedding (vetor)
                                               ↓
Query de texto → Embedding (vetor) → Similaridade coseno
                                               ↓
                                    Ranking de resultados
```

## 💡 Exemplos de queries

- "cachorro correndo na praia ao entardecer"
- "paisagem urbana noturna com luzes"
- "pessoa sorrindo em ambiente profissional"
- "montanhas cobertas de neve"
- "comida colorida em close-up"

## ⚙️ Configurações

- **Número de resultados**: 1-10 imagens mais similares
- **Mostrar descrições**: Análise do GPT-4 Vision
- **Mostrar scores**: Percentual de similaridade
- **Cache**: Automático para performance

## 📝 Notas

- Primeira execução é lenta (processa com GPT-4 Vision)
- Execuções seguintes são instantâneas (usa cache)
- Modo Unsplash consome API calls da OpenAI e Unsplash
- Imagens do Unsplash ficam em `./unsplash_cache/`

## 🎯 Entregável do Desafio

✅ Gerar embeddings das imagens  
✅ Gerar embedding de uma frase digitada  
✅ Calcular similaridade semântica  
✅ Retornar a imagem mais próxima semanticamente  
✅ Score de similaridade  
✅ **PLUS**: Interface Streamlit  
✅ **PLUS**: Integração com Unsplash API  

---

🚀 Desenvolvido para o Curso de Extensão IA Generativa - Busca Semântica Multimodal
