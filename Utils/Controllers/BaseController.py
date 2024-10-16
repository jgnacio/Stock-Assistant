import time
import json
from datetime import datetime, timedelta
from typing import List
import uuid
import pandas as pd
import os
import pytz
from Utils.Steps import LOGS


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import Utils.Steps as steps


class BaseController:
    def __init__(self, driver):
        self.driver = driver
        self.products = []
        self.url = None
        self.user_login = False
        self.user = None
        self.password = None
        self.hours_update = 12
        self.number_in_list = 1
        self.category = None

    def open(self):
        # Verificar si el driver esta configurado
        if not self.driver:
            raise Exception('El driver no esta configurado')

        # Cargar las credenciales
        self.credentials()

        # Ir a la pagina
        self.driver.get(self.url)

    def productsLoader(self, category=None):
        try:
            # Cargar los productos
            with open(f'{steps.PRODUCT_DATA_PATH}/{self.name}-products.json', 'r') as file:
                self.products = json.load(file)
                if category:
                    self.products = self.searchByCategory(category)
                else:
                    self.removeAllOfCategory('Notebooks')
        except Exception as e:
            raise Exception(
                f'No se pudo cargar los productos del proveedor {self.name}.', e)

        return self.products

    def removeAllOfCategory(self, category):
        if not self.products:
            raise Exception('No se especifico ningun producto')
        if category:
            productos_filtrados = []
            for producto in self.products:
                if 'Categoria' in producto and producto['Categoria'] != category:
                    productos_filtrados.append(producto)
            self.products = productos_filtrados
        else:
            raise Exception('No se especifico ninguna categoria')

    def productsSave(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')
        if self.category:
            if not os.path.exists(f'{steps.PRODUCT_DATA_PATH}/{self.category}'):
                os.mkdir(f'{steps.PRODUCT_DATA_PATH}/{self.category}')
            try:
                with open(f'{steps.PRODUCT_DATA_PATH}/{self.category}/{self.name}-products.json', 'w') as file:
                    json.dump(self.products, file, indent=2)
            except Exception as e:
                raise Exception(
                    f'No se pudo guardar los productos del proveedor {self.name}.', e)
        else:
            try:
                with open(f'{steps.PRODUCT_DATA_PATH}/{self.name}-products.json', 'w') as file:
                    json.dump(self.products, file, indent=2)
            except Exception as e:
                raise Exception(
                    f'No se pudo guardar los productos del proveedor {self.name}.', e)

    def find_product_by_id(self, product_id: str) -> int:
        for index, product in enumerate(self.products):
            if product.get('ID') == product_id:
                return product[index]
        return None

    def addProduct(self, product: dict):
        self.products.append(product)

    def addProducts(self, products: List[dict]):
        self.products.extend(products)

    def removeProduct(self, product_id: str):
        for index, product in enumerate(self.products):
            if product.get('ID') == product_id:
                self.products.pop(index)
                break

    def removeProducts(self, products_id: List[str]):
        for product_id in products_id:
            for index, product in enumerate(self.products):
                if product.get('ID') == product_id:
                    self.products.pop(index)
                    break

    def updateProduct(self, product_id: str):
        for index, product in enumerate(self.products):
            if product.get('ID') == product_id:
                self.products[index] = product
                break

    def checkLastUpdate(self, date, max_hours):
        # Obtener la fecha y hora actual
        ahora = datetime.now()

        # Calcular la fecha y hora límite restando las horas máximas
        limite = ahora - timedelta(hours=max_hours)

        # Verificar si la fecha objetivo está dentro del rango
        if limite <= date <= ahora:
            return True
        else:
            return False

    def updateAttribute(self, product_id: str, attribute: str, value: str):
        for index, product in enumerate(self.products):
            if product.get('ID') == product_id:
                self.products[index][attribute] = value
                self.updateLastModification(product_id)

    def updateLastModification(self, product_id: str):
        for index, product in enumerate(self.products):
            if product.get('ID') == product_id:
                self.products[index]['ultima_actualizacion'] = datetime.now(
                ).isoformat()
                break

    def generate_unique_id(self) -> str:
        return str(uuid.uuid4())

    def productsOrder(self, clave, valor):
        # Separar los elementos que cumplen con el criterio
        elementos_cumplen_criterio = [
            elemento for elemento in self.products if elemento.get(clave) == valor]

        # Separar los elementos que no cumplen con el criterio
        elementos_no_cumplen_criterio = [
            elemento for elemento in self.products if elemento.get(clave) != valor]

        # Ordenar la lista manteniendo primero los elementos que cumplen con el criterio
        resultado = elementos_cumplen_criterio + \
            sorted(elementos_no_cumplen_criterio, key=lambda x: x.get(clave))

        return resultado

    def credentials(self):
        try:
            with open(f'./Utils/AccessProviders.json', 'r') as file:
                access_providers = json.load(file)
        except Exception as e:
            raise Exception(f'No se pudo cargar los proveedores de acceso.', e)

        for provider in access_providers:
            if provider['name'] == self.name:
                self.url = provider['url']
                self.user = provider['user']
                self.password = provider['password']
                break

    def simpleClick(self, css_selector=None, xpath=None, speed=5):
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            if css_selector:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, css_selector)))\
                    .click()
            if xpath:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable(
                        (By.XPATH, xpath)))\
                    .click()
        except:
            raise Exception('No se pudo hacer click en el elemento')

    def getAllElementsIn(self, context, css_selector=None, xpath=None, speed=5):
        self.driver.implicitly_wait(speed)
        context = context or self.driver
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            # CSS Selector Options
            if css_selector:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, css_selector)))

            # Xpath Options
            if xpath:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_all_elements_located(
                        (By.XPATH, xpath)))
        except:
            return None

        return clickable

    def getElementIn(self, context=None, css_selector=None, xpath=None, speed=5):
        self.driver.implicitly_wait(speed)
        context = context or self.driver
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            # CSS Selector Options
            if css_selector:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, css_selector)))

            # Xpath Options
            if xpath:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_element_located(
                        (By.XPATH, xpath)))
        except:
            return None

        return clickable

    def click(self, css_selector=None, xpath=None, speed=5, new_tab=False, new_tab_one_ocurrence=False, new_tab_position=1, find_tag=None, context=None):
        self.driver.implicitly_wait(speed)
        context = context or self.driver
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            # CSS Selector Options
            if css_selector:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))

            # Xpath Options
            if xpath:
                clickable = WebDriverWait(context, speed)\
                    .until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        except:
            return None

        # checkear si contiene mas de un elemento
        if len(clickable) > 1:
            for element in clickable:
                print(clickable)
                print(element)
                enlace = element
                if find_tag:
                    enlace = WebDriverWait(element, 10).until(
                        EC.presence_of_element_located(
                            (By.TAG_NAME, find_tag))
                    )
                    print(enlace)
                if not new_tab:
                    enlace.click()
                else:
                    enlace.send_keys(Keys.CONTROL + Keys.RETURN)
            return clickable
        else:
            if new_tab and new_tab_one_ocurrence:
                clickable[0].send_keys(Keys.CONTROL + Keys.RETURN)
                return clickable[0]
            else:
                clickable[0].click()
                time.sleep(0.5)
                return clickable[0]

    def loadText(self, css_selector=None, xpath=None, speed=5, context=None):
        self.driver.implicitly_wait(speed)
        context = context or self.driver
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            if css_selector:
                return WebDriverWait(context, speed)\
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))\
                    .text
            if xpath:
                return WebDriverWait(context, speed)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath)))\
                    .text
        except:
            return None

    def clearInput(self, css_selector=None, xpath=None, speed=5):
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            if css_selector:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))\
                    .clear()
            if xpath:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath)))\
                    .clear()
        except:
            print("No se pudo limpiar el campo de busqueda")
            print("Recargando el driver...")
            self.driver.get(self.url)
            time.sleep(3)
        time.sleep(0.5)

    def typeText(self, text, css_selector=None, xpath=None, speed=5):
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            if css_selector:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))\
                    .send_keys(text)
            if xpath:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath)))\
                    .send_keys(text)
        except:
            pass
        time.sleep(0.5)

    def getNumberOfProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        return len(self.products)

    def thereAreOutdated(self):
        # Iterar por la lista
        for i, producto in enumerate(self.products):
            # Verificar si contiene la key 'ultima_actualizacion'
            if 'ultima_actualizacion' in producto:
                if producto['ultima_actualizacion'] != '':
                    self.products[i]['ultima_actualizacion'] = datetime.fromisoformat(
                        producto['ultima_actualizacion'])

                # Verificar si el producto se actualizo en las ultimas 24 horas
                if self.checkLastUpdate(self.products[i]['ultima_actualizacion'], self.hours_update):
                    print(f"El producto {
                          producto["Producto"]} se actualizo hace menos de {self.hours_update} horas")

                    # Actualizar la fecha de ultima actualizacion
                    self.products[i]['ultima_actualizacion'] = self.products[i]['ultima_actualizacion'].isoformat(
                    )
                    continue
                else:
                    return True
        return False

    def saveToExcel(self, category=None):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        # Verificar si existe la carpeta de salida
        if not os.path.exists(steps.EXPORT):
            os.mkdir(steps.EXPORT)

        # verificar si existe la carpeta de la categoria
        if category:
            if not os.path.exists(f'{steps.EXPORT}/{category}'):
                os.mkdir(f'{steps.EXPORT}/{category}')

        try:
            products_shadow = self.products[:]
            for product in products_shadow:
                if "ID" in product:
                    product.pop("ID")
                if "ultima_actualizacion" in product:

                    # Convertimos la cadena a un objeto datetime
                    ultima_actualizacion_dt = datetime.strptime(
                        product["ultima_actualizacion"], "%Y-%m-%dT%H:%M:%S.%f")

                    # Reformateamos la fecha al formato "día/mes/año"
                    ultima_actualizacion_formateada = ultima_actualizacion_dt.strftime(
                        "%d/%m/%Y")

                    product["ultima_actualizacion"] = ultima_actualizacion_formateada

                ordered_product = {}

                # Ordenar el diccionario por clave
                for key in sorted(product.keys()):
                    ordered_product[key] = product[key]
                product = ordered_product

            # Exportar a Excel
            if category:
                pd.DataFrame(products_shadow).to_excel(
                    f'{steps.EXPORT}/{category}/{self.name}-products.xlsx', index=False, engine='openpyxl')
            else:
                pd.DataFrame(products_shadow).to_excel(
                    f'{steps.EXPORT}/{self.name}-products.xlsx', index=False, engine='openpyxl')
        except Exception as e:
            print('Mas información en el archivo de logs', end='\n\n')
            try:
                zona_horaria_uruguay = pytz.timezone('America/Montevideo')
                with open(f'{LOGS}/{datetime.now(zona_horaria_uruguay).strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]}-{self.name}.txt', 'w') as file:
                    file.write(str(e))
            except:
                pass

    def searchByCategory(self, category):
        # filtra los elementos de self.products que contengan la categoria en la key Categoria
        filtered_products = []

        for product in self.products:
            try:
                if category in product['Categoria']:
                    filtered_products.append(product)
            except KeyError:
                # Si la clave 'Categoria' no existe en el producto, continuar al siguiente sin hacer nada
                pass

        return filtered_products
