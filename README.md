# NetUser404-api

NetUser404 es una API construida con FastAPI que permite almacenar y consultar métricas de conectividad a internet recolectadas desde estaciones cliente. Este módulo forma parte del sistema completo de monitoreo del estado de internet. El repositorio general de este proyecto se encuentra en [NetUser404-docs](https://github.com/franyober/netUser404-docs/).

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
sudo chmod +x install_api
```

Luego ejecutar el archivo:
```
sudo ./install_api
```

### Desinstalación

Para desinstalar, se recomienda descargar el siguiente script de desinstalación:

```
wget https://raw.githubusercontent.com/franyober/NetUser404-api/refs/heads/main/uninstall_api
```

Los pasos para ejecutar el script de desinstalación son los mismos que se usó para el de instalación.


## Endpoints

Esta API expone los siguientes endpoints RESTful para la recepción, almacenamiento y consulta de métricas de conectividad.

| Método | Endpoint | Descripción |
|:------:|:---------|:------------|
| `GET` | `/macs_by_bssid` | Obtiene todas las direcciones MAC asociadas a un BSSID específico. |
| `GET` | `/bssids_by_mac` | Obtiene todos los BSSID a los que se ha conectado una dirección MAC específica. |
| `GET` | `/networks` | Devuelve la lista de redes (BSSID) registradas en la base de datos. |
| `GET` | `/MAC_list` | Devuelve la lista de direcciones MAC registradas. |
| `GET` | `/pages` | Obtiene la lista de páginas web accedidas. |
| `GET` | `/metrics/status_code` | Devuelve el conteo de códigos de respuesta HTTP agrupados por red. |
| `GET` | `/metrics/load` | Obtiene los tiempos de carga promedio de las páginas web. |
| `GET` | `/metrics/latency` | Obtiene la latencia promedio de conectividad (ping) por red. |
| `GET` | `/metrics/download` | Obtiene la velocidad promedio de descarga medida. |
| `POST` | `/metric` | Inserta una métrica individual en la base de datos. |
| `POST` | `/metrics` | Inserta múltiples métricas en lote en la base de datos. |
| `GET` | `/check-mongodb` | Verifica la conectividad entre la API y la base de datos MongoDB. |

---

- **Recepción de métricas:**  
  Los clientes (sensores de red) usando [NetUser404](https://github.com/mateoprotocol/NetUser404) envían las métricas recolectadas utilizando los endpoints `POST /metric` (una sola métrica) o `POST /metrics` (varias métricas).

- **Consulta de datos:**  
  El dashboard [NetUser404-visual](https://github.com/franyober/NetUser404-visual) consulta métricas específicas filtradas por MAC, BSSID o URL mediante los endpoints `GET`.

- **Monitoreo interno:**  
  El endpoint `GET /check-mongodb` permite validar si la API tiene conexión activa con la base de datos MongoDB.





