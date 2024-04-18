import logging

logging.basicConfig(level=logging.DEBUG)
# 涉及的三方包日志等级统一设置为ERROR
for pkg in ['selenium', 'urllib3', 'httpx']:
    logger_pkg = logging.getLogger(pkg)
    logger_pkg.setLevel(logging.ERROR)


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger