# Importamos paquetes y librerías necesarios
from collections import deque
import numpy as np
import argparse
import cv2
import time

# Se construye el argumento que se va a analizar y se analizan los argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=16, help="Tamaño máximo del buffer")
args = vars(ap.parse_args())

# Define el rango de color verde en el espacio HSV
greenLower = (29, 86, 6)  #BGR
greenUpper = (64, 255, 100)  #BGR

# Inicializar la lista de los puntos rastreados
pts = deque(maxlen=args["buffer"])

# Ruta estática del video
video_path = "video/seguimiento.mp4"
vs = cv2.VideoCapture(video_path)

# Permite el archivo de video o la cámara sea presentado
time.sleep(2.0)

# Continua el ciclo
while True:
    # Toma el cuadro actual
    ret, frame = vs.read()
    
    # Si estamos viendo un video y no tomamos un cuadro,
    # entonces hemos llegado al final del video
    if frame is None:
        break
        
    # Cambiar el tamaño del marco, desenfocar y convertir al espacio de color HSV
    frame = cv2.resize(frame, (600, int(frame.shape[0] * 600 / frame.shape[1])))
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Construir una máscara para el color "verde", luego se realizan
    # una serie de dilataciones y erosiones para eliminar cualquier pequeña
    # mancha en la máscara
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    
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
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
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

# Liberar la cámara y cerrar todas las ventanas
vs.release()
cv2.destroyAllWindows()