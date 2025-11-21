import logging
from pathlib import Path

class Logger:
    """
    Sistema de logging para operações e erros do SRHP.
    
    Níveis de Log:
    - INFO: operações normais
    - WARNING: situações incomuns mas não críticas
    - ERROR: erros recuperáveis
    - CRITICAL: erros que impedem funcionamento
    """

    def __init__(self, nome_modulo: str, arquivo_log: str = "srhp.log"):
        # Cria o objeto Logger
        self.logger = logging.getLogger(nome_modulo)
        self.logger.setLevel(logging.DEBUG)  # <-- CORRETO: setLevel do objeto Logger

        # Evita duplicação de handlers
        if not self.logger.handlers:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Handler para arquivo
            file_handler = logging.FileHandler(log_dir / arquivo_log, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Formato das mensagens
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, mensagem: str):
        self.logger.info(mensagem)

    def warning(self, mensagem: str):
        self.logger.warning(mensagem)

    def error(self, mensagem: str, exc_info=False):
        self.logger.error(mensagem, exc_info=exc_info)

    def critical(self, mensagem: str, exc_info=False):
        self.logger.critical(mensagem, exc_info=exc_info)

    def debug(self, mensagem: str):
        self.logger.debug(mensagem)
     

