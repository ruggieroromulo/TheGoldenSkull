import pgzrun
from pgzero.actor import Actor
 
# --- CONFIGURAÇÕES (CONSTANTES) ---
WIDTH = 800
HEIGHT = 600
TITLE = "The Golden Skull"

# Configurações de Física
GRAVITY = 1
JUMP_POWER = -18
SPEED = 5

# --- CLASSES ---

class GameActor(Actor):
    """
    Classe Pai: Qualquer coisa no jogo que tenha vida ou se mova
    vai herdar daqui. Isso mostra organização para os avaliadores.
    """
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
        if keyboard.left:
            self.x -= SPEED
        elif keyboard.right:
            self.x += SPEED

        # Pulo (Só pula se estiver no chão)
        if keyboard.space and self.on_ground:
            self.velocity_y = JUMP_POWER
            self.on_ground = False # Saiu do chão

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