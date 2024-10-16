import pandas as pd
import os
import json
import numpy as np
import pandas as pd
import uuid


def make_dict_products_from_dataframe(dataframe_sku, dataframe_part_number, dataframe_producto, file_name, proveedor):
    # Crear una lista de diccionarios
    product_list = []
    categoria = ''
    try:
        categoria = file_name.split('.')[0].split(
            '-')[0].removesuffix(f' {proveedor}')
    except:
        print('No se pudo obtener el nombre de la categoria')

    # Iterar sobre los índices comunes de los tres DataFrames
    for index in set(dataframe_sku.index) & set(dataframe_part_number.index) & set(dataframe_producto.index):
        product = {
            'ID': str(uuid.uuid4()),
            'Sku': str(dataframe_sku.loc[index]) if pd.notna(dataframe_sku.loc[index]) else '',
            'Part_number': str(dataframe_part_number.loc[index]) if pd.notna(dataframe_part_number.loc[index]) else '',
            'Producto': str(dataframe_producto.loc[index]) if pd.notna(dataframe_producto.loc[index]) else '',
            'Dis. Antes': '',
            'Dis. Ahora': '',
            'Precio Antes': '',
            'Precio Ahora': '',
            'Categoria': categoria,
        }

        # Agregar el producto a la lista
        product_list.append(product)

    return product_list


def process_and_save_products_from_folders(archivos_cleaned, output_path, spinner):
    for i in range(len(archivos_cleaned)):
        proveedor = f'{archivos_cleaned[i]["folder"]}'
        spinner.write(f'{archivos_cleaned[i]["folder"]}')
        products = []

        for j in range(len(archivos_cleaned[i]["subFolder"])):
            path = f'{archivos_cleaned[i]["subFolder"][j]["path"]}'
            file_name = f'{archivos_cleaned[i]["subFolder"][j]["file"]}'
            print(file_name)
            datos = pd.read_excel(path, engine='openpyxl', skiprows=1)

            try:
                product_name = datos['PRODUCTO']
            except:
                try:
                    product_name = datos['PRODUCTOS']
                except:
                    product_name = pd.DataFrame()

            try:
                sku_values = datos['SKU']
            except:
                sku_values = pd.DataFrame()

            try:
                partnumber_values = datos['PART NUMBER']
            except:
                partnumber_values = pd.DataFrame()

            if not product_name.empty:
                indices_product_name = product_name.index
            else:
                print('No se encontraron productos')
                continue

            if sku_values.empty:
                sku_values = pd.DataFrame(
                    np.nan, index=indices_product_name, columns=['SKU'])['SKU']
            if partnumber_values.empty:
                partnumber_values = pd.DataFrame(np.nan, index=indices_product_name, columns=[
                                                 'PART NUMBER'])['PART NUMBER']

            products = products + make_dict_products_from_dataframe(
                sku_values, partnumber_values, product_name, file_name, proveedor)

        # Verificar si existe el directorio
        if not os.path.exists(output_path):
            # Crear directorio
            os.makedirs(output_path)

        with open(f'{output_path}/{archivos_cleaned[i]["folder"]}-products.json', 'w') as file:
            json.dump(products, file, indent=2)
