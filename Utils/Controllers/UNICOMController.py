import json
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
import time


class UNICOMController(BaseController):
    search_input_xpath = '//*[@id="SearchQuery"]'
    search_button_xpath = '/html/body/header/div[2]/div[1]/div/div[2]/form/div/span/button'

    product_xpath = '/html/body/section/div/div[3]/div[2]/div/div[2]/div/div/h4/a'
    product_title_xpath = '/html/body/section/div[1]/div[2]/div[2]/div[1]/h2'
    products_part_number_xpath = '//*[@id="detail-tab"]/div[1]/table/tbody/tr/td[1]'
    product_description_xpath = '/html/body/section/div[1]/div[2]/div[2]/div[6]'
    product_sku_xpath = '/html/body/section/div[1]/div[2]/div[2]/p'
    products_price_xpath = '//*[@id="detail-tab"]/div[1]/div[4]/div[1]/p'
    product_availability_xpath = '//*[@id="detail-tab"]/div[1]/div[5]/label'
    product_guarantee_xpath = '//*[@id="detail-tab"]/div[1]/div[7]/div[1]'

    # Login elemetns
    login_button_xpath = '/html/body/header/div[2]/div[1]/div/div[3]/ul/li/div/button'
    login_input_user_xpath = '//*[@id="Username"]'
    login_input_password_xpath = '//*[@id="Password"]'
    login_button_submit_xpath = '//*[@id="ajax-form"]/form/div/div[4]/button'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'UNICOM'

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
                try:
                    print(f'No se encontro el producto {
                          self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get('Sku', "")}', end=' - ')
                    print(f'part_number: {
                          self.products[i].get('Part_number', "")}')
                except:
                    print('No se encontro el producto')

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', ''
                )
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
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', ''
                )
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
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', ''
                )
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

            self.products[i]['Dis. Ahora'] = ''

            self.products[i]['Sku'] = self.loadText(
                xpath=self.product_sku_xpath)

            try:
                # limpiar sku
                self.products[i]['Sku'] = self.products[i]['Sku'].split(': ')[
                    1]
            except:
                pass

            # Obtenemos el part number del producto
            self.products[i]['Part_number'] = self.loadText(
                xpath=self.products_part_number_xpath)

            # Actualizar la fecha de ultima actualizacion
            self.products[i]['ultima_actualizacion'] = datetime.now(
            ).isoformat()

            self.products[i]['Precio Antes'] = self.products[i].get(
                'Precio Ahora', '')

            # Obtener Precio Ahora
            self.products[i]['Precio Ahora'] = self.loadText(
                xpath=self.products_price_xpath)

            # Obtener garantia
            self.products[i]['Garantia'] = self.loadText(
                xpath=self.product_guarantee_xpath)

            try:
                # Limpiar garantia
                self.products[i]['Garantia'] = self.products[i]['Garantia'].split(':\n')[
                    1]
            except:
                pass

            # Limpiamos el campo de busqueda
            self.clearInput(xpath=self.search_input_xpath)
            self.productsSave()

            print(
                f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()
        return self.products
