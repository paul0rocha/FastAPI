import zipfile
import json
import os
import requests
from google.colab import files
from time import sleep
from IPython.display import display, HTML

# ==== CONFIGURAÇÕES DE CREDENCIAL ====
CLIENT_ID = "3bjSWcQhUHZ80fTzEaZ2KPM55OiHUoIh"
CLIENT_SECRET = "UKKCLqxSvYEegDgC"
TOKEN_URL = "https://dsc.api.dhl.com/dhllink/auth/token"
API_ENDPOINT = "https://dsc.api.dhl.com/dhllink/emissao"  # Ajuste se necessário

# ==== PRINT BONITO PARA CONSOLE ESCURO ====
def print_highlight(text, color="#2E7D32"):
    display(HTML(f"""
    <pre style='
        background:{color};
        padding:12px;
        border-radius:6px;
        font-family:Consolas,monospace;
        color:#F1F1F1;
        white-space:pre-wrap;
    '>{text}</pre>
    """))

# ==== FUNÇÃO COM CORES CATEGORIZADAS ====
def print_msg(text, tipo="info"):
    cores = {
        "sucesso": "#2E7D32",  # verde escuro
        "erro": "#C62828",     # vermelho escuro
        "aviso": "#6A1B9A",    # roxo escuro
        "info": "#1565C0",     # azul escuro
        "neutro": "#455A64"    # azul acinzentado
    }
    cor = cores.get(tipo, "#455A64")
    print_highlight(text, cor)

# ==== FUNÇÃO PARA OBTER TOKEN ====
def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print_msg("✅ Access Token obtido com sucesso!", "sucesso")
        return token
    else:
        raise Exception(f"Erro ao obter token: {response.status_code} - {response.text}")

# ==== UPLOAD DO ZIP ====
uploaded = files.upload()
zip_filename = next(iter(uploaded))
arquivos_gerados = []

# ==== GERAÇÃO DO TOKEN ====
access_token = get_access_token()
headers_api = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

# ==== PROCESSAMENTO DO ZIP ====
with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    arquivos_texto = [f for f in zip_ref.namelist() if not f.endswith('/')]
    print_msg(f"📦 Arquivos no ZIP: {arquivos_texto}", "neutro")

    for file_name in arquivos_texto:
        try:
            with zip_ref.open(file_name) as file:
                content_bytes = file.read()
                try:
                    content = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    print_msg(f"❌ Erro UTF-8 em {file_name}, ignorado.", "erro")
                    continue

                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    print_msg(f"❌ JSON inválido em {file_name}, ignorado.", "erro")
                    continue

            documentos_root = data.get("documentos")
            if documentos_root is None:
                print_msg(f"⚠️ 'documentos' não encontrado em {file_name}", "aviso")
                continue

            print_msg(f"📄 {file_name}: {len(documentos_root)} documentos encontrados", "info")

            for doc_container in documentos_root:
                documentos_internos = doc_container.get("documentos", [])
                if not documentos_internos:
                    print_msg(f"⚠️ Documento vazio em {file_name}", "aviso")
                    continue

                for doc in documentos_internos:
                    chave = doc.get("chave", "sem_chave").replace('/', '_').replace('\\', '_')
                    nova_estrutura = {
                        "documentos": [
                            {
                                **{k: v for k, v in doc_container.items() if k != "documentos"},
                                "documentos": [doc]
                            }
                        ]
                    }

                    nome_arquivo = f"json_chave_{chave}.json"
                    with open(nome_arquivo, "w", encoding="utf-8") as f_out:
                        json.dump(nova_estrutura, f_out, ensure_ascii=False, indent=2)
                    arquivos_gerados.append(nome_arquivo)

                    # === CHAMADA DE API POR CHAVE ===
                    print_msg(f"🚀 Realizando chamada de API para chave: {chave}", "info")
                    try:
                        response = requests.post(API_ENDPOINT, headers=headers_api, json=nova_estrutura)
                        if response.status_code == 200:
                            resposta_formatada = json.dumps(response.json(), indent=2, ensure_ascii=False)
                            print_msg(f"✅ Sucesso na API para chave {chave}:\n{resposta_formatada}", "sucesso")
                        else:
                            print_msg(f"❌ Falha na API para chave {chave}: {response.status_code}\n{response.text}", "erro")
                    except Exception as e:
                        print_msg(f"🔥 Erro de conexão com API para chave {chave}: {str(e)}", "erro")
                    sleep(1)  # Evita sobrecarregar a API

        except Exception as e:
            print_msg(f"⚠️ Erro ao processar {file_name}: {str(e)}", "aviso")

# ==== CRIAÇÃO DO ZIP FINAL ====
if arquivos_gerados:
    zip_saida = "jsons_por_chave.zip"
    with zipfile.ZipFile(zip_saida, 'w') as zip_out:
        for arquivo in arquivos_gerados:
            zip_out.write(arquivo)
            os.remove(arquivo)

    print_msg(f"📦 ZIP final criado com {len(arquivos_gerados)} arquivos: {zip_saida}", "info")
    files.download(zip_saida)
else:
    print_msg("⚠️ Nenhum arquivo JSON foi gerado.", "aviso")
