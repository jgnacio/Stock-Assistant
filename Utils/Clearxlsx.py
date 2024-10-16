import os
import pandas as pd
import shutil


def limpiar_excel(ruta_excel):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_excel, header=None, engine='openpyxl')
    df.reset_index(drop=True, inplace=True)
    # Lista de palabras clave para buscar
    palabras_clave = ['producto', 'Producto', 'Productos', 'productos', 'PRODUCTO',
                      'PRODUCTOS', 'Componente', 'COMPONENTE']

    # Encontrar la fila que contiene alguna de las palabras clave
    indice_fila_producto = df[df.apply(lambda row: any(
        palabra in row.values for palabra in palabras_clave), axis=1)].index

    # Si se encuentra la palabra 'Producto', eliminar las filas anteriores
    if not indice_fila_producto.empty:
        df = df.iloc[indice_fila_producto[0]:, :]

        # Eliminar columnas anteriores a la columna que contiene alguna de las palabras clave
        indice_columna_producto = df.apply(lambda col: any(
            palabra in col.values for palabra in palabras_clave), axis=0).idxmax()
        df = df.loc[:, indice_columna_producto:]

    # Eliminar filas que contienen solo valores NaN
    df_limpiado = df.dropna(axis=0, how='all')

    # Colocar la primera fila en mayúsculas
    df_limpiado.iloc[0] = df_limpiado.iloc[0].apply(
        lambda x: x.upper() if isinstance(x, str) else x).copy()

    return df_limpiado


def save_cleaned(archivos, CLEANED_PATH):
    for i in range(len(archivos)):
        # print(archivos[i]["folder"])
        cleaned_path = f'{CLEANED_PATH}/{archivos[i]["folder"]}'

        # Verificar si existe el directorio
        if not os.path.exists(cleaned_path):
            # Crear directorio
            os.makedirs(cleaned_path)
        else:
            # Eliminar carpeta y crearla de nuevo
            shutil.rmtree(cleaned_path)
            os.makedirs(cleaned_path)

        for j in range(len(archivos[i]["subFolder"])):
            path = f'{archivos[i]["subFolder"][j]["path"]}'
            try:
                # eliminar el .xlsx del nombre del archivo
                file_name = archivos[i]["subFolder"][j]["file"][:-5]
                limpiar_excel(path).to_excel(
                    f'{CLEANED_PATH}/{archivos[i]["folder"]}/{file_name}-cleaned.xlsx', engine='openpyxl')
            except:
                continue
