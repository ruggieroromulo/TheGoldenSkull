import pgzrun
from pgzero.actor import Actor
 
# --- CONFIGURAÇÕES (CONSTANTES) ---
WIDTH = 1200
HEIGHT = 800
TITLE = "The Golden Skull"

# Configurações de Física
GRAVITY = 0.7
JUMP_POWER = -14
HOLD_JUMP_POWER = -20
SPEED = 5

# --- CLASSES ---

class GameActor(Actor):
    def __init__(self, image_name, pos):
        super().__init__(image_name, pos)
        self.velocity_y = 0
        self.on_ground = False

class Player(GameActor):
    """
    Classe do Herói: Controla o input do teclado e a física específica dele.
    """
    def update(self):
        self.move()
        self.apply_gravity()
        self.check_boundaries()

    def move(self):
        # Movimento Horizontal
        if keyboard.A:
            self.x -= SPEED
        elif keyboard.D:
            self.x += SPEED


        # PULO INICIAL (Sempre força máxima)
        if keyboard.W and self.on_ground:
            self.velocity_y = -15  # Força total para ir lá no alto
            self.on_ground = False

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

    def check_boundaries(self):
        # Colisão simples com o chão (temporário até termos plataformas)
        # O chão é na altura 500
        if self.y >= 500:
            self.y = 500
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

def on_key_up(key):
    # Se soltou ESPAÇO e o herói está subindo (velocidade negativa)
    if key == keys.W and hero.velocity_y < 0:
        hero.velocity_y = hero.velocity_y * 0.3 



# --- INICIALIZAÇÃO ---

#spawna o player no meio da tela 
hero = Player("player_idle_word01", (400, 100))

# --- LOOP PRINCIPAL DO PGZERO ---

def draw():
    screen.fill((135, 206, 235)) #céu
    
    # Desenha o chaol marrom
    screen.draw.filled_rect(Rect(0, 530, 800, 70), (100, 50, 0))
    
    hero.draw()

def update():
    hero.update()

# Inicia o jogo
pgzrun.go()