
## GERA EXCEL FISIA
!pip install pandas openpyxl
import zipfile
import json
import pandas as pd
from google.colab import files
import openpyxl

def fazer_upload_zip():
    uploaded = files.upload()
    for filename in uploaded.keys():
        return filename
    return None

def extrair_dados_e_salvar_excel(zip_path):
    dados_extraidos = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            try:
                with zip_ref.open(file_name) as file:
                    data = json.load(file)

                    lista_documentos = data.get("documentos", [])

                    for doc_container in lista_documentos:
                        documentos_internos = doc_container.get("documentos", [])
                        for doc in documentos_internos:
                            chave = doc.get("chave")
                            qvol = doc.get("qVol")
                            pbru = doc.get("pBru")
                            pcub = doc.get("pCub")  # <<< CAMPO ADICIONADO AQUI
                            ndoc = doc.get("nDoc")

                            dados_extraidos.append({
                                "arquivo": file_name,
                                "nDoc": ndoc,
                                "qVol": qvol,
                                "pBru": pbru,
                                "pCub": pcub,  # <<< INCLUÍDO NO DICT
                                "chave": chave
                            })

            except Exception as e:
                print(f"Erro ao processar {file_name}: {e}")
                continue

    if dados_extraidos:
        df = pd.DataFrame(dados_extraidos)

        output_excel = "saida_documentos_internos.xlsx"
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
            worksheet = writer.sheets['Dados']

            # Formatando qVol, pBru e pCub como números com 2 casas decimais
            for col_name in ["qVol", "pBru", "pCub"]:
                if col_name in df.columns:
                    col_idx = df.columns.get_loc(col_name) + 1
                    for row in range(2, len(df) + 2):
                        cell = worksheet.cell(row=row, column=col_idx)
                        cell.number_format = '0.00'

        files.download(output_excel)
    else:
        print("Nenhum dado extraído.")

# Executar no Colab
zip_path = fazer_upload_zip()
if zip_path:
    extrair_dados_e_salvar_excel(zip_path)
