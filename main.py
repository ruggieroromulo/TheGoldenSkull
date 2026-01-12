import pgzrun
from pgzero.actor import Actor
import random
from pygame import Rect

# --- SETTINGS (CONSTANTS) ---
WIDTH = 1200
HEIGHT = 800
TITLE = "The Golden Skull"

# Physics Settings
GRAVITY = 0.7
JUMP_POWER = -14
SPEED = 5

# --- GLOBAL VARIABLES ---
game_state = "menu"
sound_on = True 
platforms = [] 
enemies = []
hazards = [] 
goals = []   


btn_sound = Actor("btn_music", (1130, 90))
btn_start = Actor("btn_start", (180, 570))
btn_exit  = Actor("btn_exit",  (175, 690))


# --- CLASSES ---
class GameActor(Actor):
    def __init__(self, image_name, pos):
        super().__init__(image_name, pos)
        self.velocity_y = 0
        self.on_ground = False

class Block(GameActor):
    #if nothing is passed, “block” is used by default.
    def __init__(self, pos, img_name="block"):
        super().__init__(img_name, pos)

class Player(GameActor):
    def __init__(self, pos):
        super().__init__("player_idle_word1", pos) 
        
        
        # --- 1. ANIMATION LISTS ---
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

        # --- CONTROL VARIABLES ---
        self.frame = 0
        self.anim_speed = 0.2
        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False
        self.is_hurt = False
        self.has_dealt_damage = False

        # --- LIFE SYSTEM ---
        self.hp = 3.0 
        self.invulnerable_timer = 0 
        self.knockback = 0 #be pushed when damaged

    def update(self):
        #1. Unbeaten
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        
        #2. Knockback
        if self.knockback != 0:
            self.x += self.knockback
            if self.knockback > 0: self.knockback -= 1
            elif self.knockback < 0: self.knockback += 1
            
        # 3. If hurt, dont move.
        elif self.is_hurt:
            pass 
            
        # 4. Normal movement
        else:
            self.handle_input()
            
        self.apply_gravity()
        self.check_damage() 
        self.check_boundaries()
        
        # 5. Attack
        if self.is_attacking:
            self.deal_damage() 
            
        self.animate()
        
    def attack(self):
         if not self.is_attacking and not self.is_hurt:
            self.is_attacking = True
            self.has_dealt_damage = False # Restart to attack again
            self.frame = 0
            if sound_on:
                sounds.attack.play()
            
    def deal_damage(self):
        # Only try to deal damage if you haven't already dealt damage with this attack.
        # and if the animation has already passed the beginning
        if not self.has_dealt_damage and int(self.frame) >= 1:
            
            # Creates an Attack Hitbox in front of the player
            attack_rect = self._rect.inflate(-20, -20) # 
            
            # Throw the rectangle forward
            if self.facing_right:
                attack_rect.x += 40 # sword's reach
            else:
                attack_rect.x -= 40
            
            #  Checks if hit any enemies
            for enemy in enemies:
                if attack_rect.colliderect(enemy):
                    print("HIT!") # Debug
                    
                    # Takes the life of the enemy.
                    enemy.hp -= 1
                    
                    # If it's zero, remove it from the list  (kill)
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                    
                    # Enemies knockback
                    if self.x < enemy.x: enemy.x += 20
                    else: enemy.x -= 20
            
            # Marks that he has already struck so as not to cause infinite damage in the same attack.
            self.has_dealt_damage = True

    def check_boundaries(self):
        #1. Left Wall
        #2. If the side of the sprite is less than 0
        
        offset = -23 #Correcting the hitbox that pgZero mistakenly set for my asset
        if self.left < offset:
            self.left = offset # Lock him at 0
            
        # 2. Parede Direita
        if self.right > WIDTH -offset:
            self.right = WIDTH -offset # Lock him in at the limit
            
        

    def check_damage(self):
        # If you are already invincible, ignore damage
        if self.invulnerable_timer > 0:
            return

        # Hitbox Adjustment 
        hitbox = self._rect.inflate(-55, -10)

        # 1. ENEMY DAMAGE (1 heart)
        for enemy in enemies:
            if hitbox.colliderect(enemy):
                self.take_damage(1)
                # Push backward 
                if enemy.x > self.x: self.knockback = -10 # Push left
                else: self.knockback = 10 # Push right
                return

        # 2. THORN DAMAGE (1.0 heart)
        for spike in hazards:
            if hitbox.colliderect(spike):
                self.take_damage(1.0)
                self.velocity_y = -10 # Little jump of pain
                return
        
        # 3.  
        for skull in goals:
            if hitbox.colliderect(skull):
                
                if sound_on: 
                    music.set_volume(0.0)
                    sounds.win.play() 
                
                global game_state
                game_state = "win" 
                return

    def take_damage(self, amount):
        self.hp -= amount
        self.invulnerable_timer = 60
        
        # Visual/sound effects
        print(f"Ouch! Life: {self.hp}")
        self.is_hurt = True
        self.is_attacking = False
        self.frame = 0
        
        if sound_on:
            try: sounds.hit.play()
            except: pass
        
        
        if self.hp <= 0:
            print("Dieedd")
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
        #1. Applies gravity (falling)
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        #correcting the hitbox automatically defined by pgzero
        hitbox = self._rect.inflate(-60, -16) 

        #2. Checks for collision with EVERY block in the ‘platforms’ list
        for plat in platforms:

            #
            if hitbox.colliderect(plat):
                
    
                if self.velocity_y > 0:
                    
                    
                    diff = self.bottom - hitbox.bottom # Visual difference
                    
                    self.velocity_y = 0      # Stop falling
                    self.bottom = plat.top + diff # Sticks the player to the ground, compensating for the difference
                    self.on_ground = True    # Allows skipping
                    return 

        # If he passed through all the blocks and didn't touch anything,is flying.
        self.on_ground = False
        

    def animate(self):
        self.frame += self.anim_speed
        
        # --- VISUAL STATES MACHINE ---
        
         # PRIORITY 0: HIT - New highest priority
        if self.is_hurt:
            if self.facing_right: current_list = self.anim_hit_r
            else: current_list = self.anim_hit_l
            
            # When the hit animation ends, it returns to normal
            if self.frame >= len(current_list):
                self.is_hurt = False
                self.frame = 0
        
        # PRIORITY 1: ATTACK
        elif self.is_attacking:
            if self.facing_right: current_list = self.anim_attack_r
            else: current_list = self.anim_attack_l
            
            if self.frame >= len(current_list):
                self.is_attacking = False 
                self.frame = 0 
                if self.facing_right: current_list = self.anim_idle_r
                else: current_list = self.anim_idle_l
            
        # PRIORITY 2: JUMP
        elif not self.on_ground:
            if self.facing_right:
                current_list = self.anim_jump_r
            else:
                current_list = self.anim_jump_l
            
            if self.frame >= len(current_list):
                self.frame = len(current_list) - 1 # Lock on the last frame

        # PRIORITY 3: RUNNING
        elif self.is_moving:
            if self.facing_right:
                current_list = self.anim_run_r
            else:
                current_list = self.anim_run_l
                
            if self.frame >= len(current_list):
                self.frame = 0

        # PRIORITY 4: STOPPED
        else:
            if self.facing_right:
                current_list = self.anim_idle_r
            else:
                current_list = self.anim_idle_l
            
            if self.frame >= len(current_list):
                self.frame = 0

        # APPLIES THE IMAGE
        idx = int(self.frame)
        if idx < len(current_list):
            self.image = current_list[idx]


class Enemy(GameActor):
    def __init__(self, pos):
        super().__init__("enemy1_run1", pos)
        
        # --- ANIMATION LISTS ---
        self.anim_run_r = [
            "enemy1_run1", "enemy1_run2", "enemy1_run3", 
            "enemy1_run4", "enemy1_run5", "enemy1_run6"
        ]
        self.anim_run_l = [
            "enemy1_run_left1", "enemy1_run_left2", "enemy1_run_left3", 
            "enemy1_run_left4", "enemy1_run_left5", "enemy1_run_left6"
        ]
        
        # --- CONTROL ---
        self.frame = 0
        self.anim_speed = 0.15
        self.speed = 2 
        self.current_speed = 2 
        self.direction = 1 
        self.walk_count = 0 
        self.max_walk_distance = 150 
        self.state = "patrol"
        self.hp = 2 

        # --- SKIP ---
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
        # Only updates position and counter if speed is greater than 0
        if self.current_speed > 0:
            self.x += self.current_speed * self.direction
            self.walk_count += self.current_speed

            if self.walk_count > self.max_walk_distance:
                self.direction *= -1
                self.walk_count = -150

    def check_player_jump(self):
        #1. Separate distances
        distancia_x = abs(hero.x - self.x)
        distancia_y = abs(hero.y - self.y)

        #2. Enemy sensors
        limite_x = 170 
        limite_y = 60  

        player_esta_perto = (distancia_x < limite_x) and (distancia_y < limite_y)

        # TRIGGER
        if hero.velocity_y < 0 and player_esta_perto and self.on_ground and self.reaction_timer == 0:
            
            # FIXED TIME: x frames
            self.reaction_timer = 14
            
            self.current_speed = 0 

        # EXECUTION
        if self.reaction_timer > 0:
            self.reaction_timer -= 1
            
            if self.reaction_timer == 0:
                self.velocity_y = -17
                self.on_ground = False
                self.current_speed = 2

    def animate(self):
        # If the speed is 0 (getting ready to jump), don't animate!
        if self.current_speed == 0:
            self.frame = 0 # Lock in the first frame (feet on the ground)
        else:
            # If you're walking, cheer normally
            self.frame += self.anim_speed
        
        # List selection
        if self.direction > 0: 
            current_list = self.anim_run_r
        else: 
            current_list = self.anim_run_l

        # Loop
        if self.frame >= len(current_list):
            self.frame = 0
            
        self.image = current_list[int(self.frame)]
        
class Goal(Actor):
    def __init__(self, pos):
       
        super().__init__("skulll1", pos)


# --- GLOBAL FUNCTIONS ---
def create_level1():
    platforms.clear()
    enemies.clear()
    hazards.clear()
    goals.clear()  
    
    #1. Main floor
    for x in range(0, WIDTH, 32): 
        plat = Block((x, 790))
        platforms.append(plat)
        
    for x in range(600, 1170, 33):
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
    
    enemy3 = Enemy((750, 630))
    enemies.append(enemy3)
    
    enemy4 = Enemy((990, 630))
    enemies.append(enemy4)
    
    skull = Goal((1050, 150)) 
    goals.append(skull)


def on_key_up(key):
    # Variable jump (jump stops if you release the button)
    if key == keys.W and hero.velocity_y < 0:
        hero.velocity_y = hero.velocity_y * 0.3 

def on_mouse_down(pos, button):
    global game_state, sound_on
    
    #1. If you are in the MENU
    if game_state == "menu":
        # Check for collision with the START button
        if btn_start.collidepoint(pos):
            print("Clicou em Iniciar")
            create_level1() # Reset the map
            hero.hp = 3.0   # Fills life
            hero.pos = (70, 745) # Starting position
            game_state = "game" 
            if sound_on:
                music.play("game")   
                music.set_volume(0.3)
            
        # Check collision with the SOUND button
        elif btn_sound.collidepoint(pos):
            print("Clicou no Som")
            sound_on = not sound_on
            
            if sound_on:
                print("Som LIGADO")
                try: music.set_volume(0.3) # Volume 30%
                except: pass
            else:
                print("Som DESLIGADO")
                try: music.set_volume(0) # Volume 0 (Silent)
                except: pass

            
        # Check collision with the EXIT button
        elif btn_exit.collidepoint(pos):
            print("leaving...")
            exit()

    #2. If you are in the GAME
    elif game_state == "game":
        if button == mouse.LEFT:
            hero.attack()
            

def on_key_down(key):
    global game_state
    
    if game_state == "game_over" and key == keys.SPACE:
        create_level1()
        hero.hp = 3.0
        hero.pos = (70, 745)
        game_state = "game"
        
    elif game_state == "win" and key == keys.SPACE:
        game_state = "menu"
        
        if sound_on:
            music.play("menu")
            music.set_volume(0.3)
        

# --- INITIALIZATION ---
create_level1() # Cria o chão
hero = Player((70, 745)) # Começa em cima do chão


# --- MAIN LOOP ---
def draw_hud():
    for i in range(3): # 0, 1, 2
        # Position on screen (top left corner)
        x = 20 + (i * 100) 
        y = 20
        
        
        if hero.hp >= i + 1:
            screen.blit("small_heart", (x, y)) #a heart
        elif hero.hp > i:
            screen.blit("small_heart", (x, y)) #two
            screen.blit("small_heart", (x, y)) #three

def draw():
    screen.blit("level1_bg", (0, 0))  # Sky
    
    if game_state == "menu":
        
        screen.blit("menu_bg", (0, 0)) 
        btn_start.draw()
        btn_sound.draw()
        btn_exit.draw()
        

    elif game_state == "game":
        
        for plat in platforms: plat.draw()
        for spike in hazards: spike.draw()
        for skull in goals: skull.draw()
        for enemy in enemies: enemy.draw()
        hero.draw()
        draw_hud()

    elif game_state == "game_over":
        screen.fill((0, 0, 0))
        #slow down the msc
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=80, color="red")
        screen.draw.text("Press SPACE to try again", center=(WIDTH/2, HEIGHT/2 + 60), fontsize=30)

    elif game_state == "win":
        
        # Title
        screen.draw.text("Victory!", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=100, color="gold", )
        
        screen.blit("win_bg2", (0, 0)) 
        
        # Instruction
        screen.draw.text("You recovered the Golden Skull!", center=(WIDTH/2, 30), fontsize=30, color="black")
        screen.draw.text("Press SPACE to return to the Menu.", center=(WIDTH/2, 50), fontsize=23, color="black")
        
def update():
    if game_state == "game":
        hero.update()
        for enemy in enemies: enemy.update()
        
if sound_on:
        music.play("menu")   
        music.set_volume(0.3) 
git add .
      # Sets initial volume (30%)
    
           

pgzrun.go()