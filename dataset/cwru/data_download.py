import pandas as pd
import requests
import os
from pathlib import Path
from tqdm import tqdm

def download_dataset(config_filename='config.csv', 
                     output_dir_relative='../../raw_data/',
                     target_filenames=None):
    """
    Baixa arquivos do dataset. Se 'target_filenames' for fornecido, baixa apenas ele.
    Senão, baixa todo o csv.

    Args:
        config_filename (str): Nome do arquivo de configuração CSV.
        output_dir_relative (str): Caminho relativo para o diretório de saída.
        target_filenames (list, optional): Lista de nomes de arquivos específicos 
                                          (ex: ['97.mat', '100.mat']) para baixar.
    """
    
    BASE_URL = "https://engineering.case.edu/sites/default/files/"

    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / config_filename
    output_path = (script_dir / output_dir_relative).resolve()
    
    os.makedirs(output_path, exist_ok=True)
    
    if target_filenames:

        filenames_to_download = [name.strip() for name in target_filenames]
        print(f"Modo Seletivo Ativado: Tentando baixar {len(filenames_to_download)} arquivo(s).")
    else:
        try:
            df = pd.read_csv(config_path, sep=',')
            df.columns = df.columns.str.strip()
            
            filenames_to_download = df['filename'].str.strip().unique()
            print(f"Modo Completo Ativado: Encontrados {len(filenames_to_download)} arquivos únicos para baixar.")

        except FileNotFoundError:
            print(f"ERRO: Arquivo de configuração não encontrado em: {config_path}")
            return
        except KeyError:
            print("ERRO: A coluna 'filename' não foi encontrada no config.csv.")
            return

    for filename in tqdm(filenames_to_download, desc="Baixando Arquivos"):
        file_url = f"{BASE_URL}{filename}"
        output_file_path = output_path / filename

        if output_file_path.exists():
            continue
        
        try:
            response = requests.get(file_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(output_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)
            else:
                print(f"\nERRO: Falha ao baixar {filename}. Status Code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"\nERRO de Conexão ao baixar {filename}: {e}")
            
    print("\nDownload do dataset concluído!")

if __name__ == "__main__":
    
    #print("--- INICIANDO DOWNLOAD SELETIVO DE TESTE ---")
    download_dataset(target_filenames=['118.mat'])
    
    #print("\n--- INICIANDO DOWNLOAD DE MÚLTIPLOS ARQUIVOS SELECIONADOS ---")
    #download_dataset(target_filenames=['104.mat', '172.mat'])
    
    #print("\n--- INICIANDO DOWNLOAD DE TODOS OS ARQUIVOS ---")
    #download_dataset()