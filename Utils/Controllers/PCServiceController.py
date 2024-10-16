import json
import random
import time
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class PCServiceController(BaseController):

    # Buscar producto
    search_input_css_selector = '#searchstr'
    desplegable_css_selector = '#searchAssistBox'

    # Productos
    product_name_xpath = '//*[@id="central"]/div[2]/h1'
    product_availability_css_selector = '#central > div.contentbody.product.id87347 > h1'
    products_price_xpath = '/html/body/section/section/section/div[1]/div[3]/div[2]/div[2]/div[2]/div/div[2]/div[1]'
    products_part_number_xpath = '//*[@id="central"]/div[2]/h2'
    products_description_css_selector = '#tabs-moreinfo > div > p'

    # Login
    login_home_css_selector = '#header_bottom_content > div.preview.item.item_2.resource.id12.qp-pcs-login > div'
    login_user_css_selector = '#usr'
    login_password_css_selector = '#psw'
    login_button_css_selector = '#btn'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'PCService'

    def login(self):
        # Iniciar sesion
        self.simpleClick(css_selector=self.login_home_css_selector)

        self.typeText(text=self.user,
                      css_selector=self.login_user_css_selector)

        self.typeText(text=self.password,
                      css_selector=self.login_password_css_selector)

        self.simpleClick(css_selector=self.login_button_css_selector)

        time.sleep(3)

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        complete = self.getNumberOfProducts()

        # Iterar por la lista
        for i, product in enumerate(self.products):
            sku = product.get('Sku', "")
            part_number = product.get('Part_number', "")
            name = product.get('Producto', "")
            product_id = product.get('ID', "")

            if sku == '' and part_number == '' and name == '':
                print('Producto Vacio (Eliminado)')
                self.products.pop(i)
                continue

            # Verificar si contiene la key 'ultima_actualizacion'
            if 'ultima_actualizacion' in product:
                if product['ultima_actualizacion'] != '':
                    product['ultima_actualizacion'] = datetime.fromisoformat(
                        product['ultima_actualizacion'])

                # Verificar si el producto se actualizo en las ultimas 24 horas
                if self.checkLastUpdate(product['ultima_actualizacion'], self.hours_update):
                    print(f"El producto {
                          product["Producto"]} se actualizo hace menos de {self.hours_update} horas")

                    # Cambiar a formato iso (str)
                    product['ultima_actualizacion'] = product['ultima_actualizacion'].isoformat(
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

                time.sleep(2)

                if desplegable.is_displayed():
                    print(f'{search} ✅')
                    break
                else:
                    print(f'{search} ❌')

                search_input.clear()

            if not desplegable or not desplegable.is_displayed():
                print(f'No se encontro el producto {search}')
                self.updateAttribute(
                    product_id, 'Dis. Antes', product.get('Dis. Ahora', '')
                )

                self.updateAttribute(
                    product_id, 'Dis. Ahora', 'No')

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
                print(f'No se encontro el producto {search}')
                self.updateAttribute(
                    product_id, 'Dis. Antes', product.get('Dis. Ahora', '')
                )

                self.updateAttribute(
                    product_id, 'Dis. Ahora', 'No')

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')
                continue

            if len(link_products) > self.number_in_list:
                link_products = link_products[:self.number_in_list]

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
                    key_word = clickable[index].text.split(' ')[0]
                except:
                    continue

                # If not is a candidate to be the product
                if key_word != name.split(' ')[0]:
                    continue

                try:
                    clickable[index].click()
                except:
                    continue
                time.sleep(0.5)

                # Obtener el nombre del producto
                products_name = self.loadText(
                    xpath=self.product_name_xpath, speed=3)

                # Obtener el Precio Ahora del producto
                products_price = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.XPATH, self.products_price_xpath))).text

                # Obtener el numero de parte del producto
                products_part_number = self.loadText(
                    xpath=self.products_part_number_xpath, speed=3)

                if index == 0:
                    # Actualizar datos del producto
                    product['Sku'] = ""
                    product['Producto'] = products_name
                    product['Part_number'] = products_part_number
                    product['Precio Antes'] = product.get('Precio Ahora', '')
                    product['Precio Ahora'] = products_price
                    product['Dis. Ahora'] = ''
                    product['ultima_actualizacion'] = datetime.now(
                    ).isoformat()
                else:
                    # Crear un nuevo producto
                    producto = {
                        'Sku': "",
                        'Producto': products_name,
                        'Part_number': products_part_number,
                        'Precio Antes': product.get('Precio Ahora', ''),
                        'Precio Ahora': products_price,
                        'Dis. Ahora': '',
                        'ultima_actualizacion': datetime.now().isoformat()
                    }
                    self.addProduct(producto)

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

            self.clearInput(css_selector=self.search_input_css_selector)
            self.productsSave()

        print(
            f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()

        return self.products
