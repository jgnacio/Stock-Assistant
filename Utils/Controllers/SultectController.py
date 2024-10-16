import json
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
import time


class SultecController(BaseController):
    search_input_css_selector = 'input#ed'
    search_button_css_selector = 'button#catalogo_submit'
    text_Dis_xpath = '/html/body/div[2]/table/tbody/tr/td/div/div/div[1]/div[1]/div/div[2]/h6'

    product_css_selector = 'div.view.overlay.p-4'
    product_title_xpath = '//*[@id="main_div"]/div/div[1]/div[1]/div/div[2]/h3'
    product_sku_xpath = '//*[@id="main_div"]/div/dl[1]/dd[5]'
    product_guarantee_xpath = '//*[@id="main_div"]/div/dl[1]/dd[3]'
    products_price_css_selector = '#main_div > div > div.card.hoverable.mb-5.p-2 > div.card-body > div > div.col-lg-7.p-3 > h4'

    # Login elemetns
    login_button_css_selector = '#nav_login_info'
    login_select_login_css_selector = '#login_div > div > table > tbody > tr:nth-child(4) > td > table > tbody > tr:nth-child(3) > td.col_HL.text_title_3.pntr'
    login_input_user_css_selector = '#login_userid'
    login_input_password_css_selector = '#login_passwd'
    login_button_submit_css_selector = '#frm_login > button'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Sultec'

    def login(self):
        # Hacer click en el boton de login
        self.click(css_selector=self.login_button_css_selector)

        # Seleccionar el login de usuario
        self.click(css_selector=self.login_select_login_css_selector)

        # Ingresar usuario
        self.typeText(text=self.user,
                      css_selector=self.login_input_user_css_selector)

        # Ingresar contraseña
        self.typeText(text=self.password,
                      css_selector=self.login_input_password_css_selector)

        # Hacer click en el boton de login
        self.click(css_selector=self.login_button_submit_css_selector)

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
                          css_selector=self.search_input_css_selector)

            try:
                # Hacer click en el boton de buscar
                self.simpleClick(css_selector=self.search_button_css_selector)
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

            # Buscamos el producto
            product_element = self.getElementIn(
                css_selector=self.product_css_selector, speed=1)

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
                self.clearInput(css_selector=self.search_input_css_selector)
                continue

            # Obtenemos el texto de Dis. Ahora del producto
            disponibilidad = self.loadText(
                xpath=self.text_Dis_xpath)

            if disponibilidad == "Disponible para ordenar":
                self.products[i]['Dis. Antes'] = self.products[i].get(
                    'Dis. Ahora', '')

                self.products[i]['Dis. Ahora'] = ''

            # Obtenemos el titulo actual del producto
            self.products[i]['Producto'] = self.loadText(
                xpath=self.product_title_xpath)

            # Obtenemos el sku del producto
            self.products[i]['Sku'] = self.loadText(
                xpath=self.product_sku_xpath)

            # Obtenemos la garantia del producto
            self.products[i]['Garantia'] = self.loadText(
                xpath=self.product_guarantee_xpath)

            # Obtenemos el part number del producto
            self.products[i]['Part_number'] = producto['Producto'].split(
                ' ')[-1]

            # Actualizar la fecha de ultima actualizacion
            self.products[i]['ultima_actualizacion'] = datetime.now(
            ).isoformat()

            self.products[i]['Precio Antes'] = self.products[i].get(
                'Precio Ahora', '')

            # Obtener Precio Ahora
            self.products[i]['Precio Ahora'] = self.loadText(
                css_selector=self.products_price_css_selector)

            # Limpiamos el campo de busqueda
            self.clearInput(css_selector=self.search_input_css_selector)
            self.productsSave()

            print(
                f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()
        return self.products
