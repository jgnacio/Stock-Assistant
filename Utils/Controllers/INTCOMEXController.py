import json
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class INTCOMEXController(BaseController):
    search_input_css_selector = '#js-txtSearch'
    search_button_css_selector = '#btnSearch'

    product_css_selector = "div.productArea"
    product_area_details_css_selector = 'div.js-productAreaDetail'

    products_not_found_xpath = '//*[@id="detail-products-content"]/div[3]/div[1]/div[2]/div/div/p[2]'

    # Login elemetns
    login_button_css_selector = '#searchForm > div.row > div.text-right.col-lg-4.visible-lg.\@\*hidden\*\@.searchButtonsContainer > a.loaderAnimateLink.text-nounderlined.btn.btn-default'
    login_input_user_css_selector = '#signInName'
    login_input_password_css_selector = '#password'
    login_button_submit_css_selector = '#next'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'INTCOMEX'

    def login(self):
        # Hacer click en el boton de login
        self.click(css_selector=self.login_button_css_selector)

        # Ingresar usuario
        self.typeText(text=self.user,
                      css_selector=self.login_input_user_css_selector)

        # Ingresar contraseña
        self.typeText(text=self.password,
                      css_selector=self.login_input_password_css_selector)

        # Hacer click en el boton de login
        self.click(css_selector=self.login_button_submit_css_selector)

        time.sleep(5)

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
                          css_selector=self.search_input_css_selector, speed=5)

            try:
                # Hacer click en el boton de buscar
                self.simpleClick(
                    css_selector=self.search_button_css_selector, speed=10)
            except:
                print(f'No se encontro el producto {
                      producto.get("Producto", "")}', end=' - ')
                print(f'sku: {producto.get("Sku", "")}', end=' - ')
                print(f'part_number: {producto.get("Part_number", "")}')

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
                self.clearInput(css_selector=self.search_input_css_selector)
                continue

            # Verificar si el producto no fue encontrado
            not_found = self.getElementIn(
                xpath=self.products_not_found_xpath, speed=3)

            print(not_found, 'not_found')

            if not_found:
                print(f'No se encontro el producto {
                      producto.get("Producto", "")}', end=' - ')
                print(f'sku: {producto.get("Sku", "")}', end=' - ')
                print(f'part_number: {producto.get("Part_number", "")}')

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
                self.clearInput(css_selector=self.search_input_css_selector)
                continue

            # Buscamos el producto y hacemos click en el nombre
            product_element = self.getAllElementsIn(
                css_selector=self.product_css_selector, context=self.driver, speed=5)

            if product_element:
                product_element = product_element[0]

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
                self.clearInput(css_selector=self.search_input_css_selector)
                continue

            link = self.getElementIn(
                css_selector='a', context=product_element, speed=5)

            try:
                # Hacer click en el producto
                link.click()
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
                self.clearInput(css_selector=self.search_input_css_selector)
                continue

            # Esperar a que cargue la pagina
            time.sleep(2)

            product_area_details = self.getElementIn(
                css_selector=self.product_area_details_css_selector, speed=5)

            product_title = self.getElementIn(
                css_selector='div.js-productName', context=product_area_details, speed=5)

            product_ids = self.getElementIn(
                css_selector='div.text-muted.font-compact.center-xs', context=product_area_details, speed=5)

            try:
                product_sku = product_ids.text.split(' ')[2].replace('\n', '')
            except:
                product_sku = ''
            try:
                product_part_number = product_ids.text.split(' ')[8]
            except:
                product_part_number = ''

            product_details_right = self.getElementIn(
                css_selector='div.panel-sm-up.panel-default-sm-up.padding-10-sm-up.text-center', speed=5)

            try:
                product_details_text = product_details_right.text
                if '$' in product_details_text or 'USD' in product_details_text:
                    product_price = f'USD {product_details_text.split(' ')[1]}'
                else:
                    product_price = product_details_text
            except:
                product_price = ''

            # Obtenemos el titulo actual del producto
            try:
                self.products[i]['Producto'] = product_title.text
            except:
                pass
            print(self.products[i]['Producto'])

            # Obtenemos el sku del producto
            self.products[i]['Sku'] = product_sku

            # Obtenemos el part number del producto
            self.products[i]['Part_number'] = product_part_number

            self.products[i]['Precio Antes'] = self.products[i].get(
                'Precio Ahora', '')

            self.products[i]['Precio Ahora'] = product_price

            # Actualizar la fecha de ultima actualizacion
            self.products[i]['ultima_actualizacion'] = datetime.now(
            ).isoformat()
            print(self.products[i]['ultima_actualizacion'])

            print(self.products[i])

            # Limpiamos el campo de busqueda
            self.clearInput(css_selector=self.search_input_css_selector)
            self.productsSave()

            print(
                f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()
        return self.products
