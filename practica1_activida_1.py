import cv2
import numpy as np
import matplotlib.pyplot as plt

# Mostrar las versiones de las librerías
print('versión OpenCV: ', cv2.__version__)
print('versión NumPy: ', np.__version__)

# Cargar las imágenes en escala de grises
placa = cv2.imread('images/placa.jpg', cv2.IMREAD_GRAYSCALE)
circuito = cv2.imread('images/circuito.jpg', cv2.IMREAD_GRAYSCALE)

# Realizar template matching
resultado = cv2.matchTemplate(placa, circuito, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultado)
print("\nResultados del Template Matching:")
print(f"Valor mínimo: {min_val}, Posición: {min_loc}")
print(f"Valor máximo: {max_val}, Posición: {max_loc}")

# Obtener dimensiones del circuito
alto, ancho = np.shape(circuito)
print("\nDimensiones del circuito:")
print(f"Alto: {alto} píxeles")
print(f"Ancho: {ancho} píxeles")

# Se identifican los pixeles superior izquierda e inferior derecha
pixel_sup_izq = max_loc
pixel_inf_der = (max_loc[0] + ancho, max_loc[1] + alto)
print("\nPuntos de la región encontrada:")
print(f"Esquina superior izquierda: {pixel_sup_izq}")
print(f"Esquina inferior derecha: {pixel_inf_der}")

# Se genera el rectángulo de color que identificará el circuito en la placa
placa_color = cv2.imread('images/placa.jpg')  # Cargar imagen en color
color = (0, 255, 255)  # Color BGR (amarillo)
cv2.rectangle(placa_color, pixel_sup_izq, pixel_inf_der, color, 4)

# Se muestran las imágenes
cv2.imshow('Placa', placa)
cv2.imshow('Practica1', placa_color)
cv2.waitKey(0)
cv2.destroyAllWindows()
