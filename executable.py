import json
from Utils.SearchEngine import SearchEngine
from Utils.Steps import Setup, LOGS, PRODUCT_DATA_PATH
from datetime import datetime
import pytz
import yaspin
import time
import os


proveedores = ['INTCOMEX', 'Sultec', 'Starcenter', 'UNICOM', 'CDR', 'Diverol', 'Microglobal',
               'OK Computers', 'PCService', 'Solution BOX']

categorias = ['Notebooks', 'Monitores', 'Sillas', 'Gráficas']

controller = None
se = None

# crear una carpeta para los logs
if not os.path.exists(LOGS):
    os.makedirs(LOGS)


def endSearchOutput():
    print('La busqueda se ha completado con exito.✅\n')
    print('Los resultados se encuentran en la carpeta Salida, en formato xlsx.\n\n')
    time.sleep(2)


print(
    'Bienvenid@ al asistente de búsqueda de productos de \033[92mAslan Store\033[0m.\n')

if not os.path.exists(PRODUCT_DATA_PATH):
    print('Al parecer no has realizado ninguna búsqueda de productos.\nEs necesario analizar los archivos xlsx para poder realizar una búsqueda.')
    time.sleep(8)
    Setup()


while True:
    if not controller:
        print('Para comenzar, seleccione una de las siguientes opciones: ')
        print('Buscar en: ')
        print('  0. Todos los proveedores')
        for i, proveedor in enumerate(proveedores):
            print(f'  {i+1}. {proveedor}')
        print('\n')

        print(
            'Para buscar por categoría en todos los proveedores, ingrese el número correspondiente a la categoría: ')
        for i, categoria in enumerate(categorias):
            print(f'  {i + len(proveedores)+1}. {categoria}')
        print('\n')

        print('Borrar Datos: ')
        print(f'  {len(proveedores) +
              len(categorias) + 1}. Limpiar cache de todos los proveedores. \033[94m(Con backup de datos)\033[0m')
        print('\n')
        print(f'{len(proveedores) + len(categorias) + 2}. Salir ❌\n\n')
        try:
            proveedor = int(input('Ingrese una de las opciones: '))
        except:
            print('\033[91mOpción no valida\033[0m')
            time.sleep(0.5)
            continue

        if proveedor == len(proveedores) + len(categorias) + 2:
            print('Hasta luego!👋')
            time.sleep(1)
            break

        if proveedor >= len(proveedores) + 1 and proveedor < len(proveedores) + len(categorias) + 1:
            se = SearchEngine()

            for i in range(len(proveedores)):
                controller = proveedores[i]

                se.setupController(controller)
                # colocar el nombre de la categoria
                se.controller.productsLoader(
                    categorias[proveedor-len(proveedores)-1])
                print(se.controller.products)
                if not se.controller.products:
                    print(
                        f'No se encontraron productos en la categoria {categorias[proveedor-len(proveedores)-1]} del proveedor {proveedores[i]}')
                    continue
                se.open()
                if controller:
                    zona_horaria_uruguay = pytz.timezone('America/Montevideo')
                    print(f'Controlador {se.controller.name} cargado - {
                        datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S')}')
                try:
                    se.login()
                except:
                    pass
                with yaspin.yaspin(text=f'Exploración de productos en la página del proveedor {proveedores[i]}.') as sp:
                    # try:
                    se.search()
                    sp.ok("✅")
                    # except Exception as e:
                    #     sp.fail("❌")
                    #     print(f'Error al buscar productos en la página del proveedor {
                    #         proveedores[i]}', end='\n\n')
                    #     print(
                    #         'Mas información en el archivo de logs', end='\n\n')
                    #     se.save(categorias[proveedor-len(proveedores)-1])
                    #     try:
                    #         zona_horaria_uruguay = pytz.timezone(
                    #             'America/Montevideo')
                    #         with open(f'{LOGS}/{datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]}-{proveedores[i]}.txt', 'w') as file:
                    #             file.write(str(e))
                    #     except:
                    #         pass
                se.save(categorias[proveedor-len(proveedores)-1])
                endSearchOutput()

                continue
            continue

        if proveedor == len(proveedores) + len(categorias) + 1:
            Setup()
            controller = "Setup"
            continue
        if proveedor == 0:
            se = SearchEngine()
            for i in range(len(proveedores)):
                controller = proveedores[i]
                se.setupController(controller)
                se.controller.productsLoader()
                se.open()
                if controller:
                    zona_horaria_uruguay = pytz.timezone(
                        'America/Montevideo')
                    print(f'Controlador {se.controller.name} cargado - {
                        datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S')}')
                try:
                    se.login()
                except:
                    pass
                with yaspin.yaspin(text=f'Exploración de productos en la página del proveedor {proveedores[i]}.') as sp:
                    # try:
                    se.search()
                    sp.ok("✅")
                    # except Exception as e:
                    #     sp.fail("❌")
                    #     print(f'Error al buscar productos en la página del proveedor {
                    #         proveedores[i]}', end='\n\n')
                    #     print(
                    #         'Mas información en el archivo de logs', end='\n\n')
                    #     se.save()
                    #     try:
                    #         zona_horaria_uruguay = pytz.timezone(
                    #             'America/Montevideo')
                    #         with open(f'{LOGS}/{datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]}-{proveedores[i]}.txt', 'w') as file:
                    #             file.write(str(e))
                    #     except:
                    #         pass
                se.save()
                endSearchOutput()

        try:
            controller = proveedores[proveedor-1]
        except:
            print('\033[91mOpción no valida\033[0m')
            time.sleep(0.5)
            continue

        se = SearchEngine()
        se.setupController(controller)
        se.controller.productsLoader()
        se.open()
        if controller:
            zona_horaria_uruguay = pytz.timezone('America/Montevideo')
            print(f'Controlador {se.controller.name} cargado - {
                datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S')}')
        try:
            se.login()
        except:
            pass
        with yaspin.yaspin(text=f'Exploración de productos en la página del proveedor {proveedores[proveedor-1]}.') as sp:
            # try:
            se.search()
            sp.ok("✅")
            # except Exception as e:
            #     sp.fail("❌")
            #     print(f'Error al buscar productos en la página del proveedor {
            #         proveedores[proveedor-1]}', end='\n\n')
            #     print('Mas información en el archivo de logs', end='\n\n')
            #     se.save()
            #     zona_horaria_uruguay = pytz.timezone('America/Montevideo')
            #     with open(f'{LOGS}/{datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S')}-{proveedores[proveedor-1]}.txt', 'w') as file:
            #         file.write(str(e))
        se.quit()
        se.save()
        endSearchOutput()

    print('\n')

    print("Operación Realizada🚀\n")
    controller = None
    if se:
        try:
            se.quit()
        except:
            pass
        finally:
            se = None
