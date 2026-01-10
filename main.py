import pgzrun
from pgzero.actor import Actor
import random
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
platforms = [] 
enemies = []
hazards = [] 
goals = []   


# --- CLASSES ---

class GameActor(Actor):
    def __init__(self, image_name, pos):
        super().__init__(image_name, pos)
        self.velocity_y = 0
        self.on_ground = False

class Block(GameActor):
    # Se não passar nada, "block" é usado por padrão
    def __init__(self, pos, img_name="block"):
        super().__init__(img_name, pos)

class Player(GameActor):
    def __init__(self, pos):
        super().__init__("player_idle_word1", pos) 
        
        # --- 1. LISTAS DE ANIMAÇÃO ---
        
        # IDLE 
        self.anim_idle_r = [
            "player_idle_word1", "player_idle_word2", "player_idle_word3", "player_idle_word4", "player_idle_word5"
        ]
        self.anim_idle_l = [
            "player_idle_word_left1", "player_idle_word_left2", "player_idle_word_left3", "player_idle_word_left4", "player_idle_word_left5"
        ]
        
        # RUN 
        self.anim_run_r = [
            "player_run_sword1", "player_run_sword2", "player_run_sword3", 
            "player_run_sword4", "player_run_sword5", "player_run_sword6"
        ]
        self.anim_run_l = [
            "player_run_sword_left1", "player_run_sword_left2", "player_run_sword_left3", 
            "player_run_sword_left4", "player_run_sword_left5", "player_run_sword_left6"
        ]
        
        # JUMP 
        self.anim_jump_r = ["player_jump_sword1", "player_jump_sword2", "player_jump_sword3"]
        self.anim_jump_l = ["player_jump_sword_left1", "player_jump_sword_left2", "player_jump_sword_left3"]

        # ATTACK 
        self.anim_attack_r = ["player_attack1", "player_attack2", "player_attack3"]
        self.anim_attack_l = ["player_attack_left1", "player_attack_left2", "player_attack_left3"]
        
        # HIT
        self.anim_hit_r = ["player_hit1", "player_hit2", "player_hit3", "player_hit4"] 
        self.anim_hit_l = ["player_hit_left1", "player_hit_left2", "player_hit_left3", "player_hit_left4"] 

        # --- VARIÁVEIS DE CONTROLE ---
        self.frame = 0
        self.anim_speed = 0.2
        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False
        self.is_hurt = False
        self.has_dealt_damage = False

        # --- SISTEMA DE VIDA ---
        self.hp = 3.0 
        self.invulnerable_timer = 0 
        self.knockback = 0 # Empurrão quando toma dano

    def update(self):
        # Lógica de Empurrão (Knockback)
        if self.knockback > 0:
            self.x += self.knockback
            if self.knockback > 0: self.knockback -= 1
            elif self.knockback < 0: self.knockback += 1
        # Se estiver machucado (animação de hit), não deixa mover
        elif self.is_hurt:
            pass 
        else:
            self.handle_input()
            
        self.apply_gravity()
        self.check_damage() # Verifica se tomou dano
        self.check_boundaries()
        
        # NOVA LÓGICA: DAR DANO
        if self.is_attacking:
            self.deal_damage() # Verifica se acertou alguém
            
        self.animate() 
        
    def attack(self):
         if not self.is_attacking and not self.is_hurt:
            self.is_attacking = True
            self.has_dealt_damage = False # Reseta para poder bater de novo
            self.frame = 0
            
    def deal_damage(self):
        # Só tenta dar dano se ainda não deu neste golpe
        # E se a animação já passou do começo (frame 1 ou 2 é o ideal visualmente)
        if not self.has_dealt_damage and int(self.frame) >= 1:
            
            # Cria uma Hitbox de Ataque na frente do jogador
            attack_rect = self._rect.inflate(-20, -20) # Começa com o tamanho do player
            
            # Joga o retângulo para a frente
            if self.facing_right:
                attack_rect.x += 40 # Ajuste esse número para o alcance da espada
            else:
                attack_rect.x -= 40
            
            # Verifica se pegou em algum inimigo
            for enemy in enemies:
                # Usamos colliderect com o retângulo criado
                if attack_rect.colliderect(enemy):
                    print("TOMA ESSA!") # Debug
                    
                    # Tira vida do inimigo
                    enemy.hp -= 1
                    
                    # Se zerou, remove da lista (mata)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                    
                    # Empurra o inimigo (opcional)
                    if self.x < enemy.x: enemy.x += 20
                    else: enemy.x -= 20
            
            # Marca que já bateu para não dar dano infinito no mesmo ataque
            self.has_dealt_damage = True

    def check_boundaries(self):
        # 1. Parede Esquerda
        # Se o lado esquerdo do boneco for menor que 0
        offset = -23

        if self.left < offset:
            self.left = offset # Trava ele no 0
            
        # 2. Parede Direita
        if self.right > WIDTH -offset:
            self.right = WIDTH -offset # Trava ele no limite
            
        # 3. Buraco (Morte) - Mantemos o que já existia
        if self.y > HEIGHT + 100:
            print("Caiu no buraco!")
            self.pos = (100, 500) # Reset
            self.velocity_y = 0

    def check_damage(self):
        # Se já estiver invencível (piscou recentemente), ignora dano
        if self.invulnerable_timer > 0:
            return

        # Ajuste da Hitbox para ser justa
        hitbox = self._rect.inflate(-80, -10)

        # 1. DANO DE INIMIGOS (0.5 corações)
        for enemy in enemies:
            if hitbox.colliderect(enemy):
                self.take_damage(0.5)
                # Empurrão para trás (Knockback)
                if enemy.x > self.x: self.knockback = -10 # Empurra pra esquerda
                else: self.knockback = 10 # Empurra pra direita
                return

        # 2. DANO DE ESPINHOS (1.0 coração - ou Morte, você decide)
        for spike in hazards:
            if hitbox.colliderect(spike):
                self.take_damage(1.0)
                self.velocity_y = -10 # Pulinho de dor
                return

    def take_damage(self, amount):
        self.hp -= amount
        self.invulnerable_timer = 60
        
        # ATIVA ESTADO DE MACHUCADO
        self.is_hurt = True
        self.is_attacking = False # Cancela ataque se tomar dano
        self.frame = 0 # Começa animação de hit
        
        print(f"Ai! Vida: {self.hp}")
        
        if self.hp <= 0:
            print("GAME OVER")
            self.pos = (100, 600)
            self.hp = 3.0


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
        
         # PRIORIDADE 0: MACHUCADO (HIT) - Nova prioridade máxima
        if self.is_hurt:
            if self.facing_right: current_list = self.anim_hit_r
            else: current_list = self.anim_hit_l
            
            # Quando a animação de hit acaba, volta ao normal
            if self.frame >= len(current_list):
                self.is_hurt = False
                self.frame = 0
        
        # PRIORIDADE 1: ATAQUE
        elif self.is_attacking:
            # ... (o resto continua igual ao seu código anterior) ...
            if self.facing_right: current_list = self.anim_attack_r
            else: current_list = self.anim_attack_l
            
            if self.frame >= len(current_list):
                self.is_attacking = False 
                self.frame = 0 
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


class Enemy(GameActor):
    def __init__(self, pos):
        super().__init__("enemy1_run1", pos)
        
        # --- LISTAS DE ANIMAÇÃO ---
        self.anim_run_r = [
            "enemy1_run1", "enemy1_run2", "enemy1_run3", 
            "enemy1_run4", "enemy1_run5", "enemy1_run6"
        ]
        self.anim_run_l = [
            "enemy1_run_left1", "enemy1_run_left2", "enemy1_run_left3", 
            "enemy1_run_left4", "enemy1_run_left5", "enemy1_run_left6"
        ]
        
        # --- CONTROLE ---
        self.frame = 0
        self.anim_speed = 0.15
        self.speed = 2 
        self.current_speed = 2 
        self.direction = 1 
        self.walk_count = 0 
        self.max_walk_distance = 150 
        self.state = "patrol"
        self.hp = 2 

        # --- PULO ---
        self.velocity_y = 0
        self.on_ground = False
        self.reaction_timer = 0 

    def update(self):
        self.apply_gravity()
        
        if self.state == "patrol":
            self.patrol()
            self.check_player_jump()
            
        self.animate()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        self.on_ground = False 

        for plat in platforms:
            if self.colliderect(plat) and self.velocity_y > 0 and self.bottom < plat.bottom:
                self.bottom = plat.top
                self.velocity_y = 0
                self.on_ground = True

    def patrol(self):
        # Só atualiza posição e contador se a velocidade for maior que 0
        if self.current_speed > 0:
            self.x += self.current_speed * self.direction
            self.walk_count += self.current_speed

            if self.walk_count > self.max_walk_distance:
                self.direction *= -1
                self.walk_count = -150

    def check_player_jump(self):
        distance_x = abs(hero.x - self.x)

        # GATILHO (Sem Random)
        if hero.velocity_y < 0 and distance_x < 200 and self.on_ground and self.reaction_timer == 0:
            
            # 1. TEMPO FIXO: 30 frames = 0.5 segundos exatos
            self.reaction_timer = 12
            
            # 2. PARA O INIMIGO
            self.current_speed = 0 

        # EXECUÇÃO
        if self.reaction_timer > 0:
            self.reaction_timer -= 1
            
            # Quando chega no zero, PULA e volta a andar
            if self.reaction_timer == 0:
                self.velocity_y = -12
                self.on_ground = False
                self.current_speed = 2 # Devolve a velocidade

    def animate(self):
        # TRUQUE DO "IDLE FALSO"
        # Se a velocidade for 0 (está se preparando pra pular), não anima!
        if self.current_speed == 0:
            self.frame = 0 # Trava no primeiro quadro (pés no chão)
        else:
            # Se está andando, anima normal
            self.frame += self.anim_speed
        
        # Seleção de lista
        if self.direction > 0: 
            current_list = self.anim_run_r
        else: 
            current_list = self.anim_run_l

        # Loop
        if self.frame >= len(current_list):
            self.frame = 0
            
        self.image = current_list[int(self.frame)]


# --- FUNÇÕES GLOBAIS ---
def create_level1():
    platforms.clear()
    enemies.clear()
    hazards.clear()
    goals.clear()  
    
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
    
    bug = Enemy((250, 500))
    enemies.append(bug)


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
    
    for plat in platforms:
        plat.draw()
        
    for enemy in enemies:
        enemy.draw() # Desenha os inimigos
        
    hero.draw()

def update():
    hero.update()
    # Atualiza todos os inimigos
    for enemy in enemies:
        enemy.update()
pgzrun.go()