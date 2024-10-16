from openpyxl import load_workbook
from Utils.Searchxlsx import search_xlsx
from Utils.AestheticsExcel.AlphaWidthColums import AlphaWidthColums
from Utils.Steps import EXPORT


# Buscar archivos xlsx en la carpeta DATA
archivos = search_xlsx(EXPORT)
print(archivos)
for i in range(len(archivos)):
    products = []

    for j in range(len(archivos[i]["subFolder"])):
        path = f'{archivos[i]["subFolder"][j]["path"]}'
        file_name = f'{archivos[i]["subFolder"][j]["file"]}'
        print(file_name)
        # Cargar el archivo de Excel existente
        AlphaWidthColums(path, file_name, './Salida/Esteticas/')

print(archivos)
