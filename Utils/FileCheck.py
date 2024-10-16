import json

def file_check(data):
    result = {}

    def file_count(sub_folder):
        # Función auxiliar para contar archivos de manera recursiva
        total_files = 0

        for element in sub_folder:
            total_files += 1  # Contar el archivo actual

            # Verificar si hay subFolder y contar archivos de manera recursiva
            if element["subFolder"]:
                total_files += file_count(element["subFolder"])

        return total_files

    for element in data:
        file_name = element["folder"]
        count = file_count(element["subFolder"])

        result[file_name] = {
            "file_count": count,
            "filechecked": 0
        }

    with open('./Process.json', 'w') as file:
        json.dump(result, file, indent=2)

    return result
