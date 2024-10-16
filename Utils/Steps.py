import time
import json
import yaspin
import shutil


import Utils.Searchxlsx as sxlsx
import Utils.Clearxlsx as cxlsx
from Utils.ProductsFunctions import process_and_save_products_from_folders as psp


DATA_PATH = './data'
CLEANED_PATH = f'{DATA_PATH}/.cleaned'
PRODUCT_DATA_PATH = f'{DATA_PATH}/.products'
EXPORT = './Salida'
BACKUP = './Backup'
LOGS = './Logs'


def Setup():
    saveBackup()

    # Buscar archivos xlsx en la carpeta DATA
    with yaspin.yaspin(text='Buscando archivos xlsx en la carpeta DATA') as sp:
        archivos = sxlsx.search_xlsx(DATA_PATH)
        sp.ok("✅")

    # Limpiar los archivos xlsx y guardarlos en la carpeta CLEANED_PATH
    with yaspin.yaspin(text='Limpiando archivos xlsx') as sp:
        cxlsx.save_cleaned(archivos, CLEANED_PATH)
        sp.ok("✅")

    # Buscar los archivos xlsx limpiados
    with yaspin.yaspin(text='Buscando archivos xlsx limpiados') as sp:
        archivos_cleaned = sxlsx.search_xlsx(CLEANED_PATH)
        sp.ok("✅")

    # Guardar el arbol de dependecia de los archivos limpiados en un archivo json
    with open('DataTree.json', 'w') as file:
        json.dump(archivos_cleaned, file, indent=2)

    # Procesar los productos y guardarlos en la carpeta PRODUCT_DATA_PATH
    with yaspin.yaspin(text='Procesando los productos') as sp:
        time.sleep(0.5)
        psp(archivos_cleaned, PRODUCT_DATA_PATH, sp)
        sp.ok("✅")


def saveBackup():
    try:
        shutil.copytree(PRODUCT_DATA_PATH, f'{BACKUP}/{time.time()}')
    except FileNotFoundError:
        print('No se encontro la carpeta de productos')
