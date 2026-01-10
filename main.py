import pgzrun
from pgzero.actor import Actor
from pygame import Rect

# --- CONFIGURAÇÕES (CONSTANTES) ---
WIDTH = 1200
HEIGHT = 800
TITLE = "The Golden Skull"

# Configurações de Física
GRAVITY = 0.7
JUMP_POWER = -14
SPEED = 5

# --- VARIÁVEIS GLOBAIS ---
platforms = [] # Lista de plataformas precisa ser uma variavel global

# --- CLASSES ---

class GameActor(Actor):
    def __init__(self, image_name, pos):
        super().__init__(image_name, pos)
        self.velocity_y = 0
        self.on_ground = False

class Block(GameActor):
    # Agora aceita um segundo argumento opcional 'img_name'
    # Se não passar nada, ele usa "block" por padrão
    def __init__(self, pos, img_name="block"):
        super().__init__(img_name, pos)

class Player(GameActor):
    def __init__(self, pos):
        super().__init__("player_idle_word1", pos) 
        
        # --- 1. LISTAS DE ANIMAÇÃO ---
        
        # IDLE (Parado)
        self.anim_idle_r = [
            "player_idle_word1", "player_idle_word2", "player_idle_word3", "player_idle_word4", "player_idle_word5"
        ]
        self.anim_idle_l = [
            "player_idle_word_left1", "player_idle_word_left2", "player_idle_word_left3", "player_idle_word_left4", "player_idle_word_left5"
        ]
        
        # RUN (Correndo)
        self.anim_run_r = [
            "player_run_sword1", "player_run_sword2", "player_run_sword3", 
            "player_run_sword4", "player_run_sword5", "player_run_sword6"
        ]
        self.anim_run_l = [
            "player_run_sword_left1", "player_run_sword_left2", "player_run_sword_left3", 
            "player_run_sword_left4", "player_run_sword_left5", "player_run_sword_left6"
        ]
        
        # JUMP (Pulo)
        self.anim_jump_r = ["player_jump_sword1", "player_jump_sword2", "player_jump_sword3"]
        self.anim_jump_l = ["player_jump_sword_left1", "player_jump_sword_left2", "player_jump_sword_left3"]

        # ATTACK (Ataque)
        self.anim_attack_r = ["player_attack1", "player_attack2", "player_attack3"]
        self.anim_attack_l = ["player_attack_left1", "player_attack_left2", "player_attack_left3"]

        # --- VARIÁVEIS DE CONTROLE ---
        self.frame = 0
        self.anim_speed = 0.17
        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.check_boundaries()
        self.animate()

    def attack(self):
        # Só ataca se não estiver atacando
        if not self.is_attacking:
            self.is_attacking = True
            self.frame = 0 # Reinicia a animação

    def check_boundaries(self):
        # 1. Parede Esquerda
        # Se o lado esquerdo do boneco for menor que 0
        offset = -23

        if self.left < offset:
            self.left = offset # Trava ele no 0
            
        # 2. Parede Direita
        # Se o lado direito do boneco passar da largura da tela
        if self.right > WIDTH -offset:
            self.right = WIDTH -offset # Trava ele no limite
            
        # 3. Buraco (Morte) - Mantemos o que já existia
        if self.y > HEIGHT + 100:
            print("Caiu no buraco!")
            self.pos = (100, 500) # Reset
            self.velocity_y = 0


    def handle_input(self):
        self.is_moving = False

        if keyboard.A:
            self.x -= SPEED
            self.facing_right = False 
            self.is_moving = True

        elif keyboard.D:
            self.x += SPEED
            self.facing_right = True 
            self.is_moving = True

        if keyboard.W and self.on_ground:
            self.velocity_y = JUMP_POWER
            self.on_ground = False
            

    def apply_gravity(self):
        # 1. Aplica a gravidade (cair)
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        #correcting the hitbox automatically defined by pgzero
        hitbox = self._rect.inflate(-60, -16) 

        # 2. Verifica colisão com CADA bloco da lista 'platforms'
        for plat in platforms:

            #
            if hitbox.colliderect(plat):
                
    
                if self.velocity_y > 0:
                    
                    
                    diff = self.bottom - hitbox.bottom # Diferença visual
                    
                    self.velocity_y = 0      # Para de cair
                    self.bottom = plat.top + diff # Cola o jogador no chão compensando a diferença
                    self.on_ground = True    # Permite pular
                    return 

        # Se passou por todos os blocos e não tocou em nada, está voando
        self.on_ground = False
        

    def animate(self):
        self.frame += self.anim_speed
        
        # --- MÁQUINA DE ESTADOS VISUAIS ---
        
        # PRIORIDADE 1: ATAQUE
        if self.is_attacking:
            if self.facing_right:
                current_list = self.anim_attack_r
            else:
                current_list = self.anim_attack_l
            
            # Lógica especial do ataque: ele não entra em loop
            if self.frame >= len(current_list):
                self.is_attacking = False 
                self.frame = 0 
                # Força update imediato
                if self.facing_right: current_list = self.anim_idle_r
                else: current_list = self.anim_idle_l
            
        # PRIORIDADE 2: PULO
        elif not self.on_ground:
            if self.facing_right:
                current_list = self.anim_jump_r
            else:
                current_list = self.anim_jump_l
            
            if self.frame >= len(current_list):
                self.frame = len(current_list) - 1 # Trava no ultimo frame

        # PRIORIDADE 3: CORRENDO
        elif self.is_moving:
            if self.facing_right:
                current_list = self.anim_run_r
            else:
                current_list = self.anim_run_l
                
            if self.frame >= len(current_list):
                self.frame = 0

        # PRIORIDADE 4: PARADO
        else:
            if self.facing_right:
                current_list = self.anim_idle_r
            else:
                current_list = self.anim_idle_l
            
            if self.frame >= len(current_list):
                self.frame = 0

        # APLICA A IMAGEM
        idx = int(self.frame)
        if idx < len(current_list):
            self.image = current_list[idx]



# --- FUNÇÕES GLOBAIS ---

def create_level1():
    platforms.clear()
    
    # 1. Chão principal (Continua usando o bloco sólido padrão)
    for x in range(0, WIDTH, 32): 
        plat = Block((x, 790), "block") # Passamos "block" explicitamente
        platforms.append(plat)
        
    for x in range(600, 1100, 33):
        plat = Block((x, 630), "platform") 
        platforms.append(plat)

    for x in range(50, 500, 33):
        plat = Block((x, 530), "platform") 
        platforms.append(plat)

    for x in range(70, 100, 33):
        plat = Block((x, 400), "platform") 
        platforms.append(plat)

    for x in range(50, 500, 33):
        plat = Block((x, 270), "platform") 
        platforms.append(plat)

    for x in range(650, 670, 20):
        plat = Block((x, 290), "platform") 
        platforms.append(plat)

    for x in range(810, 830, 20):
        plat = Block((x, 240), "platform") 
        platforms.append(plat)

    for x in range(950, 1150, 33):
        plat = Block((x, 200), "platform") 
        platforms.append(plat)


def on_key_up(key):
    # Pulo variável (corta o pulo se soltar o botão)
    if key == keys.W and hero.velocity_y < 0:
        hero.velocity_y = hero.velocity_y * 0.3 

def on_mouse_down(pos, button):
    # Se o botão for o ESQUERDO
    if button == mouse.LEFT:
        hero.attack()

# --- INICIALIZAÇÃO ---

create_level1() # Cria o chão
hero = Player((100, 600)) # Começa em cima do chão


# --- LOOP PRINCIPAL ---

def draw():
    screen.fill((135, 206, 235))
    
    # Desenha todas as plataformas
    for plat in platforms:
        plat.draw()
        
    hero.draw()

def update():
    hero.update()

pgzrun.go()