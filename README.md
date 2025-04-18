# NetUser404-api

NetUser404 es una API construida con FastAPI que permite almacenar y consultar métricas de conectividad a internet recolectadas desde estaciones cliente. Este módulo forma parte del sistema completo de monitoreo del estado de internet.

## Características principales

* Recepción de métricas individuales o por lote.
* Consultas por BSSID, MAC, fecha, latencia, carga y velocidad de descarga.
* Agrupación de códigos de estado HTTP por red.
* Servicio autoejecutable vía systemd.
* Instalación automática mediante script install_api.

## Requisitos

* Solo disponible para Linux
* Python 3.10 o superior
* Git
* MongoDB Community Edition -> [Guía de instalación](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)

## Instalación

En la terminal, ejecutar el siguiente comando:
```
wget https://raw.githubusercontent.com/franyober/NetUser404-api/refs/heads/main/install_api
```

Luego dar permisos de ejecución al archivo de instalación:
```
chmod +x install_api
```

Luego ejecutar el archivo:
```
sudo ./install_api
```

