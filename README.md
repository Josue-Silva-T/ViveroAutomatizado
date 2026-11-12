# 🍄 Vivero Automatizado para Setas Ostra

Sistema basado en dos ESP32 (MicroPython) para monitorear y automatizar un vivero de setas ostra. Una placa lee **temperatura, humedad, iluminación y nivel de agua**, y la otra, una **ESP32-CAM**, recibe esos datos, los muestra en una **pantalla OLED**, toma **una foto cada hora** y ofrece un **servidor web con la cámara en vivo**.

<img width="400" alt="20260115_153403" src="https://github.com/user-attachments/assets/f173631f-e63c-48eb-a885-731842e76715" />


## Cómo funciona

```
┌─────────────────────────┐    WiFi · TCP :5000      ┌──────────────────────────┐
│  ESP32 (sensores)       │ ───────────────────────► │  ESP32-CAM               │
│  mainesp32.py           │  "hum,temp,luz,agua"     │  main.py + camara.py     │
│                         │  cada 2 s                │                          │
│  • DHT11 (temp/humedad) │                          │  • Pantalla OLED         │
│  • Sensor nivel de agua │                          │  • Foto cada hora (/img) │
│  • LDR (luz)            │                          │  • Servidor web :80      │
│  • Luz de cultivo (PWM) │                          │  • Hora por NTP          │
└─────────────────────────┘                          └──────────────────────────┘
```

## Archivos del repositorio

| Ruta | Descripción |
|---|---|
| `main.py` | Programa de la **ESP32-CAM**: cámara, OLED, fecha/hora, fotos y recepción de datos. |
| `camara.py` | Servidor web de la cámara (puerto 80). |
| `mainesp32.py` | Programa de la **ESP32 de sensores**: lee sensores, controla la luz y envía los datos. |
| `pcb/` | Diseño de las 2 placas (el PDF muestra mejor ambas). |
| `mdf/` | Archivos de corte láser en MDF. |

> Cada placa necesita que su programa se llame `main.py` al cargarlo. Por eso `mainesp32.py` debe renombrarse al subirlo a la ESP32 de sensores.

## Hardware

| Componente | Placa | Uso |
|---|---|---|
| ESP32 | Sensores | Lectura de sensores y control de la luz |
| ESP32-CAM | Cámara | Fotos, servidor web y pantalla |
| DHT11 | Sensores | Temperatura y humedad |
| Sensor de nivel de agua (digital) | Sensores | Detecta si hay agua en el depósito |
| LDR | Sensores | Medición de luz ambiental |
| Luz de cultivo + etapa de potencia | Sensores | Iluminación regulada por PWM |
| Pantalla OLED SSD1306 128x64 (I2C) | Cámara | Muestra el estado del vivero |

### Conexiones

**ESP32 de sensores**

| GPIO | Conectado a |
|---|---|
| 14 | DHT11 (datos) |
| 27 | Sensor de nivel de agua (entrada digital) |
| 34 | LDR (entrada analógica, 12 bits, atenuación 11 dB) |
| 5 | Luz de cultivo (salida PWM a 5 kHz) |


**ESP32-CAM**

| GPIO | Conectado a |
|---|---|
| 14 | OLED SDA |
| 15 | OLED SCL |





## Protocolo de comunicación

La ESP32 de sensores abre una conexión TCP a la ESP32-CAM (puerto **5000**) cada 2 segundos y envía una línea de texto separada por comas:

```
humedad,temperatura,iluminacion,agua
```

Ejemplo: `85,22,OPTIMA,True`

| Campo | Valores |
|---|---|
| `humedad` | % de humedad relativa (DHT11) |
| `temperatura` | °C (DHT11) |
| `iluminacion` | `OSCURA`, `OPTIMA` o `EXCESIVA` |
| `agua` | `True` si hay agua, `False` si no |

### Niveles de iluminación

| Lectura ADC del LDR | Estado |
|---|---|
| > 1600 | `OSCURA` |
| 901 – 1600 | `OPTIMA` |
| ≤ 900 | `EXCESIVA` |

<img width="400" alt="20260106_163054" src="https://github.com/user-attachments/assets/289df07c-5477-487e-aae1-62ca818fdcdf" />

## Funciones de la ESP32-CAM

- **Cámara web:** servidor en el puerto 80, resolución 800x600, contraste 2 y efecto de escala de grises. Sin contraseña por defecto.
- **Fotos automáticas:** guarda una foto en `/img/` cada vez que cambia la hora, con el nombre `DD-MM-AAAA-HH-MM.jpg`.
- **Fecha y hora:** se sincronizan por NTP.
- **Pantalla OLED:** muestra fecha, temperatura, humedad, brillo y el aviso `NO HAY AGUA`.
- **Arranque:** si la cámara no responde tras 5 intentos o el WiFi no conecta, la placa se reinicia.

  <img width="400" alt="16-01-2026-02-00" src="https://github.com/user-attachments/assets/31141d03-87f4-49b6-8713-9e0babbedb3e" />

## Requisitos

- 2 placas ESP32 (una con cámara) con **MicroPython**. La ESP32-CAM necesita un firmware con el módulo `camera`.
- Módulos: `ssd1306`, `ntptime` (incluido), `dht` (incluido).
- Módulos para importar `main.py`: `wifi`, `help` y `site`.
- Herramienta para cargar archivos, como [Thonny](https://thonny.org/) o `mpremote`.

