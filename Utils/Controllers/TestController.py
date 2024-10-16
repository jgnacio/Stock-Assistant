import json
import random
import time
from datetime import datetime
from Utils.Controllers.BaseController import BaseController
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class TestController(BaseController):

    table_css_selector = '#hockey > div > table'
    rows_css_selector = '#hockey > div > table > tbody > tr'

    pagination_css_selector = '#hockey > div > div.row.pagination-area > div.col-md-10.text-center > ul'

    def __init__(self, driver):
        super().__init__(driver)
        self.name = 'Test'

    def searchProducts(self):
        # if not self.products:
        #     raise Exception('No se especifico ningun producto')

        # Cargar las credenciales
        self.credentials()

        # Ir a la pagina
        self.driver.get(self.url)

        # Productos a eliminar
        products_to_drop = []

        # complete = self.getNumberOfProducts()

        # cargar la tabla
        table = self.getElementIn(css_selector=self.table_css_selector)

        print('tabla:', table)

        if not table:
            print('No se encontro la tabla')

        # Obtener las filas
        rows = self.getAllElementsIn(table, self.rows_css_selector)

        # imprimir las filas
        for row in rows:
            print(row.text)

        if not rows:
            print('No se encontraron las filas')

        # Obtener la paginacion
        pagination = self.getElementIn(
            css_selector=self.pagination_css_selector)

        pages = self.click(css_selector='li > a',
                           context=pagination, new_tab=True)

        print(pages)
