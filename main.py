import pgzrun
from pgzero.actor import Actor

# --- CONFIGURAÇÕES (CONSTANTES) ---
WIDTH = 1200
HEIGHT = 800
TITLE = "The Golden Skull"

# Configurações de Física
GRAVITY = 0.7
JUMP_POWER = -14
SPEED = 5

# --- CLASSES ---

class GameActor(Actor):
    def __init__(self, image_name, pos):
        super().__init__(image_name, pos)
        self.velocity_y = 0
        self.on_ground = False

class Player(GameActor):
    def __init__(self, pos):
        super().__init__("player_idle_word1", pos) 
        
        
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
        self.anim_speed = 0.15
        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.check_boundaries()
        self.animate() # Chama a função que troca as roupas

    def handle_input(self):
        
        
        self.is_moving = False

        if keyboard.A:
            self.x -= SPEED
            self.facing_right = False # Virou pra esquerda
            self.is_moving = True
        elif keyboard.D:
            self.x += SPEED
            self.facing_right = True # Virou pra direita
            self.is_moving = True

        # PULO com W
        if keyboard.W and self.on_ground:
            self.velocity_y = -15
            self.on_ground = False
            
        # ATAQUE com ESPAÇO (Só ataca se não estiver atacando já)
        if keyboard.space and not self.is_attacking:
            self.is_attacking = True
            self.frame = 0 # Reseta a animação para começar do frame 1 do ataque

    def animate(self):
        self.frame += self.anim_speed
        
        # --- MÁQUINA DE ESTADOS VISUAIS ---
        
        # PRIORIDADE 1: ATAQUE (Se estiver atacando, ignora o resto)
        if self.is_attacking:
            if self.facing_right:
                current_list = self.anim_attack_r
            else:
                current_list = self.anim_attack_l
            
            # Lógica especial do ataque: ele não entra em loop
            if self.frame >= len(current_list):
                self.is_attacking = False # Terminou o ataque
                self.frame = 0 # Reseta para a próxima animação
                # Força uma atualização imediata para não piscar
                if self.facing_right: current_list = self.anim_idle_r
                else: current_list = self.anim_idle_l
            
        # PRIORIDADE 2: PULO (Se não está no chão)
        elif not self.on_ground:
            if self.facing_right:
                current_list = self.anim_jump_r
            else:
                current_list = self.anim_jump_l
                
            # O pulo geralmente congela no último frame ou faz loop
            if self.frame >= len(current_list):
                self.frame = 0 

        # PRIORIDADE 3: CORRENDO (No chão e movendo)
        elif self.is_moving:
            if self.facing_right:
                current_list = self.anim_run_r
            else:
                current_list = self.anim_run_l
                
            if self.frame >= len(current_list):
                self.frame = 0

        # PRIORIDADE 4: PARADO (No chão e quieto)
        else:
            if self.facing_right:
                current_list = self.anim_idle_r
            else:
                current_list = self.anim_idle_l
            
            if self.frame >= len(current_list):
                self.frame = 0

        # APLICA A IMAGEM FINAL
        # Verificação de segurança para não quebrar se o frame passar do limite
        idx = int(self.frame)
        if idx < len(current_list):
            self.image = current_list[idx]

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

    def check_boundaries(self):
        # Chão temporário
        if self.y >= 500:
            self.y = 500
            self.velocity_y = 0
            self.on_ground = True
        else:
            # Se saiu do chão (caiu de uma plataforma), on_ground vira False
            # Mas cuidado: aqui estamos forçando 500. 
            # Quando tiver plataformas, essa lógica muda.
            pass

def on_key_up(key):
    # Pulo variável (corta o pulo se soltar o botão)
    if key == keys.W and hero.velocity_y < 0:
        hero.velocity_y = hero.velocity_y * 0.3 

# --- INICIALIZAÇÃO ---
# Use o nome da PRIMEIRA imagem da lista idle aqui para evitar erro no início
hero = Player((400, 100)) 

# --- LOOP PRINCIPAL ---
def draw():
    screen.fill((135, 206, 235))
    screen.draw.filled_rect(Rect(0, 530, 800, 70), (100, 50, 0))
    hero.draw()

def update():
    hero.update()

pgzrun.go()