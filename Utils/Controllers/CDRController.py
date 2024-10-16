from datetime import datetime
import time

from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class CDRController(BaseController):

    search_input_css_selector = 'input#buscador_select'
    search_product_item_css_selector = '#eac-container-buscador_select > ul'

    product_name_xpath_option_0 = '//*[@id="gencont2"]/div[2]/div[1]/h1'
    product_name_xpath_option_1 = '/html/body/div[4]/div[3]/div[2]/div[4]'
    product_description_css_selector = '#contenedor_35 > div.desc'
    product_sku_xpath = '//*[@id="contenedor_35"]/div[2]/div[3]/table/tbody/tr[1]/td[2]/span'
    product_guarantee_xpath = '/html/body/div[4]/div[3]/div[2]/div[9]/div[2]/div[3]/table/tbody/tr[6]/td[2]/span'
    product_part_number_xpath = '//*[@id="contenedor_35"]/div[2]/div[3]/table/tbody/tr[4]/td[2]'
    product_price_css_selector = '#gencont2 > div.gencont2cont > div.opciones_cont > div.cont > div.precios_cont > div.precio_cont_mas'
    product_off_css_selector = '#gencont2 > div.gencont2cont > div.opciones_cont > div.cont > div.descuento_especial'
    product_price_whiout_off_css_selector = '#contenedor_precio_anterior'

    # Login elements
    login_button_css_selector = '#bienvenida > div.bienvenidacont > div > div.usu > div.bienvenido > div.hlogin > div.hingresar > a'
    login_username_input_css_selector = '#login_usuario'
    login_password_input_css_selector = '#login_clave'
    login_submit_button_css_selector = '#btn_login_submit'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'CDR'

    def login(self):
        # Hacer click en el boton de login
        self.click(css_selector=self.login_button_css_selector)

        time.sleep(0.5)

        # Ingresar usuario
        self.typeText(text=self.user,
                      css_selector=self.login_username_input_css_selector)

        # Ingresar contraseña
        self.typeText(text=self.password,
                      css_selector=self.login_password_input_css_selector)

        # Hacer click en el boton de login
        self.click(css_selector=self.login_submit_button_css_selector)

        time.sleep(3)

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        complete = self.getNumberOfProducts()

        # Iterar por la lista
        for i, producto in enumerate(self.products):
            sku = producto.get('Sku', "")
            part_number = producto.get('Part_number', "")
            name = producto.get('Producto', "")

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

            search_input = self.getElementIn(
                css_selector=self.search_input_css_selector)

            for search in [sku, part_number, name]:
                if search == '':
                    continue

                # Buscar el producto
                search_input.send_keys(search)

                desplegable = self.getElementIn(
                    css_selector=self.search_product_item_css_selector)

                time.sleep(1)

                if desplegable.is_displayed():
                    print(f'{search} - encontrado')
                    break
                else:
                    print(f'{search} - no encontrado')

                search_input.clear()

            if not desplegable or not desplegable.is_displayed():
                print(f'No se encontro el producto {
                      name} - sku: {sku} - part_number: {part_number}')

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Actualizar lista de productos en el json
                self.productsSave()

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

                # Limpiamos el campo de busqueda
                search_input.clear()
                continue

            link_products = self.getAllElementsIn(
                css_selector='li', context=desplegable) or []

            if len(link_products) == 0 or not desplegable.is_displayed():
                try:
                    print(f"lista: {link_products}")
                    print(f'No se encontro el producto {
                        self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get(
                        'Sku', "")}', end=' - ')
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
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')
                continue

            link_products.pop()

            clickable = link_products

            for index in range(len(link_products)):
                if index != 0:
                    self.clearInput(
                        css_selector=self.search_input_css_selector)
                    self.typeText(
                        text=search, css_selector=self.search_input_css_selector)

                    desplegable = self.getElementIn(
                        css_selector=self.search_product_item_css_selector)

                    time.sleep(1)
                    clickable = self.getAllElementsIn(
                        css_selector='li', context=desplegable)

                try:
                    clickable[index].click()
                except:
                    print(f'No se encontro el producto {
                          self.products[i].get("Producto", "")}', end=' - ')
                    print(f'sku: {self.products[i].get('Sku', "")}', end=' - ')
                    print(f'part_number: {
                          self.products[i].get('Part_number', "")}')

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
                    self.clearInput(
                        css_selector=self.search_input_css_selector)

                    print(
                        f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')
                    continue
                time.sleep(0.5)

                # Obtenemos la informacion del producto
                try:
                    self.products[i]['Producto'] = self.loadText(
                        xpath=self.product_name_xpath_option_0, speed=1)
                except:
                    self.products[i]['Producto'] = self.loadText(
                        xpath=self.product_name_xpath_option_1, speed=1)

                self.products[i]['Sku'] = self.loadText(
                    xpath=self.product_sku_xpath, speed=1)

                self.products[i]['Part_number'] = self.loadText(
                    xpath=self.product_part_number_xpath, speed=1)

                self.products[i]['Precio Antes'] = self.products[i]['Precio Ahora']

                self.products[i]['Precio Ahora'] = self.loadText(
                    css_selector=self.product_price_css_selector, speed=1)

                # Limpiar Precio Ahora
                if self.products[i]['Precio Ahora']:
                    self.products[i]['Precio Ahora'] = self.products[i]['Precio Ahora'].replace(
                        '\n', ' ').replace(',', '.')
                else:
                    self.products[i]['Precio Ahora'] = ''

                self.products[i]['Precio Ahora_sin_descuento'] = self.loadText(
                    css_selector=self.product_price_whiout_off_css_selector, speed=1)

                if self.products[i]['Precio Ahora_sin_descuento']:
                    self.products[i]['Precio Ahora_sin_descuento'] = self.products[i]['Precio Ahora_sin_descuento'].replace(
                        'Antes\n', '').replace(',', '.')
                else:
                    self.products[i]['Precio Ahora_sin_descuento'] = ''

                self.products[i]['Descuento'] = self.loadText(
                    css_selector=self.product_off_css_selector, speed=1)

                # Limpiar descuento
                if self.products[i]['Descuento']:
                    self.products[i]['Descuento'] = self.products[i]['Descuento'].replace(
                        '\nOFF', '').replace(',', '.')
                else:
                    self.products[i]['Descuento'] = ''

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = ''

                # Ultima actualizacion del producto
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                # Obtenemos la garantia del producto y si es None
                self.products[i]['Garantia'] = self.loadText(
                    xpath=self.product_guarantee_xpath) or ''

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                self.productsSave()

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        self.products.pop(i)
        # Actualizar lista de productos en el json
        self.productsSave()

        return self.products

    def click(self, css_selector=None, xpath=None, speed=5):
        if not css_selector and not xpath:
            raise Exception('No se especifico ningun selector')
        if css_selector and xpath:
            raise Exception('No se puede especificar dos selectores')

        try:
            if css_selector:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))\
                    .click()
            if xpath:
                WebDriverWait(self.driver, speed)\
                    .until(EC.element_to_be_clickable((By.XPATH, xpath)))\
                    .click()
        except:
            raise Exception('No se pudo hacer click en el elemento')

        time.sleep(0.5)
