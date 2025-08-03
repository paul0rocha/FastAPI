import zipfile
import json
import os
from google.colab import files
import requests

# --- Token fixo da API DHL ---
ACCESS_TOKEN = "8Gwx7R7ArpUqxKRaA5OG60K7AVPn"
ENVIO_URL = "https://dsc.api.dhl.com/dhllink/emissao"

# --- Envio de JSON para API DHL ---
def enviar_json_api(json_data, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(ENVIO_URL, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()

# --- Upload e extração do ZIP ---
uploaded = files.upload()
zip_filename = next(iter(uploaded))

arquivos_gerados = []

with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    arquivos_texto = [f for f in zip_ref.namelist() if not f.endswith('/')]

    print(f"Arquivos encontrados no ZIP: {arquivos_texto}")

    for file_name in arquivos_texto:
        try:
            with zip_ref.open(file_name) as file:
                content_bytes = file.read()
                try:
                    content = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    print(f"Não foi possível decodificar {file_name} como UTF-8. Pulando.")
                    continue

                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    print(f"{file_name} não contém JSON válido. Pulando.")
                    continue

            documentos_root = data.get("documentos")
            if documentos_root is None:
                print(f"A chave 'documentos' não encontrada em {file_name}")
                continue

            print(f"{file_name}: {len(documentos_root)} documentos encontrados")

            for doc_container in documentos_root:
                documentos_internos = doc_container.get("documentos", [])
                if not documentos_internos:
                    print(f"  Nenhum documento interno em {file_name}")
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
                    print(f"  Arquivo gerado: {nome_arquivo}")

        except Exception as e:
            print(f"Erro ao processar {file_name}: {e}")

# --- Envio dos arquivos JSON gerados ---
if arquivos_gerados:
    print("Enviando arquivos para a API DHL...")
    for arquivo in arquivos_gerados:
        with open(arquivo, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        try:
            resposta = enviar_json_api(json_data, ACCESS_TOKEN)
            print(f"Envio do arquivo {arquivo} bem-sucedido. Resposta: {resposta}")
        except Exception as e:
            print(f"Erro ao enviar {arquivo}: {e}")

        os.remove(arquivo)
else:
    print("Nenhum arquivo JSON gerado.")
