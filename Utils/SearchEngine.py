import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from Utils.Controllers.SultectController import SultecController
from Utils.Controllers.CDRController import CDRController
from Utils.Controllers.DiverolController import DiverolController
from Utils.Controllers.MicroglobalController import MicroglobalController
from Utils.Controllers.TestController import TestController
from Utils.Controllers.OKComputersController import OKComputersController
from Utils.Controllers.PCServiceController import PCServiceController
from Utils.Controllers.SolutionBOXController import SolutionBOXController
from Utils.Controllers.StarcenterController import StarcenterController
from Utils.Controllers.UNICOMController import UNICOMController
from Utils.Controllers.INTCOMEXController import INTCOMEXController

PROVIDERS_CONTOLLERS = {
    'Sultec': SultecController,
    'CDR': CDRController,
    'Diverol': DiverolController,
    'Microglobal': MicroglobalController,
    'OK Computers': OKComputersController,
    'PCService': PCServiceController,
    'Solution BOX': SolutionBOXController,
    'Starcenter': StarcenterController,
    'UNICOM': UNICOMController,
    'INTCOMEX': INTCOMEXController,
    'Test': TestController
}


class SearchEngine:

    def __init__(self):
        self.configuration()
        self.controller = None

    def configuration(self, maximized=True, headless=False, disable_extensions=True, user_agent=None, minimized=True):

        user_agent = user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

        # Opciones de navegacion
        opt = webdriver.ChromeOptions()
        opt.add_argument(f'user-agent={user_agent}')  # User Agent
        maximized and opt.add_argument(
            '--start-maximized')  # Inicializar maximizada
        minimized and opt.add_argument(
            '--start-minimized')  # Inicializar minimizada
        disable_extensions and opt.add_argument(
            '--disable-extensions')  # Deshabilitar extensiones
        headless and opt.add_argument('--headless')  # headless mode

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opt
        )

    def setupController(self, provider_name):
        self.checkConfiguration(controller=False)

        # Verificar que el controlador del proveedor este en la lista de proveedores
        if not provider_name in PROVIDERS_CONTOLLERS:
            raise Exception(
                f'No se encontro el controlador del proveedor {provider_name}')

        # Obtener el driver del proveedor
        self.controller = PROVIDERS_CONTOLLERS[provider_name](self.driver)

    def runAllControllers(self):
        self.checkConfiguration(controller=False)

        for provider_name in PROVIDERS_CONTOLLERS:
            self.setupController(provider_name)
            self.open()
            self.login()
            self.search()

    def open(self):
        self.checkConfiguration()

        # Ir a la pagina
        self.controller.open()

    def login(self):
        self.checkConfiguration()

        # Iniciar sesion
        self.controller.login()

    def search(self):
        self.checkConfiguration()

        # Buscar productos en el proveedor
        self.controller.searchProducts()

        # Buscar los productos
        return

    def searchByCategoryInAllProviders(self, category):
        self.checkConfiguration(controller=False)

        for provider_name in PROVIDERS_CONTOLLERS:
            self.setupController(provider_name)
            self.open()
            try:
                self.login()
            except:
                pass
            self.controller.searchByCategory(category)
            self.quit()

    def checkConfiguration(self, driver=True, controller=True):
        if not self.driver and driver:
            raise Exception('El driver no esta configurado')
        if not self.controller and controller:
            raise Exception('El controlador no esta configurado')

    def close(self):
        self.driver.close()

    def closeAll(self):
        handles = self.driver.window_handles
        for handle in handles:
            self.driver.switch_to.window(handle)
            self.driver.close()

    def quit(self):
        self.driver.quit()

    def thereAreOutdated(self):
        return self.controller.thereAreOutdated()

    def save(self, category=None):
        self.controller.saveToExcel(category)
