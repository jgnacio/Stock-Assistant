import json
import random
import time
from datetime import datetime
from Utils.Controllers.BaseController import BaseController


class MicroglobalController(BaseController):

    # Navbar
    login_navbar_xpath = '/html/body/div[2]/div/div/div/div[1]/ul/li[2]/a'

    # Formulario de login
    login_client_number_css_selector = 'input#Cliente'
    login_user_css_selector = 'input#Usuario'
    login_password_css_selector = 'input#Clave'
    login_button_css_selector = '#boton-login'

    # Ir la pestaña de compra
    buy_tab_xpath = '/html/body/div[2]/div/div/div/div[2]/div/ul/li[1]/a'

    # Buscar producto
    search_input_css_selector = 'input#buscar'
    desplegable_css_selector = '#ui-id-1'

    # Productos
    product_name_xpath = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[4]'
    product_sku_xpath = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[1]'
    products_price_xpath = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[6]'
    products_part_number_xpath = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[5]'
    products_iva_xpath = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[7]'
    products_vto_promo = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[9]'
    products_stock = '//*[@id="frmMPage"]/table/tbody/tr[2]/td[10]'
    products_description_css_selector = '#oculto_GB0064 > p.espaciado.descripion_padding'

    # Catalogo tabla
    table_css_selector = '#frmMPage > table > tbody'
    table_rows_css_selector = '#frmMPage > table > tbody > tr.producto'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Microglobal'

    def login(self):
        # Hacer click en el boton de login
        self.simpleClick(xpath=self.login_navbar_xpath)

        # Escribir el numero de cliente
        self.typeText(text=self.user,
                      css_selector=self.login_client_number_css_selector)

        # Escribir la contraseña
        self.typeText(text=self.password,
                      css_selector=self.login_password_css_selector)

        # Esperar un tiempo considerable
        self.driver.implicitly_wait(random.randint(2, 4))

        # Hacer click en el boton de login
        self.simpleClick(css_selector=self.login_button_css_selector)

        # Esperar a que se cargue la pagina
        self.driver.implicitly_wait(random.randint(2, 4))

        # Hacer click en la pestaña de compra
        self.simpleClick(xpath=self.buy_tab_xpath)

        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[0])
        self.driver.close()
        self.driver.switch_to.window(handles[1])

        time.sleep(3)

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
            producto_id = producto.get('ID', "")

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

            if not search_input:
                print('No se pudo escribir en el campo de busqueda')
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
                print(f'No se encontro el producto {name}', end=' - ')

                self.updateAttribute(
                    producto_id, 'Dis. Antes', producto.get('Dis. Ahora', '')
                )

                self.updateAttribute(
                    producto_id, 'Dis. Ahora', 'No')

                # Actualizar lista de productos en el json
                self.productsSave()

                # Limpiamos el campo de busqueda
                self.clearInput(
                    css_selector=self.search_input_css_selector)

                print(
                    f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')
                continue

            link_products = self.getAllElementsIn(
                css_selector='li > a', context=desplegable)

            if not link_products or not desplegable.is_displayed():
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

            # Iterar por los links
            for i, link_text in enumerate(link_products):

                # Limpiar el campo de busqueda
                if i > 0:
                    self.clearInput(
                        css_selector=self.search_input_css_selector)

                    # Buscar el producto
                    self.typeText(text=link_text,
                                  css_selector=self.search_input_css_selector)

                link_a = self.getAllElementsIn(
                    css_selector='li > a', context=desplegable)

                if not link_a:
                    continue

                for link in link_a:
                    try:
                        link.click()
                    except:
                        continue
                    # Cargar Tabla
                    table = self.getElementIn(
                        css_selector=self.table_css_selector)

                    if not table:
                        continue

                    # Cargar filas
                    rows = self.getAllElementsIn(
                        css_selector=self.table_rows_css_selector, context=table)

                    if not rows:
                        continue

                    # Iterar por las filas
                    for row_index, row in enumerate(rows):
                        # Hacer click para ver mas informacion
                        row.click()

                        get_sku = self.loadText(
                            css_selector='td:nth-child(1)', context=row)
                        get_name = self.loadText(
                            css_selector='td:nth-child(4)', context=row)
                        get_part_number = self.loadText(
                            css_selector='td:nth-child(5)', context=row)
                        get_price = self.loadText(
                            css_selector='td:nth-child(6)', context=row)
                        get_iva = self.loadText(
                            css_selector='td:nth-child(7)', context=row)
                        get_imp_int = self.loadText(
                            css_selector='td:nth-child(8)', context=row)
                        get_vto_promo = self.loadText(
                            css_selector='td:nth-child(9)', context=row)
                        get_stock = self.loadText(
                            css_selector='td:nth-child(10)', context=row)

                        all_descriptions = self.getAllElementsIn(
                            css_selector=f'tr.detalleproducto.azulbor', context=table)

                        try:
                            information = all_descriptions[row_index]
                            get_description = self.loadText(
                                css_selector='p.espaciado.descripion_padding', context=information)
                        except:
                            get_description = ''

                        if get_stock == '' or get_stock == '0':
                            get_Dis = 'No'
                        else:
                            get_Dis = ''

                        # Limpiar el sku
                        get_sku = get_sku.replace(
                            ' ', '').replace('\n', '').replace('\t', '')

                        # Limpiar el part_number
                        get_part_number = get_part_number.replace(
                            ' ', '').replace('\n', '').replace('\t', '')

                        if row_index == 0:
                            # Actualizar datos del producto
                            producto['Sku'] = get_sku
                            producto['Part_number'] = get_part_number
                            producto['Producto'] = get_name
                            producto['Precio Antes'] = producto.get(
                                'Precio Ahora', '')
                            producto['Precio Ahora'] = get_price
                            producto['IVA'] = get_iva
                            producto['Impuesto_interno'] = get_imp_int
                            producto['Vto_promo'] = get_vto_promo
                            producto['Stock'] = get_stock
                            producto['Dis. Antes'] = producto.get(
                                'Dis. Ahora', '')
                            producto['Dis. Ahora'] = get_Dis
                            producto['ultima_actualizacion'] = datetime.now(
                            ).isoformat()
                        else:
                            # Crear un nuevo producto
                            producto = {
                                'Sku': get_sku,
                                'Part_number': get_part_number,
                                'Producto': get_name,
                                'Precio Antes': producto.get('Precio Ahora', ''),
                                'Precio Ahora': get_price,
                                'IVA': get_iva,
                                'Impuesto_interno': get_imp_int,
                                'Vto_promo': get_vto_promo,
                                'Stock': get_stock,
                                'Dis. Antes': producto.get('Dis. Ahora', ''),
                                'Dis. Ahora': get_Dis,
                                'ultima_actualizacion': datetime.now().isoformat()
                            }
                            self.addProduct(producto)

                        # Limpiamos el campo de busqueda
                        self.clearInput(
                            css_selector=self.search_input_css_selector)

                        self.productsSave()

                        continue

                    self.productsSave()

            # Limpiamos el campo de busqueda
            self.clearInput(css_selector=self.search_input_css_selector)

            self.productsSave()
        print(
            f' {i+1}/{complete} \033[94m{complete - (i+1)} productos por actualizar\033[0m')

        # Actualizar lista de productos en el json
        self.productsSave()

        return self.products
