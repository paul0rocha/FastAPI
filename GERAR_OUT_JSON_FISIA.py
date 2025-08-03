## GERA O OUTPUT DE JSON DA API POR CHAVE DE ACESSO

import zipfile
import json
import os
from google.colab import files

uploaded = files.upload()
zip_filename = next(iter(uploaded))

arquivos_gerados = []

with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    # Ignora diretórios, tenta todos os arquivos
    arquivos_texto = [f for f in zip_ref.namelist() if not f.endswith('/')]

    print(f"Arquivos encontrados no ZIP (sem filtro de extensão): {arquivos_texto}")

    for file_name in arquivos_texto:
        try:
            with zip_ref.open(file_name) as file:
                content_bytes = file.read()
                try:
                    content = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    print(f"Não foi possível decodificar {file_name} como UTF-8, pulando.")
                    continue

                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    print(f"Conteúdo de {file_name} não é JSON válido, pulando.")
                    continue

            documentos_root = data.get("documentos")
            if documentos_root is None:
                print(f"A chave 'documentos' não encontrada em {file_name}")
                continue

            print(f"Lendo {file_name}: {len(documentos_root)} documentos encontrados")

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

if arquivos_gerados:
    zip_saida = "jsons_por_chave.zip"
    with zipfile.ZipFile(zip_saida, 'w') as zip_out:
        for arquivo in arquivos_gerados:
            zip_out.write(arquivo)
            os.remove(arquivo)

    print(f"ZIP criado: {zip_saida} com {len(arquivos_gerados)} arquivos")
    files.download(zip_saida)
else:
    print("Nenhum arquivo JSON gerado.")
