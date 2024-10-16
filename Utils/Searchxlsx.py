import os
import glob
import re

def search_xlsx(folder):
    files_xlsx = []

    # Obtener la lista de files xlsx en la carpeta actual
    files_in_folder = glob.glob(os.path.join(folder, '*.xlsx'))
    for file in files_in_folder:
        name_file = os.path.basename(file)
        files_xlsx.append({'path': file, 'file': name_file, 'subFolder': []})

    # Obtener la lista de subfolders en la carpeta actual, excluyendo los que comienzan con "."
    subfolders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) and not re.match(r'^\.', name)]

    # Recorrer las subcarpetas y buscar files xlsx en cada una de ellas de forma recursiva
    for subfolder in subfolders:
        subfolder_path = os.path.join(folder, subfolder)
        files_xlsx.append({
            'path': subfolder_path,
            'folder': subfolder,
            'subFolder': search_xlsx(subfolder_path)
        })

    return files_xlsx