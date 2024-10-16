import json
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
import time


class StarcenterController(BaseController):
    search_input_xpath = '//*[@id="main_sec"]/div[2]/div[1]/div/form/input'
    search_button_xpath = '//*[@id="main_sec"]/div[2]/div[1]/div/form/button'
    text_Dis_xpath = '/html/body/div[2]/table/tbody/tr/td/div/div/div[1]/div[1]/div/div[2]/h6'

    product_xpath = '//*[@id="app"]/div/section/div[2]/section[2]/section/div[1]/div/div[2]/div/h3/a'
    product_title_xpath = '//*[@id="app"]/div/div/div/div[1]/div[2]/div[1]/div[1]'
    products_part_number_xpath = '//*[@id="app"]/div/div/div/div[1]/div[2]/div[1]/div[2]/span'
    product_description_xpath = '//*[@id="app"]/div/div/div/div[1]/div[2]/div[2]/div[2]/span'
    products_price_xpath = '//*[@id="app"]/div/div/div/div[2]/div/div/div[2]/div[1]/div[2]'
    product_stock_xpath = '//*[@id="app"]/div/div/div/div[1]/div[2]/div[1]/div[2]/span[2]'

    # Login elemetns
    login_button_xpath = '//*[@id="main_sec"]/div[2]/div[1]/div/div[2]/div/span/span/div'
    login_input_user_xpath = '/html/body/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/input'
    login_input_password_xpath = '/html/body/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/input'
    login_button_submit_xpath = '//*[@id="main_sec"]/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/div[3]'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Starcenter'

    def login(self):
        # Hacer click en el boton de login
        self.simpleClick(xpath=self.login_button_xpath)

        # Ingresar usuario
        self.typeText(text=self.user, xpath=self.login_input_user_xpath)

        # Ingresar contraseña
        self.typeText(
            text=self.password, xpath=self.login_input_password_xpath)

        # Hacer click en el boton de login
        self.simpleClick(xpath=self.login_button_submit_xpath)

        time.sleep(3)

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        complete = self.getNumberOfProducts()

        # Iterar por la lista
        for i, producto in enumerate(self.products):
            sku = None
            part_number = None
            name = None
            if producto['Sku'] != '':
                sku = producto['Sku']
            elif producto['Part_number'] != '':
                part_number = producto['Part_number']
            elif producto['Producto'] != '':
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
                print('No se encontro el boton de buscar')
                try:
                    print(f'No se encontro el producto {
                          self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get('Sku', "")}', end=' - ')
                    print(f'part_number: {
                          self.products[i].get('Part_number', "")}')
                except:
                    print('No se encontro el producto')

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(xpath=self.search_input_xpath)
                continue

            # Buscamos el producto
            product_element = self.getElementIn(
                xpath=self.product_xpath, speed=1)

            if not product_element:
                try:
                    print(f'No se encontro el producto {
                          self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get('Sku', "")}', end=' - ')
                    print(f'part_number: {
                          self.products[i].get('Part_number', "")}')
                except:
                    print('No se encontro el producto')

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(xpath=self.search_input_xpath)
                continue

            try:
                # Hacemos click en el producto
                product_element.click()
            except:
                try:
                    print(f'No se encontro el producto {
                          self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get('Sku', "")}', end=' - ')
                    print(f'part_number: {
                          self.products[i].get('Part_number', "")}')
                except:
                    print('No se encontro el producto')
                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(xpath=self.search_input_xpath)
                continue

            # Obtenemos el titulo actual del producto
            self.products[i]['Producto'] = self.loadText(
                xpath=self.product_title_xpath)\

            self.products[i]['Stock'] = self.loadText(
                xpath=self.product_stock_xpath)

            if self.products[i]['Stock']:
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', '')
                self.products[i]['Dis. Ahora'] = ''

            # Obtenemos el part number del producto
            self.products[i]['Part_number'] = self.loadText(
                xpath=self.products_part_number_xpath)

            # Limpiar part number
            self.products[i]['Part_number'] = self.products[i]['Part_number'].split(': ')[
                1]

            # Actualizar la fecha de ultima actualizacion
            self.products[i]['ultima_actualizacion'] = datetime.now(
            ).isoformat()

            self.products[i]['Precio Antes'] = self.products[i].get(
                'Precio Ahora', '')

            # Obtener Precio Ahora
            self.products[i]['Precio Ahora'] = self.loadText(
                xpath=self.products_price_xpath)

            # Limpiamos el campo de busqueda
            self.clearInput(xpath=self.search_input_xpath)
            self.productsSave()

            print(
                f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()
        return self.products
