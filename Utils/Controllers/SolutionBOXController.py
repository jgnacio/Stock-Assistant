import json
import random
import time
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class SolutionBOXController(BaseController):

    # Buscar producto
    search_input_css_selector = '#navbarScroll > form > div.search-bar-container > div > input'
    desplegable_xpath = '//*[@id="navbarScroll"]/form/div[2]/div'

    # Productos
    product_name_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(2) > div > div:nth-child(2) > div.sc-jXbUNg.hfCbZb > h1'
    products_price_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(2) > div > div:nth-child(2) > div.sc-jlZhew.hsoPYN'
    products_part_number_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(2) > div > div:nth-child(2) > div:nth-child(4) > p'
    products_description_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(1) > div.sc-gsFSXq.dAiQbv > div > p'
    products_guarranty_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(2) > div > div:nth-child(2) > div.sc-kpDqfm.lbkCZR > div > span.detalle > p'
    product_stock_css_selector = '#root > div.sc-gFqAkR.iQSuWw > div > div > div.sc-gEvEer.cAlgxB > div:nth-child(2) > div > div:nth-child(2) > div.sc-kpDqfm.lbkCZR > div > span.more > p'

    # Login
    login_home_css_selector = '#dropdown-basic'
    login_home_button_css_selector = '#dropdown-menu-align-responsive-1 > div > a:nth-child(1)'
    login_user_css_selector = '#root > div.container-fluid.d-flex.justify-content-center.align-items-center.bg-light > div > div:nth-child(1) > div > form > div:nth-child(2) > input'
    login_password_css_selector = '#root > div.container-fluid.d-flex.justify-content-center.align-items-center.bg-light > div > div:nth-child(1) > div > form > div:nth-child(3) > input'
    login_button_css_selector = '#root > div.container-fluid.d-flex.justify-content-center.align-items-center.bg-light > div > div:nth-child(1) > div > form > div.input-group.mb-3 > button'
    check_login_css_selector = '#navbarScroll > div.btnLogueado'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Solution BOX'

    def login(self):
        # Iniciar sesion
        self.simpleClick(css_selector=self.login_home_css_selector)

        self.simpleClick(css_selector=self.login_home_button_css_selector)

        self.typeText(text=self.user,
                      css_selector=self.login_user_css_selector)

        self.typeText(text=self.password,
                      css_selector=self.login_password_css_selector)

        self.simpleClick(css_selector=self.login_button_css_selector)
        time.sleep(3)

    def searchProducts(self):
        if not self.products:
            raise Exception('No se especifico ningun producto')

        login = self.getElementIn(
            css_selector=self.check_login_css_selector, speed=5
        )

        if not login:
            print(
                '\033[94mNo fue posible iniciar sesion, alguien puede estar usando la cuenta en este momento\033[0m')
            return

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

                desplegable = self.getElementIn(xpath=self.desplegable_xpath)

                time.sleep(2)

                if desplegable.is_displayed():
                    print(f'{search} ✅')
                    break
                else:
                    print(f'{search} ❌')

                search_input.clear()

            if not desplegable or not desplegable.is_displayed():
                print(f'No se encontro el producto {search}')

                # Actualizamos Dis. Antes del producto
                self.products[i]['Dis. Antes'] = self.products[i]['Dis. Ahora']
                # Actualizamos Dis. Ahora del producto
                self.products[i]['Dis. Ahora'] = 'No'

                # Actualizar la fecha de ultima actualizacion
                self.products[i]['ultima_actualizacion'] = datetime.now(
                ).isoformat()

                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')
                continue

            link_products = self.getAllElementsIn(
                css_selector='div.suggested-result', context=desplegable) or []

            if len(link_products) == 0 or not desplegable.is_displayed():
                print(f'No se encontro el producto {search}')

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
                        xpath=self.desplegable_xpath)

                    time.sleep(2)
                    clickable = self.getAllElementsIn(
                        css_selector='div.suggested-result', context=desplegable)

                try:
                    key_word = clickable[index].text.split(' ')[0]

                    # If not is a candidate to be the product
                    if key_word != name.split(' ')[0]:
                        continue
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
                products_name = self.loadText(
                    css_selector=self.product_name_css_selector, speed=5)

                # Obtener el Precio Ahora del producto
                products_price_element = self.getElementIn(
                    css_selector=self.products_price_css_selector
                )

                try:
                    products_price = products_price_element.text
                except:
                    products_price = ''

                # Obtener el numero de parte del producto
                products_part_number = self.loadText(
                    css_selector=self.products_part_number_css_selector, speed=5)

                # Limpiar el numero de parte
                try:
                    if products_part_number is not None and ':' in products_part_number:
                        products_part_number = products_part_number.split(': ')[
                            1]
                    else:
                        products_part_number = ''
                except:
                    pass

                # Obtener la garantia del producto
                products_guarranty = self.loadText(
                    css_selector=self.products_guarranty_css_selector, speed=2)
                # Limpiar la garantia
                try:
                    if products_guarranty is not None and products_guarranty != '':
                        products_guarranty = products_guarranty.split(': ')[1]
                except:
                    pass
                # Obtener el stock del producto
                products_stock = self.loadText(
                    css_selector=self.product_stock_css_selector, speed=2)
                # Limpiar el stock
                try:
                    if products_stock is not None and products_stock != '':
                        products_stock = products_stock.split(': ')[1]
                except:
                    pass
                get_Dis = 'No'

                if products_stock == '' or products_stock == '0':
                    get_Dis = 'No'
                else:
                    get_Dis = ''

                if index == 0:
                    # Actualizar datos del producto
                    product['Sku'] = ""
                    product['Part_number'] = products_part_number or ''
                    product['Producto'] = products_name
                    product['Precio Antes'] = product.get('Precio Ahora', '')
                    product['Precio Ahora'] = products_price
                    product['Stock'] = products_stock or ''
                    product['Garantia'] = products_guarranty or ''
                    product['Dis. Antes'] = product.get('Dis. Ahora', '')
                    product['Dis. Ahora'] = get_Dis
                    product['ultima_actualizacion'] = datetime.now(
                    ).isoformat()
                else:
                    # Crear un nuevo producto
                    producto = {
                        'Sku': "",
                        'Part_number': products_part_number,
                        'Producto': products_name,
                        'Precio Antes': product.get('Precio Ahora', ''),
                        'Precio Ahora': products_price,
                        'Stock': products_stock,
                        'Garantia': products_guarranty,
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
