import socket
import network
import time
import dht
import machine

monitor = dht.DHT11(machine.Pin(14))
nivelDelAgua = machine.Pin(27, machine.Pin.IN)
brillo = machine.ADC(machine.Pin(34))
brillo.atten(machine.ADC.ATTN_11DB)      
brillo.width(machine.ADC.WIDTH_12BIT) 
luz = machine.Pin(5)
luzpwm = machine.PWM(luz, freq=5000, duty=0)
valor = 0

ssid = "Totalplay-41AD"
password = "41AD4791eHEmTk9H"

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

CAM_IP = "192.168.100.66"  # IP de la ESP32-CAM

def modIluminacion():
    lbrillo = brillo.read()
    print("Valor LDR (ADC):", valor)
    if lbrillo > 1600:
        return "OSCURA"
        if tono < 1024:
            luzpwm.duty(tono)
            tono +=5
    elif lbrillo > 900:
        return  "OPTIMA"
        tono = 0
    else:
        return "EXCESIVA"
        if tono > 0:
            luzpwm.duty(tono)
            tono -=5
            
    

print("listo")
while True:
    try:
        monitor.measure()
        humedad = monitor.humidity()
        temperatura = monitor.temperature()
        iluminacion = modIluminacion()
        if nivelDelAgua.value() == 1: agua = False
        else: agua = True 
        #humedad, temperatura, luminosidad, nivel del agua
        msg = f"{humedad},{temperatura},{iluminacion},{agua}"
        print(msg)
        s = socket.socket()
        s.connect((CAM_IP, 5000))
        s.send(msg)
        s.close()
        time.sleep(2)
    except OSError as e:
        print("Fallo al leer el sensor:", e)
    
    
    
    
    
