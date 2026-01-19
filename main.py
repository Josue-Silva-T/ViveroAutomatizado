#para el uso del esp32 cam
from machine import reset, Pin, I2C

#Utilizar fecha y hora
from time import sleep, localtime
import ntptime

#Para obtener las fotos tomadas
import requests

#para poder hacer hilos
import threading

#utilizar la pantalla oled
import ssd1306

#Utilizar camara
import camera

#Conexion wifi
from wifi import Sta

#Para la configuracion de la camara
from help import Setting as cam_setting
from camara import server
import site

auth=site.auth
pwd=site.pwd


i2c = I2C(0, scl=Pin(15), sda=Pin(14), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)


oled.fill(0)
oled.text("Iniciando...", 0, 0)
oled.show()


#Obtener fecha y hora
def Fecha():
    try:
        ntptime.settime()
    except:
        print("Error al sincronizar")
        current_time = localtime()
        formatted_time = "{:02d}_{:02d}_{} {:02d}.{:02d}".format(
            current_time[2], current_time[1], current_time[0],
            current_time[3], current_time[4], current_time[5]
        )
        print("hora lista ", formatted_time)
     




#intentar acceder a la camara
def camara():
    for i in range(5):
        cam = camera.init()
        print("Camara activa?: ", cam)
        if cam: break
        else: sleep(2)
    else:
        print('Tiempo agotado')
        reset() 

    if cam:
       print("Camara Lista")
       #Intentar acceder a la conexion wifi
       w = Sta()
       w.connect()
       w.wait()
       for i in range(5):
           if w.wlan.isconnected(): break
           else: print("WIFI no esta listo. Espera...");sleep(2)
       else:
          print("No se pudo conectar al WIFI")
          reset()

    # True: Se necesita contraseña
    # False: no se necesita contraseña
    auth.on=False   

    # Solo se necesita si auth.on=True
    #
    #if auth.on:
    #   auth.pwd=pwd()
    #   auth.ip=''
    #   print(f'PWD: {auth.pwd}')

    # Configuracion de preferencias de camara
    camera.framesize(10)     # tamaño del capturador 800X600
    camera.contrast(2)       # Contraste
    camera.speffect(2)       # jpeg en escala de grises

    cam_setting['framesize']=10
    cam_setting['contrast']=2
    cam_setting['speffect']=2

    site.ip=w.wlan.ifconfig()[0]
    site.camera=camera

    server((80,))  # puerto 80


    reset()
    
def toma():
    horaAnterior = 0.1
    while True:
        current_time = localtime()
        hora = "{:02d}-{:02d}-{}-{:02d}-{:02d}".format(
            current_time[2], current_time[1], current_time[0],
            current_time[3], current_time[4]
        )
        
        if(horaAnterior != current_time[3] and horaAnterior != 0.1):
            print(hora)
            print("foto tomada")
            buf = camera.capture()
            with open(f"/img/{hora}.jpg", "wb") as f:
                f.write(buf)
        horaAnterior = current_time[3]


#Actualizar Estado en pantalla oled
def Estado():
    print("recibiendo")
    oled.fill(0)
    oled.text("recibiendo...", 0, 0)
    oled.show()

    while True:
        #Sta.datos()
        sensor = Sta.datos().split(",")
        
        current_time = localtime()
        hora = "{:02d}_{:02d}_{} {:02d}.{:02d}".format(
            current_time[2], current_time[1], current_time[0],
            current_time[3], current_time[4]
        )
        
        print(f"Temp: {sensor[0]}, Humedad: {sensor[1]}, Luminosidad: {sensor[2]}, agua: {sensor[3]}, Fecha: {hora}")
        
        oled.fill(0)
        oled.text(f"{hora}", 0, 0)
        oled.text(f"Temperatura: {sensor[1]}C", 0, 10)
        oled.text(f"Humedad: {sensor[0]}%", 0, 20)
        oled.text(f"Brillo: {sensor[2]}", 0, 30)
        #NUEVO
        if(not sensor[2]):
            oled.text("NO HAY AGUA", 0, 40)
        #hasta aqui
        oled.show()



foto = threading.Thread(target=toma)
ActCam = threading.Thread(target=camara)
actualizar = threading.Thread(target=Estado)

oled.fill(0)
oled.text("Comenzando...", 0, 0)
oled.show()

ActCam.start()
sleep(20)

oled.fill(0)
oled.text("Camara activa", 0, 0)
oled.show()

Fecha()

oled.fill(0)
oled.text("fecha activa", 0, 0)
oled.show()

actualizar.start()
foto.start()
print("todo listo")

