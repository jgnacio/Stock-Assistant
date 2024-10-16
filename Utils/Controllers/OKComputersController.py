import json
import random
import time
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class OKComputersController(BaseController):

    # Navbar
    # login_navbar_xpath = '/html/body/div[2]/div/div/div/div[1]/ul/li[2]/a'

    # Formulario de login
    # login_client_number_css_selector = 'input#Cliente'
    # login_user_css_selector = 'input#Usuario'
    # login_password_css_selector = 'input#Clave'
    # login_button_css_selector = '#boton-login'

    # Ir la pestaña de compra
    # buy_tab_xpath = '/html/body/div[2]/div/div/div/div[2]/div/ul/li[1]/a'

    # Buscar producto
    search_input_css_selector = '#buscador_select'
    desplegable_css_selector = '#eac-container-buscador_select > ul'

    # Productos
    product_name_css_selector = '#contenedor_31 > div.nombre_cont > h1'
    products_price_without_off_css_selector = '#contenedor_precio_anterior > div.prod_preciomas2'
    products_price_css_selector = '#contenedor_31 > div.opciones_cont > div.cont > div.precios_cont > div.precio_cont_mas > div.prod_preciomas'
    products_part_number_xpath = '//*[@id="contenedor_31"]/div[2]/span[2]'
    products_description_css_selector = '#contenedor_31 > div.desc'
    products_off_css_selector = '#contenedor_31 > div.opciones_cont > div.cont > div.descuento_especial > div > span.valor'
    products_guarantee_css_selector = '#contenedor_31 > div.prod_datos_extendidos > div.gendatacont > table > tbody > tr.garantia > td.data.garantia2'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'OK Computers'

    # def login(self):
    #     # Hacer click en el boton de login
    #     self.simpleClick(xpath=self.login_navbar_xpath)

    #     # Escribir el numero de cliente
    #     self.typeText(text=self.user,
    #                   css_selector=self.login_client_number_css_selector)

    #     # Escribir la contraseña
    #     self.typeText(text=self.password,
    #                   css_selector=self.login_password_css_selector)

    #     # Esperar un tiempo considerable
    #     self.driver.implicitly_wait(random.randint(2, 4))

    #     # Hacer click en el boton de login
    #     self.simpleClick(css_selector=self.login_button_css_selector)

    #     # Esperar a que se cargue la pagina
    #     self.driver.implicitly_wait(random.randint(2, 4))

    #     # Hacer click en la pestaña de compra
    #     self.simpleClick(xpath=self.buy_tab_xpath)

    #     handles = self.driver.window_handles
    #     self.driver.switch_to.window(handles[0])
    #     self.driver.close()
    #     self.driver.switch_to.window(handles[1])

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        # Cargar las credenciales
        self.credentials()

        # Productos a eliminar
        products_to_drop = []

        self.productsSave()

        complete = self.getNumberOfProducts()

        # Iterar por la lista
        for i, producto in enumerate(self.products):
            sku = producto.get('Sku', "")
            part_number = producto.get('Part_number', "")
            name = producto.get('Producto', "")

            if sku == '' and part_number == '' and name == '':
                print('Producto Vacio -> (Eliminado)')
                self.products.pop(i)
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

            desplegable = None
            search = ""
            search_input = self.getElementIn(
                css_selector=self.search_input_css_selector)

            for search in [sku, part_number, name]:
                if search == '':
                    continue
                # Buscar el producto
                search_input.send_keys(search)

                desplegable = self.getElementIn(
                    css_selector=self.desplegable_css_selector)

                time.sleep(1)

                if desplegable.is_displayed():
                    print(f'{search} - encontrado')
                    break
                else:
                    print(f'{search} - no encontrado')

                search_input.clear()

            if not desplegable or not desplegable.is_displayed():
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
                        css_selector=self.desplegable_css_selector)

                    time.sleep(1)
                    clickable = self.getAllElementsIn(
                        css_selector='li', context=desplegable)

                try:
                    clickable[index].click()
                except:
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
                time.sleep(0.5)

                # Obtener el nombre del producto
                product_name = self.loadText(
                    css_selector=self.product_name_css_selector)

                products_price_element = self.getElementIn(
                    css_selector=self.products_price_css_selector)

                try:
                    products_price = products_price_element.text
                except:
                    products_price = ''

                # Obtener el Precio Ahora sin descuento del producto
                products_price_without_off = self.loadText(
                    css_selector=self.products_price_without_off_css_selector, speed=5)

                # Obtener el numero de parte del producto
                products_part_number = self.loadText(
                    xpath=self.products_part_number_xpath, speed=5)

                # Obtener el descuento del producto
                products_off = self.loadText(
                    css_selector=self.products_off_css_selector, speed=5)

                # Obtener la garantia del producto
                products_guarantee = self.loadText(
                    css_selector=self.products_guarantee_css_selector, speed=5)

                # Actualizar datos del producto
                producto['Sku'] = ""
                producto['Producto'] = product_name
                producto['Part_number'] = products_part_number
                producto['Precio Antes'] = producto.get('Precio Ahora', "")
                producto['Precio Ahora'] = products_price
                producto['Precio Ahora_sin_descuento'] = products_price_without_off
                producto['Descuento'] = products_off
                producto['Garantia'] = products_guarantee
                producto['Dis. Antes'] = producto.get('Dis. Ahora', "")
                producto['Dis. Ahora'] = ''
                producto['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                self.products.append(producto)

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                self.productsSave()
                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

            self.products.pop(i)
            self.clearInput(css_selector=self.search_input_css_selector)

        print(
            f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()

        return self.products
