import tkinter as tk 
from tkinter import messagebox 
import heapq
#tkinter: Biblioteca estándar de Python para crear interfaces gráficas de usuario (GUI).
#messagebox: Submódulo de tkinter para mostrar cuadros de diálogo.
#heapq: Implementación de cola de prioridad en Python, crucial para la eficiencia del algoritmo A*
class Nodo:
    def __init__(self, posicion, costo_g, costo_h, padre):
        self.posicion = posicion  # Posición del nodo en el mapa
        self.costo_g = costo_g    # Costo real desde el inicio hasta este nodo
        self.costo_h = costo_h    # Costo heurístico estimado desde este nodo hasta el objetivo
        self.costo_f = costo_g + costo_h  # Costo total estimado (costo_g + costo_h)
        self.padre = padre        # Nodo padre en el camino

    def __lt__(self, otro): #Método de comparación "menor que", necesario para el funcionamiento correcto de heapq.
        return self.costo_f < otro.costo_f  # Comparación para la cola de prioridad

def heuristica(a, b):
    # Calcula la distancia Manhattan entre dos puntos
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def obtener_vecinos(mapa, nodo):
    vecinos = []
    # Verifica los vecinos en las cuatro direcciones (arriba, derecha, abajo, izquierda)
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nueva_posicion = (nodo.posicion[0] + dx, nodo.posicion[1] + dy)
        # Verifica si la nueva posición está dentro del mapa
        if 0 <= nueva_posicion[0] < len(mapa) and 0 <= nueva_posicion[1] < len(mapa[0]):
            terreno = mapa[nueva_posicion[0]][nueva_posicion[1]]
            if terreno == 0:  # Camino libre
                costo = 1
            elif terreno == 2:  # Agua
                costo = 3
            elif terreno == 3:  # Área bloqueada temporalmente
                costo = 5
            else:  # Obstáculo
                continue
            vecinos.append((nueva_posicion, costo))
    return vecinos

def a_estrella(mapa, inicio, objetivo):
    nodo_inicial = Nodo(inicio, 0, heuristica(inicio, objetivo), None)
    lista_abierta = [nodo_inicial]
    conjunto_cerrado = set()

    while lista_abierta:
        nodo_actual = heapq.heappop(lista_abierta)  # Obtiene el nodo con menor costo_f

        if nodo_actual.posicion == objetivo:
            # Reconstruye el camino si se ha llegado al objetivo
            camino = []
            while nodo_actual:
                camino.append(nodo_actual.posicion)
                nodo_actual = nodo_actual.padre
            return camino[::-1]  # Invierte el camino para que vaya desde el inicio al final

        conjunto_cerrado.add(nodo_actual.posicion)

        for posicion_vecino, costo_vecino in obtener_vecinos(mapa, nodo_actual):
            if posicion_vecino in conjunto_cerrado:
                continue

            vecino = Nodo(posicion_vecino,
                          nodo_actual.costo_g + costo_vecino,
                          heuristica(posicion_vecino, objetivo),
                          nodo_actual)

            if vecino not in lista_abierta:
                heapq.heappush(lista_abierta, vecino)
            else:
                idx = lista_abierta.index(vecino)
                if lista_abierta[idx].costo_g > vecino.costo_g:
                    lista_abierta[idx] = vecino
                    heapq.heapify(lista_abierta)

    return None  # No se encontró un camino

class InterfazBuscadorRutas:
    def __init__(self, maestro):
        self.maestro = maestro
        self.maestro.title("Calculadora de Rutas")
        self.mapa = [[0 for _ in range(20)] for _ in range(20)]  # Inicializa el mapa
        self.inicio = None
        self.objetivo = None
        self.tamano_celda = 30

        # Crea el lienzo para dibujar el mapa
        self.lienzo = tk.Canvas(self.maestro, width=600, height=600)
        self.lienzo.pack()

        self.dibujar_cuadricula()

        # Vincula el evento de clic del ratón
        self.lienzo.bind("<Button-1>", self.al_hacer_clic)
        
        # Crea botones para limpiar el mapa y encontrar la ruta
        self.boton_limpiar = tk.Button(self.maestro, text="Limpiar", command=self.limpiar_mapa)
        self.boton_limpiar.pack()
        
        self.boton_encontrar_ruta = tk.Button(self.maestro, text="Encontrar Ruta", command=self.encontrar_ruta)
        self.boton_encontrar_ruta.pack()

    def dibujar_cuadricula(self):
        # Dibuja la cuadrícula del mapa
        for i in range(20):
            for j in range(20):
                x1 = j * self.tamano_celda
                y1 = i * self.tamano_celda
                x2 = x1 + self.tamano_celda
                y2 = y1 + self.tamano_celda
                self.lienzo.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

    def al_hacer_clic(self, evento):
        # Maneja los clics del usuario para establecer inicio, fin y obstáculos
        columna = evento.x // self.tamano_celda
        fila = evento.y // self.tamano_celda
        
        if not self.inicio:
            self.inicio = (fila, columna)
            self.colorear_celda(fila, columna, "green")
        elif not self.objetivo:
            self.objetivo = (fila, columna)
            self.colorear_celda(fila, columna, "red")
        else:
            if self.mapa[fila][columna] == 0:
                self.mapa[fila][columna] = 1
                self.colorear_celda(fila, columna, "black")
            else:
                self.mapa[fila][columna] = 0
                self.colorear_celda(fila, columna, "white")

    def colorear_celda(self, fila, columna, color):
        # Colorea una celda en el mapa
        x1 = columna * self.tamano_celda
        y1 = fila * self.tamano_celda
        x2 = x1 + self.tamano_celda
        y2 = y1 + self.tamano_celda
        self.lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def limpiar_mapa(self):
        # Limpia el mapa y restablece el inicio y el fin
        self.mapa = [[0 for _ in range(20)] for _ in range(20)]
        self.inicio = None
        self.objetivo = None
        self.dibujar_cuadricula()

    def encontrar_ruta(self):
        # Encuentra y muestra la ruta utilizando el algoritmo A*
        if not self.inicio or not self.objetivo:
            messagebox.showerror("Error", "Por favor, seleccione un punto de inicio y un punto final.")
            return

        camino = a_estrella(self.mapa, self.inicio, self.objetivo)
        if camino:
            for fila, columna in camino[1:-1]:  # Excluimos el inicio y el final
                self.colorear_celda(fila, columna, "yellow")
        else:
            messagebox.showinfo("Resultado", "No se encontró un camino.")

def main():
    raiz = tk.Tk()
    app = InterfazBuscadorRutas(raiz)
    raiz.mainloop()

if __name__ == "__main__":
    main()