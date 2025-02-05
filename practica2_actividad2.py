# Importamos paquetes y librerías necesarios
from collections import deque
import numpy as np
import argparse
import cv2
import time

# Se construye el argumento que se va a analizar y se analizan los argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="activar la ruta de ubicación del video")
ap.add_argument("-b", "--buffer", type=int, default=16, help="Tamaño máximo del buffer")
args = vars(ap.parse_args())

# Define el rango de color azul en el espacio HSV
blueLower = (100, 60, 60)  # HSV valores para azul
blueUpper = (130, 255, 255)  # HSV valores para azul

# Inicializar la lista de los puntos rastreados
pts = deque(maxlen=args["buffer"])

# Si no se proporciona ruta del video, busca la cámara web
if not args.get("video", False):
    vs = cv2.VideoCapture(0)
    time.sleep(2.0)  # Permitir que la cámara se inicialice
# En otro caso, toma como referencia el archivo de video
else:
    vs = cv2.VideoCapture(args["video"])

# Permite el archivo de video o la cámara sea presentado
time.sleep(2.0)

# Continua el ciclo
while True:
    # Toma el cuadro actual
    ret, frame = vs.read()
    
    # Manejar el marco VideoCapture o VideoStream
    frame = frame if not args.get("video", False) else frame
    
    # Si estamos viendo un video y no tomamos un cuadro,
    # entonces hemos llegado al final del video
    if frame is None:
        break
        
    # Cambiar el tamaño del marco, desenfocar y convertir al espacio de color HSV
    frame = cv2.resize(frame, (600, int(frame.shape[0] * 600 / frame.shape[1])))
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Construir una máscara para el color "azul", luego se realizan
    # una serie de dilataciones y erosiones para eliminar cualquier pequeña
    # mancha en la máscara
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    
    # Realizar operaciones morfológicas para eliminar pequeños ruidos
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Encontrar contornos en la máscara e inicializar el centro actual
    # de la imagen (x,y)
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    
    # Proceder solo si se ha encontrado al menos un contorno
    if len(contours) > 0:
        # Encontrar el contorno más grande en la máscara, luego calcular el
        # círculo envolvente mínimo y centroide
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        # Proceder solo si el radio cumple con un tamaño mínimo
        if radius > 10:
            # Dibujar el círculo y el centroide en el marco
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)  # Azul para el círculo
            cv2.circle(frame, center, 5, (0, 0, 255), -1)  # Rojo para el centro
            
            # Actualizar la cola de puntos
            pts.appendleft(center)
            
    # Bucle sobre el conjunto de puntos rastreados
    for i in range(1, len(pts)):
        # Si no es ninguno de los puntos rastreados ignorarlos
        if pts[i - 1] is None or pts[i] is None:
            continue
            
        # Dibujar la línea entre los puntos
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), 2)
        
    # Mostrar el marco a la pantalla
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # Detener el ciclo si se presiona la tecla q
    if key == ord("q"):
        break

# Si no se utiliza un archivo de video, detener la transmisión de video de la cámara
if not args.get("video", False):
    vs.stop()
# En otro caso liberar la cámara
else:
    vs.release()

# Cerrar todas las ventanas
cv2.destroyAllWindows()