import logging
import sys

LOG_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Отключаем лишний спам от SQLAlchemy в консоли
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str):
    return logging.getLogger(name)
