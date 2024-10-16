from datetime import datetime
import time
import random
import uuid
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class DiverolController(BaseController):

    search_input_xpath = '/html/body/header/div[2]/div/div/div/div[2]/div/form/input'
    search_button_xpath = '/html/body/header/div[2]/div/div/div/div[2]/div/form/button'

    product_css_selector = '.gi-product-inner'
    product_name_xpath = '/html/body/section[1]/div/div/div/div/div/div/div[2]/div/h5'
    product_description_css_selector = 'body > section.gi-single-product.padding-tb-40 > div > div > div > div > div > div > div.single-pro-desc.single-pro-desc-no-sidebar.m-t-991 > div > div.gi-single-list > ul > li:nth-child(3)'
    product_sku_css_selector = 'body > section.gi-single-product.padding-tb-40 > div > div > div > div > div > div > div.single-pro-desc.single-pro-desc-no-sidebar.m-t-991 > div > div.gi-single-list > ul > li:nth-child(1)'
    product_price_xpath = '/html/body/section[1]/div/div/div/div/div/div/div[2]/div/div[2]/div/div[1]'
    product_availability_xpath = '/html/body/section[1]/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]'

    # Login
    login_home_xpath = '/html/body/header/div[2]/div/div/div/div[3]/div/div/a'
    login_home_button_login_xpath = '/html/body/header/div[2]/div/div/div/div[3]/div/div/ul/li[1]/a'
    login_user_xpath = '/html/body/section/div/div[2]/div/div/div/div/form/span[1]/input'
    login_password_xpath = '/html/body/section/div/div[2]/div/div/div/div/form/span[2]/input'
    login_button_xpath = '/html/body/section/div/div[2]/div/div/div/div/form/span[4]/button'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Diverol'

    def login(self):
        # Iniciar sesion
        self.simpleClick(xpath=self.login_home_xpath)

        self.simpleClick(xpath=self.login_home_button_login_xpath)

        self.typeText(text=self.user, xpath=self.login_user_xpath)

        self.typeText(text=self.password, xpath=self.login_password_xpath)

        self.simpleClick(xpath=self.login_button_xpath)

        time.sleep(3)

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        # Productos a eliminar
        products_to_drop = []

        self.productsSave()

        complete = self.getNumberOfProducts()

        # Iterar por la lista
        for i, producto in enumerate(self.products):
            sku = None
            part_number = None
            name = None
            if producto.get('Sku', '') != '':
                sku = producto['Sku']
            elif producto.get('Part_number', '') != '':
                part_number = producto['Part_number']
            elif producto.get('Producto', '') != '':
                name = producto['Producto']
            else:
                continue

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

            # Buscar el producto
            self.typeText(text=sku or part_number or name,
                          xpath=self.search_input_xpath)

            try:
                # Hacer click en el boton de buscar
                self.simpleClick(xpath=self.search_button_xpath)
            except:
                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', '')
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(css_selector=self.search_input_xpath)
                continue

            try:
                # Hacemos click en el producto que queremos
                located = self.click(css_selector=self.product_css_selector,
                                     speed=2, new_tab=True, find_tag='a')
            except:
                located = False

            # Cargar las pestañas abiertas (handles)
            handles = self.driver.window_handles

            if len(handles) <= 1:
                if located:
                    product_name = self.loadText(
                        xpath=self.product_name_xpath)

                    product_description = self.loadText(
                        css_selector=self.product_description_css_selector)

                    product_sku = self.loadText(
                        css_selector=self.product_sku_css_selector)

                    try:
                        product_sku = product_sku.split(': ')[1]

                    except:
                        pass

                    # Precio Ahora del producto
                    product_price = self.loadText(
                        xpath=self.product_price_xpath)

                    producto['Producto'] = product_name
                    producto['Sku'] = product_sku or producto['Sku'] or ''
                    producto['Dis. Ahora'] = ''
                    producto['Precio Antes'] = producto.get('Precio Ahora', "")
                    producto['Precio Ahora'] = product_price
                    producto['ultima_actualizacion'] = datetime.now(
                    ).isoformat()

                    self.productsSave()
                    print(
                        f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

                    # Limpiamos el campo de busqueda
                    self.clearInput(xpath=self.search_input_xpath)

                    continue
                else:
                    try:
                        print(f'No se encontro el producto {
                            self.products[i].get("Producto", "")}', end=' - ')
                        print(f'sku: {self.products[i].get(
                            'Sku', "")}', end=' - ')
                        print(f'part_number: {
                            self.products[i].get('Part_number', "")}')
                    except:
                        print('No se encontro el producto')

                    # Actualizamos Dis. Antes del producto
                    self.products[i]['Dis. Antes'] = self.products[i].get(
                        'Dis. Ahora', '')
                    # Actualizamos Dis. Ahora del producto
                    self.products[i]['Dis. Ahora'] = 'No'

                    # Actualizar la fecha de ultima actualizacion
                    self.products[i]['ultima_actualizacion'] = datetime.now(
                    ).isoformat()

                    # Actualizar lista de productos en el json
                    self.productsSave()

                    # Limpiamos el campo de busqueda
                    self.clearInput(css_selector=self.search_input_xpath)

            print('Multiple ventana')
            print(handles)

            # Iterar por las pestañas cambiando a la ultima pestaña sin contar la primera
            for index, handle in enumerate(handles[1:]):
                self.driver.switch_to.window(handle)

                # Obtenemos la informacion del producto
                print(f'-{handle}-')

                product_name = self.loadText(
                    xpath=self.product_name_xpath)

                product_description = self.loadText(
                    css_selector=self.product_description_css_selector)

                product_sku = self.loadText(
                    css_selector=self.product_sku_css_selector)

                try:
                    product_sku = product_sku.split(': ')[1]

                except:
                    pass

                # Precio Ahora del producto
                product_price = self.loadText(
                    xpath=self.product_price_xpath)

                if index == 0:
                    producto['Producto'] = product_name
                    producto['Sku'] = product_sku or producto['Sku'] or ''
                    producto['Dis. Ahora'] = ''
                    producto['Precio Antes'] = producto.get('Precio Ahora', "")
                    producto['Precio Ahora'] = product_price
                    producto['ultima_actualizacion'] = datetime.now(
                    ).isoformat()
                else:
                    # Crear un nuevo producto
                    producto = {
                        "ID": str(uuid.uuid4()),
                        "Sku": product_sku,
                        "Part_number": producto.get('Part_number', ""),
                        "Producto": product_name,
                        "Dis. Ahora": '',
                        "Precio Antes": producto.get('Precio Ahora', ""),
                        "Precio Ahora": product_price,
                        "Categoria": producto.get('Categoria', ""),
                        'ultima_actualizacion': datetime.now().isoformat()
                    }

                    self.addProduct(producto)

                self.productsSave()
                self.driver.close()

            # Cambiar a la primera pestaña
            self.driver.switch_to.window(handles[0])

            time.sleep(1)

            # Limpiamos el campo de busqueda
            self.clearInput(xpath=self.search_input_xpath)

            self.productsSave()
            print(
                f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Eliminar los productos de la lista products_to_drop
        for products in products_to_drop:
            self.products.remove(products)

        # Actualizar lista de productos en el json
        self.productsSave()

        return self.products
