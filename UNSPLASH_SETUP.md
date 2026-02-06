# 🔑 Como obter sua UNSPLASH_ACCESS_KEY

## Passo a passo (5 minutos)

### 1. Criar conta no Unsplash
- Acesse: https://unsplash.com
- Clique em "Join free" no canto superior direito
- Complete o cadastro (pode usar conta Google)

### 2. Registrar-se como desenvolvedor
- Acesse: https://unsplash.com/developers
- Clique em "Register as a developer"
- Preencha o formulário:
  - **First name**: Seu nome
  - **Last name**: Seu sobrenome
  - **Email**: Seu email
  - **Username**: Escolha um username
  - Aceite os termos de uso

### 3. Criar uma aplicação
- Após registrar, acesse: https://unsplash.com/oauth/applications
- Clique em "New Application"
- Preencha os dados:
  - **Application name**: "Semantic Image Search" (ou outro nome)
  - **Description**: "Sistema de busca semântica de imagens"
  - Marque **TODAS** as checkboxes dos termos
- Clique em "Create application"

### 4. Copiar a Access Key
- Na página da sua aplicação, você verá:
  - **Access Key**: Comece com algo como `abc123...`
  - **Secret Key**: Não precisa (só para OAuth)
  
- Copie apenas a **Access Key**

### 5. Configurar no sistema

**No terminal (macOS/Linux):**
```bash
export UNSPLASH_ACCESS_KEY=sua_access_key_aqui
```

**No terminal (Windows PowerShell):**
```powershell
$env:UNSPLASH_ACCESS_KEY="sua_access_key_aqui"
```

**Permanente (macOS/Linux) - adicione ao `~/.zshrc` ou `~/.bashrc`:**
```bash
echo 'export UNSPLASH_ACCESS_KEY=sua_access_key_aqui' >> ~/.zshrc
source ~/.zshrc
```

### 6. Testar
```bash
python test_unsplash.py
```

## ⚠️ Limites da API gratuita

- **50 requisições por hora**
- **Demonstração/desenvolvimento**: OK
- **Produção**: Precisa de plano pago

## 🔒 Segurança

- **NUNCA** commite a chave no Git
- **NUNCA** compartilhe publicamente
- Use variáveis de ambiente
- Arquivo `.env` está no `.gitignore`

## 🆘 Problemas comuns

### Erro 401 (Unauthorized)
- ✅ Verifique se copiou a chave completa
- ✅ Sem espaços extras antes/depois
- ✅ Use aspas ao exportar: `export UNSPLASH_ACCESS_KEY="sua_key"`
- ✅ Reabra o terminal após configurar

### Erro 403 (Forbidden)
- ✅ Limite de 50 req/hora atingido
- ✅ Aguarde 1 hora
- ✅ Ou crie nova aplicação (temporário)

### "UNSPLASH_ACCESS_KEY não configurada"
- ✅ Execute o `export` no mesmo terminal que roda a app
- ✅ Ou adicione ao arquivo de perfil do shell

## 📧 Suporte

Problemas com a API do Unsplash:
- Documentação: https://unsplash.com/documentation
- Suporte: help@unsplash.com
