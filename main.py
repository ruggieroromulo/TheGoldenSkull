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
game_state = "menu"
sound_on = True 
platforms = [] 
enemies = []
hazards = [] 
goals = []   


btn_start = Actor("btn_start", (WIDTH/2, 300))
btn_sound = Actor("btn_music", (WIDTH/2, 500))
btn_exit  = Actor("btn_exit",  (WIDTH/2, 700))


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
        #1. Invencibilidade
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        
        #2. Knockback
        if self.knockback != 0:
            self.x += self.knockback
            if self.knockback > 0: self.knockback -= 1
            elif self.knockback < 0: self.knockback += 1
            
        # 3. Se estiver machucado, não move
        elif self.is_hurt:
            pass 
            
        # 4. Movimento normal
        else:
            self.handle_input()
            
        self.apply_gravity()
        self.check_damage() 
        self.check_boundaries()
        
        # 5. Ataque
        if self.is_attacking:
            self.deal_damage() 
            
        self.animate()
        
    def attack(self):
         if not self.is_attacking and not self.is_hurt:
            self.is_attacking = True
            self.has_dealt_damage = False # Reseta para poder bater de novo
            self.frame = 0
            if sound_on:
                sounds.attack.play()
            
    def deal_damage(self):
        # Só tenta dar dano se ainda não deu neste golpe
        # E se a animação já passou do começo
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
                if attack_rect.colliderect(enemy):
                    print("TOMA ESSA!") # Debug
                    
                    # Tira vida do inimigo
                    enemy.hp -= 1
                    
                    # Se zerou, tira da lista(elimina)
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
        
        offset = -23 #Corrigindo a hitbox que o phzero setou para meu asset

        if self.left < offset:
            self.left = offset # Trava ele no 0
            
        # 2. Parede Direita
        if self.right > WIDTH -offset:
            self.right = WIDTH -offset # Trava ele no limite
            
        

    def check_damage(self):
        # Se já estiver invencível, ignora dano
        if self.invulnerable_timer > 0:
            return

        # Ajuste da Hitbox para ser justa
        hitbox = self._rect.inflate(-80, -10)

        # 1. DANO DE INIMIGOS (1 coracao)
        for enemy in enemies:
            if hitbox.colliderect(enemy):
                self.take_damage(1)
                # Empurrão para tras 
                if enemy.x > self.x: self.knockback = -10 # Empurra esquerda
                else: self.knockback = 10 # Empurra direita
                return

        # 2. DANO DE ESPINHOS (1.0 coração - ou Morte)
        for spike in hazards:
            if hitbox.colliderect(spike):
                self.take_damage(1.0)
                self.velocity_y = -10 # Pulinho de dor
                return

    def take_damage(self, amount):
        self.hp -= amount
        self.invulnerable_timer = 60
        
        # Efeitos visuais/sonoros
        print(f"Ai! Vida: {self.hp}")
        self.is_hurt = True
        self.is_attacking = False
        self.frame = 0
        
        if sound_on:
            try: sounds.hit.play()
            except: pass
        
        # AQUI ESTÁ A CORREÇÃO:
        if self.hp <= 0:
            print("MORREUUUUUUUUU")
            global game_state
            game_state = "game_over"


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
            
            if sound_on:
                sounds.jump2.set_volume(0.1)
                sounds.jump2.play()
            
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
        # 1. Distâncias separadas
        distancia_x = abs(hero.x - self.x)
        distancia_y = abs(hero.y - self.y)

        # 2. Seus limites personalizados
        limite_x = 160 
        limite_y = 30  

        player_esta_perto = (distancia_x < limite_x) and (distancia_y < limite_y)

        # GATILHO
        if hero.velocity_y < 0 and player_esta_perto and self.on_ground and self.reaction_timer == 0:
            
            # TEMPO FIXO: 15frames
            self.reaction_timer = 15
            
            self.current_speed = 0 

        # EXECUÇÃO
        if self.reaction_timer > 0:
            self.reaction_timer -= 1
            
            if self.reaction_timer == 0:
                self.velocity_y = -16 
                self.on_ground = False
                self.current_speed = 2

    def animate(self):
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
    
    enemy1 = Enemy((250, 500))
    enemies.append(enemy1)
    
    enemy2 = Enemy((250, 230))
    enemies.append(enemy2)


def on_key_up(key):
    # Pulo variável (corta o pulo se soltar o botão)
    if key == keys.W and hero.velocity_y < 0:
        hero.velocity_y = hero.velocity_y * 0.3 

def on_mouse_down(pos, button):
    global game_state, sound_on
    
    # 1. Se estiver no MENU
    if game_state == "menu":
        # Verifica colisão com o botão INICIAR
        if btn_start.collidepoint(pos):
            print("Clicou em Iniciar")
            create_level1() # Reseta o mapa
            hero.hp = 3.0   # Enche a vida
            hero.pos = (100, 600) # Posição inicial
            game_state = "game" # MUDA O ESTADO
            
        # Verifica colisão com o botão SOM (Use ELIF)
        elif btn_sound.collidepoint(pos):
            print("Clicou no Som")
            sound_on = not sound_on
            if sound_on: 
                music.set_volume(0.3)

            
        # Verifica colisão com o botão SAIR (Use ELIF)
        elif btn_exit.collidepoint(pos):
            print("Saindo...")
            exit()

    # 2. Se estiver no JOGO
    elif game_state == "game":
        if button == mouse.LEFT:
            hero.attack()
            

def on_key_down(key):
    global game_state
    
    if game_state == "game_over" and key == keys.RETURN:
        create_level1()
        hero.hp = 3.0
        hero.pos = (100, 600)
        game_state = "game"
        
    elif game_state == "win" and key == keys.RETURN:
        game_state = "menu"
        

# --- INICIALIZAÇÃO ---
create_level1() # Cria o chão
hero = Player((100, 600)) # Começa em cima do chão


# --- LOOP PRINCIPAL ---
def draw_hud():
    for i in range(3): # 0, 1, 2
        # Posição na tela (canto superior esquerdo)
        x = 20 + (i * 100) 
        y = 20
        
        
        if hero.hp >= i + 1:
            screen.blit("small_heart", (x, y)) #um coracao
        elif hero.hp > i:
            screen.blit("small_heart", (x, y)) #dois
            screen.blit("small_heart", (x, y)) #tres

def draw():
    screen.fill((135, 206, 235)) # Céu
    
    if game_state == "menu":
        
        #screen.draw.image("THE GOLDEN SKULL", center=(WIDTH/2, 150))
        
        btn_start.draw()
        btn_sound.draw()
        btn_exit.draw()
        

    elif game_state == "game":
        # O jogo normal
        for plat in platforms: plat.draw()
        for spike in hazards: spike.draw()
        for skull in goals: skull.draw()
        for enemy in enemies: enemy.draw()
        hero.draw()
        draw_hud()

    elif game_state == "game_over":
        screen.fill((0, 0, 0))
        #deixar a msc mais lenta
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=80, color="red")
        screen.draw.text("Press ENTER to try again", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=30)

    elif game_state == "win":
        #trocar a trilha sonora pra vitoriosa
        screen.draw.text("YOU WIN!", center=(WIDTH/2, HEIGHT/2), fontsize=80, color="gold")
        screen.draw.text("Press ENTER to back on menu", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=30)

def update():
    if game_state == "game":
        hero.update()
        for enemy in enemies: enemy.update()
        
if sound_on:
    try:
        music.play("game")   # Toca a música
        music.set_volume(0.3) # Define volume inicial (30%)
    except:
        print("Erro: Música não encontrada")

        

pgzrun.go()