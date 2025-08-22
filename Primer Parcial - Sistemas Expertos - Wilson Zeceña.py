import pygame, sys, random, json, os

# ----- Configuración -----
pygame.init()
ANCHO, ALTO = 600, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tres en Raya Explosivo")
FUENTE = pygame.font.SysFont("Arial", 80)
MSG_FUENTE = pygame.font.SysFont("Arial", 50)
BLANCO, NEGRO, ROJO, AZUL, GRIS = (255,255,255),(0,0,0),(220,0,0),(0,0,220),(240,240,240)
DB_FILE = os.path.join(os.path.dirname(__file__), "conocimiento.json")  # ruta segura
WIN_COMBOS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

# ----- Base de conocimiento -----
def cargar(): 
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)  # JSON legible
        f.flush()
        os.fsync(f.fileno())  # asegura escritura inmediata

# ----- Lógica -----
def ganador(tablero, jugador): 
    return any(all(tablero[i]==jugador for i in combo) for combo in WIN_COMBOS)

def tablero_lleno(tablero): 
    return all(c!=" " for c in tablero)

def movimientos(tablero): 
    return [i for i,c in enumerate(tablero) if c==" "]

def clave(tablero, turno): 
    return "".join(tablero)+"|"+turno

def heuristica(tablero, maquina, usuario):
    for pos in movimientos(tablero):
        tmp = tablero[:]; tmp[pos]=maquina
        if ganador(tmp, maquina): return pos
    for pos in movimientos(tablero):
        tmp = tablero[:]; tmp[pos]=usuario
        if ganador(tmp, usuario): return pos
    if tablero[4]==" ": return 4
    for pos in [0,2,6,8]: 
        if tablero[pos]==" ": return pos
    for pos in [1,3,5,7]: 
        if tablero[pos]==" ": return pos
    return random.choice(movimientos(tablero))

def jugada_maquina(tablero, conocimiento, maquina, usuario):
    k = clave(tablero, maquina)
    if k in conocimiento and conocimiento[k] in movimientos(tablero):
        return conocimiento[k], conocimiento
    pos = heuristica(tablero, maquina, usuario)
    conocimiento[k] = pos
    return pos, conocimiento

# ----- Dibujar tablero -----
def dibujar(tablero, resaltar=[]):
    color_fondo = (200, 220, 255)
    VENTANA.fill(color_fondo)
    for i in range(1,3):
        pygame.draw.line(VENTANA, NEGRO, (0,i*200),(ANCHO,i*200),8)
        pygame.draw.line(VENTANA, NEGRO, (i*200,0),(i*200,ALTO),8)
    for i,c in enumerate(tablero):
        x,y = (i%3)*200+100, (i//3)*200+100
        if c=="X": pygame.draw.line(VENTANA, ROJO, (x-60,y-60),(x+60,y+60),15); pygame.draw.line(VENTANA, ROJO, (x+60,y-60),(x-60,y+60),15)
        if c=="O": pygame.draw.circle(VENTANA, AZUL, (x,y), 70, 15)
    if resaltar:
        for idx in resaltar:
            x,y = (idx%3)*200+100, (idx//3)*200+100
            for _ in range(5):
                pygame.draw.rect(VENTANA, (0,255,0), (x-90, y-90, 180, 180), 6)
                pygame.display.flip()
    pygame.display.flip()

# ----- Animación fichas -----
def animar_ficha(pos, tipo):
    x,y = (pos%3)*200+100, (pos//3)*200+100
    for r in range(0, 71, 10):
        dibujar(tablero)
        if tipo=="X":
            pygame.draw.line(VENTANA, ROJO, (x-r,y-r),(x+r,y+r),15)
            pygame.draw.line(VENTANA, ROJO, (x+r,y-r),(x-r,y+r),15)
        else:
            pygame.draw.circle(VENTANA, AZUL, (x,y), r, 15)
        pygame.display.flip()
        pygame.time.delay(40)

# ----- Partículas de victoria -----
def efecto_victoria(resaltar):
    particulas = []
    for idx in resaltar:
        x,y = (idx%3)*200+100, (idx//3)*200+100
        for _ in range(20):
            dx,dy = random.randint(-50,50), random.randint(-50,50)
            color = random.choice([ROJO,AZUL,(255,255,0),(0,255,0)])
            particulas.append([x,y,dx,dy,color, random.randint(3,6)])
    for _ in range(30):
        dibujar(tablero, resaltar)
        for p in particulas:
            x0,y0,dx,dy,color,r = p
            pygame.draw.circle(VENTANA,color,(x0+dx,y0+dy),r)
        pygame.display.flip()
        pygame.time.delay(50)

# ----- Mensajes -----
def mostrar_mensaje(texto):
    VENTANA.fill(GRIS)
    msg = MSG_FUENTE.render(texto, True, NEGRO)
    VENTANA.blit(msg, msg.get_rect(center=(ANCHO//2, ALTO//2)))
    pygame.display.flip()
    pygame.time.delay(1500)

def pantalla_inicio():
    VENTANA.fill(GRIS)
    msg1 = MSG_FUENTE.render("TRES EN RAYA", True, ROJO)
    msg2 = MSG_FUENTE.render("Presiona para jugar", True, AZUL)
    VENTANA.blit(msg1, msg1.get_rect(center=(ANCHO//2, ALTO//2-40)))
    VENTANA.blit(msg2, msg2.get_rect(center=(ANCHO//2, ALTO//2+40)))
    pygame.display.flip()
    esperando=True
    while esperando:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN: esperando=False

# ----- Juego principal -----
def main():
    pantalla_inicio()
    global tablero
    tablero, conocimiento = [" "]*9, cargar()
    turno = random.choice(["usuario","maquina"])
    usuario, maquina = ("O","X") if turno=="maquina" else ("X","O")
    jugando = True
    ganador_actual = None

    while jugando:
        dibujar(tablero, resaltar=ganador_actual if ganador_actual else [])
        for e in pygame.event.get():
            if e.type==pygame.QUIT: guardar(conocimiento); pygame.quit(); sys.exit()
            if turno=="usuario" and e.type==pygame.MOUSEBUTTONDOWN:
                x,y = e.pos; pos = y//200*3 + x//200
                if tablero[pos]==" ":
                    tablero[pos]=usuario
                    animar_ficha(pos, usuario)
                    if ganador(tablero, usuario):
                        ganador_actual = [i for i in WIN_COMBOS if all(tablero[j]==usuario for j in i)][0]
                        efecto_victoria(ganador_actual)
                        mostrar_mensaje("Has ganado")
                        jugando=False
                    elif tablero_lleno(tablero):
                        mostrar_mensaje("Empate")
                        jugando=False
                    else: turno="maquina"

        if turno=="maquina" and jugando:
            pygame.time.delay(500)
            pos, conocimiento = jugada_maquina(tablero, conocimiento, maquina, usuario)
            tablero[pos] = maquina
            guardar(conocimiento)  # guardado inmediato
            animar_ficha(pos, maquina)
            if ganador(tablero, maquina):
                ganador_actual = [i for i in WIN_COMBOS if all(tablero[j]==maquina for j in i)][0]
                efecto_victoria(ganador_actual)
                mostrar_mensaje("La máquina ganó")
                jugando=False
            elif tablero_lleno(tablero):
                mostrar_mensaje("Empate")
                jugando=False
            else: turno="usuario"

    guardar(conocimiento)
    dibujar(tablero, resaltar=ganador_actual if ganador_actual else [])
    mostrar_mensaje("¿Jugar de nuevo? (Y/N)")
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_y: main()
                if e.key==pygame.K_n: pygame.quit(); sys.exit()

if __name__=="__main__": main()
