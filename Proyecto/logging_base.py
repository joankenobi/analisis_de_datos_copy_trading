import logging as loge

"""
    Al importar desde otro archivo este log usando 'from logging_base import log' 
    permitida trabajar con logging utilizaldo la configuración basica dada por este archivo.
"""

loge.basicConfig(level=loge.INFO, #nivel de trabajo
    format="%(asctime)s:, %(levelname)s, [%(filename)s:%(lineno)s], %(message)s", #info soble el mensaje.
    datefmt="%D %I:%M:%S %P", #d-m-y h:m:s pm
    handlers=[
        loge.FileHandler("capa_datos.loge"), #info en doc.loge
        loge.StreamHandler() #info en consola
    ]
)

#myLog=loge.getLogger("my_loger")

#myLog.addHandler(loge.FileHandler("capa_datos.loge"),loge.StreamHandler)

#myLog

if __name__ == "__main__":
    loge.debug("Mensaje a nivel debug")
    loge.info("Mensaje a nivel info")
    loge.warning("Mensaje a nivel warning")
    loge.error("Mensaje a nivel error")
    loge.critical("Mensaje a nivel critical")