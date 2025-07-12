import pygame
import sys
import os
import random 
from .player import Player
from .enemy import BasicEnemy, StrongEnemy, FinalBoss
from .cloud import Cloud 
from .satellite import Satellite
from .shield import Shield
from .cinematic import Cinematics

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Invasión Espacial")

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 28)
        # Variables niveles
        self.current_level = 1
        self.max_levels = 3
        self.level_background = None
        self.load_level_background()

        self.player = Player(self.screen_width // 2, self.screen_height - 70)
        self.enemies = []
        self.create_enemies()

        # Volúmenes
        self.volume_general = 0.5
        self.volume_musica = 0.5
        self.volume_efectos = 0.5
        self.muted = False

        # Variables  generales
        self.score = 0
        self.game_over = False
        self.enemy_direction = 1
        self.enemy_speed_increase = 0.5
        self.enemy_move_timer = 0
        self.enemy_move_interval = 15

        # Variables para nubes/tiempo
        self.clouds = []
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = 60

        self.satellites = []
        self.satellite_spawn_timer = 0
        self.satellite_spawn_interval_min = 240
        self.satellite_spawn_interval_max = 480
        self.next_satellite_spawn_interval = random.randint(self.satellite_spawn_interval_min, self.satellite_spawn_interval_max)
        self.shields = []
        self.paused = False
        self.pause_menu_state = "main"  
        self.pause_buttons = []
        self.game_over_buttons = []
        # Variables para cinematicas
        self.cinematics = Cinematics(self.screen_width, self.screen_height)
        self.show_intro_cinematic = True  # Control para mostrar cinemática solo al inicio

        # Para menú de victoria
        self.victory = False
        self.victory_buttons = []

        # Ruta para archivo de guardado
        base_path = os.path.dirname(__file__)
        self.save_path = os.path.join(base_path, '..', 'savegame.txt')

         # Inicializar mixer y cargar sonido de clic
        try:
            pygame.mixer.init()
            click_sound_path = os.path.join(base_path, '..', 'sounds', 'eleccion_menu.mp3')
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            self.click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de elección de menú: {e}")
            self.click_sound = None

        # Sonido de pasar mouse sobre botones del menú de pausa
        self.hover_sound = None
        self.hovered_pause_buttons = set()
        try:
            base_path = os.path.dirname(__file__)
            hover_sound_path = os.path.join(base_path, '..', 'sounds', 'seleccionar_menu.mp3')
            self.hover_sound = pygame.mixer.Sound(hover_sound_path)
            self.hover_sound.set_volume(0.5)
        except Exception as e:  
            print(f"Error cargando sonido de selección de pausa: {e}")

        # Sonido de daño recibido por el jugador
        try:
            damage_sound_path = os.path.join(base_path, '..', 'sounds', 'daño_recibido_prota.mp3')
            self.damage_sound = pygame.mixer.Sound(damage_sound_path)
            self.damage_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de daño del jugador: {e}")
            self.damage_sound = None

        # Sonido de disparo del jugador
        try:
            shoot_sound_path = os.path.join(base_path, '..', 'sounds', 'disparo_protagonista.mp3')
            self.shoot_sound = pygame.mixer.Sound(shoot_sound_path)
            self.shoot_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de disparo del jugador: {e}")
            self.shoot_sound = None

        # Sonido de estructura destruida
        try:
            destroyed_sound_path = os.path.join(base_path, '..', 'sounds', 'estructura_destruida.mp3')
            self.destroyed_sound = pygame.mixer.Sound(destroyed_sound_path)
            self.destroyed_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de estructura destruida: {e}")
            self.destroyed_sound = None

        # Sonido de muerte
        try:
            death_sound_path = os.path.join(base_path, '..', 'sounds', 'sonido_muerte_prota.mp3')
            self.death_sound = pygame.mixer.Sound(death_sound_path)
            self.death_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de muerte del protagonista: {e}")
            self.death_sound = None

        # Reproducir la música del nivel actual al iniciar
        self.play_level_music()

    def play_level_music(self):
        base_path = os.path.dirname(__file__)
        sounds_path = os.path.join(base_path, '..', 'sounds')
        
        pygame.mixer.music.stop()
        
        if self.current_level % 3 == 0:
            music_file = os.path.join(sounds_path, 'musica_jefe_final.mp3')
        elif self.current_level > 3:
            music_file = os.path.join(sounds_path, 'musica_nivel2.mp3')
        else:
            music_file = os.path.join(sounds_path, f'musica_nivel{self.current_level}.mp3')
        
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)  # Loop infinito
        except Exception as e:
            print(f"Error cargando música {music_file}: {e}")

    
    # NIVELES
    def load_level_background(self):
        base_path = os.path.dirname(__file__)

        if self.current_level == 1:
            image_name = 'lvl1.png'
        elif self.current_level == 2:
            image_name = 'lvl2.png'
        else:  # Nivel 3 y siguientes
            image_name = 'lvl3.png'

        image_path = os.path.join(base_path, '..', 'images', image_name)
        image_path = os.path.abspath(image_path)

        print(f"Cargando fondo del nivel {self.current_level} desde: {image_path}")

        try:
            self.level_background = pygame.image.load(image_path).convert()
            self.level_background = pygame.transform.scale(self.level_background, (self.screen_width, self.screen_height))
        except pygame.error as e:
            print(f"Error al cargar la imagen de fondo {image_name}: {e}")
            self.level_background = None

    def create_enemies(self):
        self.enemies = []

        # Vida base y aumento por nivel
        base_life_lvl1 = 1 + (self.current_level - 1)
        base_life_lvl2 = 2 + (self.current_level - 1)

        # Velocidad base y aumento progresivo
        base_speed_lvl1 = 4 + 0.2 * (self.current_level - 1)
        base_speed_lvl2 = 4.5 + 0.2 * (self.current_level - 1)

        # Cadencia de disparo (probabilidad), aumentamos progresivamente
        # Ejemplo: multiplicar la base por un factor creciente
        base_shoot_prob_lvl1 = 0.06 * (1 + 0.1 * (self.current_level - 1))
        base_shoot_prob_lvl2 = 0.12 * (1 + 0.1 * (self.current_level - 1))

        if self.current_level % 3 == 0:
            # Jefe cada 3 niveles
            # Vida base 20 y se duplica cada jefe (nivel 3, 6, 9, ...)
            boss_lives = 20 * (2 ** ((self.current_level // 3) - 1))
            boss_speed = 20 + 2 * ((self.current_level // 3) - 1)
            boss_bullet_speed = 4 + ((self.current_level // 3) - 1)
            boss_shoot_prob = 0.5 + 0.1 * ((self.current_level // 3) - 1)

            boss = FinalBoss(
                x=self.screen_width // 2 - 90,
                y=50,
                bullet_speed=boss_bullet_speed
            )
            boss.lives = boss_lives
            boss.speed = boss_speed
            boss.shoot_probability = boss_shoot_prob
            self.enemies.append(boss)
        else:
            spacing_x = self.screen_width // 7
            y_lvl1 = 80
            y_lvl2 = 140

            for i in range(3):
                enemy1 = BasicEnemy(
                    x=spacing_x * (i + 1),
                    y=y_lvl1,
                    bullet_speed=3 + 0.1 * (self.current_level - 1),
                    level=self.current_level
                )
                enemy1.lives = base_life_lvl1
                enemy1.speed = base_speed_lvl1
                enemy1.shoot_probability = base_shoot_prob_lvl1
                self.enemies.append(enemy1)

            for i in range(3):
                enemy2 = StrongEnemy(
                    x=spacing_x * (i + 1),
                    y=y_lvl2,
                    bullet_speed=3 + 0.1 * (self.current_level - 1),
                    level=self.current_level
                )
                enemy2.lives = base_life_lvl2
                enemy2.speed = base_speed_lvl2
                enemy2.shoot_probability = base_shoot_prob_lvl2
                self.enemies.append(enemy2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.delete_save()
                pygame.quit()
                sys.exit()
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused and not self.victory:
                    self.player.shoot()
                    if self.shoot_sound:
                        self.shoot_sound.play()
                if event.key == pygame.K_ESCAPE and not self.game_over and not self.victory:
                    if self.paused and self.pause_menu_state in ["options", "sound", "controls"]:
                        self.pause_menu_state = "main"
                    else:
                        self.paused = not self.paused
                        self.pause_menu_state = "main"
    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
    
                if self.paused and not self.game_over and not self.victory:
                    for i, btn_rect in enumerate(self.pause_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
    
                            if self.pause_menu_state == "main":
                                if i == 0:
                                    self.resume_game()
                                elif i == 1:
                                    self.show_options()
                                elif i == 2:
                                    self.go_to_menu()
                                elif i == 3:
                                    self.quit_game()
    
                            elif self.pause_menu_state == "options":
                                if i == 0:
                                    self.pause_menu_state = "controls"
                                elif i == 1:
                                    self.pause_menu_state = "sound"
                                elif i == 2:
                                    self.back_to_pause_main()
    
                            elif self.pause_menu_state == "sound":
                                if i == 0:
                                    self.muted = not self.muted
                                    if self.muted:
                                        pygame.mixer.music.set_volume(0)
                                        for s in [self.shoot_sound, self.damage_sound, self.death_sound, self.click_sound, self.hover_sound, self.destroyed_sound]:
                                            if s: s.set_volume(0)
                                    else:
                                        pygame.mixer.music.set_volume(self.volume_musica * self.volume_general)
                                        for s in [self.shoot_sound, self.damage_sound, self.death_sound, self.click_sound, self.hover_sound, self.destroyed_sound]:
                                            if s: s.set_volume(self.volume_efectos * self.volume_general)
                                elif i == 1:
                                    self.pause_menu_state = "options"
    
                            elif self.pause_menu_state == "controls":
                                # Sólo un botón "Volver" en controls
                                if i == 0:
                                    self.back_to_pause_main()
    
                    # Ajuste de volumen por clic en barras (verificación con hasattr)
                    if self.pause_menu_state == "sound":
                        x, y = mouse_pos
    
                        if hasattr(self, 'general_bar') and self.general_bar.collidepoint(x, y):
                            relative_x = x - self.general_bar.x
                            self.volume_general = max(0.0, min(1.0, relative_x / self.general_bar.width))
    
                        elif hasattr(self, 'music_bar') and self.music_bar.collidepoint(x, y):
                            relative_x = x - self.music_bar.x
                            self.volume_musica = max(0.0, min(1.0, relative_x / self.music_bar.width))
    
                        elif hasattr(self, 'effects_bar') and self.effects_bar.collidepoint(x, y):
                            relative_x = x - self.effects_bar.x
                            self.volume_efectos = max(0.0, min(1.0, relative_x / self.effects_bar.width))
    
                        if not self.muted:
                            pygame.mixer.music.set_volume(self.volume_musica * self.volume_general)
                            for s in [self.shoot_sound, self.damage_sound, self.death_sound, self.click_sound, self.hover_sound, self.destroyed_sound]:
                                if s: s.set_volume(self.volume_efectos * self.volume_general)
    
            elif event.type == pygame.MOUSEMOTION:
                if self.paused and self.pause_menu_state == "sound":
                    # Espacio para drag futuro si lo deseas
                    pass


    def update(self):
        if self.game_over or self.paused or self.victory:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left", self.screen_width)
        if keys[pygame.K_RIGHT]:
            self.player.move("right", self.screen_width)

        self.player.update(self.screen_height)

        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.enemy_move_timer = 0

            hit_edge = False
            for enemy in self.enemies:
                enemy.rect.x += enemy.speed * enemy.direction
                enemy.try_shoot()
                if enemy.rect.right >= self.screen_width or enemy.rect.left <= 0:
                    hit_edge = True

            if hit_edge:
                for enemy in self.enemies:
                    enemy.direction *= -1
                    enemy.rect.y += enemy.move_down_distance

        for enemy in self.enemies:
            enemy.update_bullets(self.screen_height)

        self.check_collisions()

        # Manejo de nubes en nivel 2
        if self.current_level == 2:
            self.cloud_spawn_timer += 1
            if self.cloud_spawn_timer >= self.cloud_spawn_interval:
                self.clouds.append(Cloud(self.screen_width, self.screen_height))
                self.cloud_spawn_timer = 0
            for cloud in self.clouds[:]:
                cloud.update()
                if cloud.is_offscreen(self.screen_height):
                    self.clouds.remove(cloud)
        else:
            self.clouds = []

        # Manejo de satélites en nivel 3 y superiores
        if self.current_level >= 3:
            self.satellite_spawn_timer += 1
            if self.satellite_spawn_timer >= self.next_satellite_spawn_interval:
                self.satellites.append(Satellite(self.screen_width, self.screen_height))
                self.satellite_spawn_timer = 0
                self.next_satellite_spawn_interval = random.randint(self.satellite_spawn_interval_min, self.satellite_spawn_interval_max)
            for satellite in self.satellites[:]:
                satellite.update()
                if satellite.is_offscreen(self.screen_width):
                    self.satellites.remove(satellite)
        else:
            self.satellites = []

        # Avanza nivel si no quedan enemigos
        if not self.enemies:
            self.current_level += 1
            print(f"¡Pasando al Nivel {self.current_level}!")
            self.save_progress()  # Guardar progreso

            self.load_level_background()
            self.create_enemies()  # Debe manejar la lógica de enemigos según nivel

            # Crear escudos a partir del nivel 2
            if self.current_level >= 2:
                self.create_shields()

            # Incrementar velocidad enemigos progresivamente
            for enemy in self.enemies:
                enemy.speed += self.enemy_speed_increase

            # Reproducir música según nivel
            self.play_level_music()

        # Verifica si enemigo toca al jugador para game over
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                self.delete_save()  # Borrar progreso al perder
                break

    def check_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.colliderect(enemy.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy in self.enemies:
                        enemy.receive_damage()
                        if enemy.dead:
                            self.enemies.remove(enemy)
                            self.score += 10
                        else:
                            self.score += 5
                    break

        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                for shield in self.shields:
                    if bullet.rect.colliderect(shield.rect):
                        enemy.bullets.remove(bullet)
                        shield.take_damage()
                        if shield.is_destroyed():
                            self.shields.remove(shield)
                            if self.destroyed_sound:
                                self.destroyed_sound.play()
                        break
                    
        # Colisión balas enemigas con jugador
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.rect.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    if self.damage_sound:
                        self.damage_sound.play()
                    if self.player.damage_timer == 0:
                        self.player.take_damage()
                        if self.player.lives <= 0:
                            if self.death_sound:
                                self.death_sound.play()
                            self.game_over = True
                            self.delete_save()
                    break

    def draw_button(self, text, x, y, w=250, h=60, 
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0), 
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)

        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        # Sonido de hover
        if hovered and text not in self.hovered_pause_buttons:
            self.hovered_pause_buttons.add(text)
            if self.hover_sound:
                self.hover_sound.play()
        elif not hovered:
            self.hovered_pause_buttons.discard(text)

        if hovered:
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, text_color)

        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, text_color)

        text_rect = rendered_text.get_rect(center=rect.center)
        self.screen.blit(rendered_text, text_rect)

        return rect

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSA", True, (255, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        if self.pause_menu_state == "main":
            continue_btn = self.draw_button("Continuar", self.screen_width // 2, 250, 250, 60)
            options_btn = self.draw_button("Opciones", self.screen_width // 2, 330, 250, 60)
            menu_btn = self.draw_button("Menú principal", self.screen_width // 2, 410, 250, 60)
            quit_btn = self.draw_button("Salir", self.screen_width // 2, 490, 250, 60)
            self.pause_buttons = [continue_btn, options_btn, menu_btn, quit_btn]

        elif self.pause_menu_state == "options":
            controls_btn = self.draw_button("Controles", self.screen_width // 2, 270, 250, 60)
            sound_btn = self.draw_button("Sonido", self.screen_width // 2, 350, 250, 60)
            back_btn = self.draw_button("Volver", self.screen_width // 2, 430, 250, 60)
            self.pause_buttons = [controls_btn, sound_btn, back_btn]

        elif self.pause_menu_state == "sound":
            overlay_height = 220
            sound_overlay = pygame.Surface((self.screen_width - 100, overlay_height))
            sound_overlay.set_alpha(220)
            sound_overlay.fill((30, 30, 30))
            overlay_rect = sound_overlay.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(sound_overlay, overlay_rect)

            title_surface = self.font.render("Ajustes de Sonido", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.screen_width // 2, overlay_rect.top + 30))
            self.screen.blit(title_surface, title_rect)

            # Volumen sliders
            slider_width = 200
            slider_height = 20
            spacing = 60
            base_x = overlay_rect.left + 50
            base_y = overlay_rect.top + 70

            # Volumen general
            self.draw_text("Volumen General", base_x, base_y, self.small_font)
            general_bar = pygame.Rect(base_x + 180, base_y - slider_height // 2, slider_width, slider_height)
            pygame.draw.rect(self.screen, (100, 100, 100), general_bar)
            pygame.draw.rect(self.screen, (0, 255, 0), (general_bar.x, general_bar.y, int(self.volume_general * slider_width), slider_height))
            general_knob_x = general_bar.x + int(self.volume_general * slider_width) - 5
            general_knob = pygame.Rect(general_knob_x, general_bar.y - 5, 10, slider_height + 10)
            pygame.draw.rect(self.screen, (255, 255, 255), general_knob)

            # Volumen música
            y_music = base_y + spacing
            self.draw_text("Volumen Música", base_x, y_music, self.small_font)
            music_bar = pygame.Rect(base_x + 180, y_music - slider_height // 2, slider_width, slider_height)
            pygame.draw.rect(self.screen, (100, 100, 100), music_bar)
            pygame.draw.rect(self.screen, (0, 255, 0), (music_bar.x, music_bar.y, int(self.volume_musica * slider_width), slider_height))
            music_knob_x = music_bar.x + int(self.volume_musica * slider_width) - 5
            music_knob = pygame.Rect(music_knob_x, music_bar.y - 5, 10, slider_height + 10)
            pygame.draw.rect(self.screen, (255, 255, 255), music_knob)

            # Volumen efectos
            y_effects = base_y + 2 * spacing
            self.draw_text("Volumen Efectos", base_x, y_effects, self.small_font)
            effects_bar = pygame.Rect(base_x + 180, y_effects - slider_height // 2, slider_width, slider_height)
            pygame.draw.rect(self.screen, (100, 100, 100), effects_bar)
            pygame.draw.rect(self.screen, (0, 255, 0), (effects_bar.x, effects_bar.y, int(self.volume_efectos * slider_width), slider_height))
            effects_knob_x = effects_bar.x + int(self.volume_efectos * slider_width) - 5
            effects_knob = pygame.Rect(effects_knob_x, effects_bar.y - 5, 10, slider_height + 10)
            pygame.draw.rect(self.screen, (255, 255, 255), effects_knob)

            # Botón mute
            mute_text = "Activar sonido" if self.muted else "Silenciar"
            mute_btn = self.draw_button(mute_text, self.screen_width // 2, overlay_rect.bottom + 40, 200, 40)

            # Botón volver
            back_btn = self.draw_button("Volver", self.screen_width // 2, overlay_rect.bottom + 100, 200, 40)

            # Guardar referencias
            self.pause_buttons = [mute_btn, back_btn]
            self.general_bar = general_bar
            self.general_knob = general_knob
            self.music_bar = music_bar
            self.music_knob = music_knob
            self.effects_bar = effects_bar
            self.effects_knob = effects_knob

        elif self.pause_menu_state == "controls":
            overlay_height = 280
            overlay = pygame.Surface((self.screen_width - 100, overlay_height))
            overlay.set_alpha(180)
            overlay.fill((30, 30, 30))
            overlay_rect = overlay.get_rect(center=(self.screen_width // 2, 350))
            self.screen.blit(overlay, overlay_rect)
        
            # Renderizamos el título y lo centramos horizontalmente
            title_surface = self.font.render("Controles del Juego", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.screen_width // 2, overlay_rect.top + 30))
            self.screen.blit(title_surface, title_rect)
        
            controls_list = [
                ("Flechas Izquierda/Derecha", "Mover jugador"),
                ("Barra Espaciadora", "Disparar"),
                ("Escape", "Pausar/Reanudar juego"),
            ]
        
            start_y = overlay_rect.top + 80
            line_spacing = 40
            for i, (key, action) in enumerate(controls_list):
                y = start_y + i * line_spacing
                key_text = self.small_font.render(key, True, (255, 255, 255))
                action_text = self.small_font.render(action, True, (200, 200, 200))
                self.screen.blit(key_text, (overlay_rect.left + 40, y))
                self.screen.blit(action_text, (overlay_rect.left + 320, y))
        
            # Botón volver centrado y guardado para eventos
            back_btn = self.draw_button("Volver", self.screen_width // 2, overlay_rect.bottom - 30, 200, 40)
            self.pause_buttons = [back_btn]



    def draw_text(self, text, x, y, font, color=(255, 255, 255)):
        rendered_text = font.render(text, True, color)
        text_rect = rendered_text.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(rendered_text, text_rect)

    def resume_game(self):
        self.paused = False

    def show_options(self):
        self.pause_menu_state = "options"

    def back_to_pause_main(self):
        self.pause_menu_state = "main"

    def go_to_menu(self):
        from .menu import Menu
        menu = Menu()
        menu.run()


    def quit_game(self):
        pygame.quit()
        sys.exit()

    def create_shields(self):
        self.shields = []
        shield_y = self.screen_height - 150
        spacing = self.screen_width // 4
        for i in range(3):
            shield_x = spacing * i + spacing // 2 - 30
            self.shields.append(Shield(shield_x, shield_y))

    def draw_game_over_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 180))

        restart_btn = self.draw_button("Reiniciar", self.screen_width // 2, 300)
        menu_btn = self.draw_button("Menú principal", self.screen_width // 2, 380)
        quit_btn = self.draw_button("Salir", self.screen_width // 2, 460)

        self.game_over_buttons = [restart_btn, menu_btn, quit_btn]

    def draw_victory_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("¡VICTORIA!", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        msg_text = self.font.render("¡Salvaste el planeta!", True, (255, 255, 255))
        self.screen.blit(msg_text, (self.screen_width // 2 - msg_text.get_width() // 2, 180))

        menu_btn = self.draw_button("Menú principal", self.screen_width // 2, 300)
        quit_btn = self.draw_button("Salir", self.screen_width // 2, 380)

        self.victory_buttons = [menu_btn, quit_btn]

    def draw(self):
        if self.level_background:
            self.screen.blit(self.level_background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        if self.current_level == 2:
            for cloud in self.clouds:
                cloud.draw(self.screen)

        if self.current_level == 3:
            for satellite in self.satellites:
                satellite.draw(self.screen)

        self.player.draw(self.screen)

        # Barra de vida para el jefe final en nivel 3
        for enemy in self.enemies:
            if isinstance(enemy, FinalBoss):
                health_bar_width = enemy.rect.width
                health_bar_height = 10
                health_ratio = max(enemy.lives / 15, 0)  # 15 es vida total del jefe
                pygame.draw.rect(self.screen, (255, 0, 0), (enemy.rect.x, enemy.rect.y - 15, health_bar_width, health_bar_height))
                health_bar = pygame.Rect(enemy.rect.x, enemy.rect.y - 15, int(health_bar_width * health_ratio), health_bar_height)
                pygame.draw.rect(self.screen, (0, 255, 0), health_bar)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, (255, 255, 0), bullet)

        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if hasattr(bullet, "draw"):
                    bullet.draw(self.screen)
                else:
                    pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

        for shield in self.shields:
            shield.draw(self.screen)

        if self.paused:
            self.draw_pause_menu()
        if self.game_over:
            self.draw_game_over_menu()
        if self.victory:
            self.draw_victory_menu()

    def save_progress(self):
        try:
            with open(self.save_path, 'w') as f:
                f.write(str(self.current_level))
            print(f"Progreso guardado: Nivel {self.current_level}")
        except Exception as e:
            print(f"Error guardando progreso: {e}")

    def delete_save(self):
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
                print("Progreso eliminado")
        except Exception as e:
            print(f"Error eliminando progreso: {e}")

    def update_volumes(self):
        # Actualiza volúmenes individuales y general
        vol_music = self.volume_general * self.volume_musica
        vol_effects = self.volume_general * self.volume_efectos

        pygame.mixer.music.set_volume(vol_music)

        if self.click_sound:
            self.click_sound.set_volume(vol_effects)
        if self.hover_sound:
            self.hover_sound.set_volume(vol_effects)
        if self.damage_sound:
            self.damage_sound.set_volume(vol_effects)
        if self.shoot_sound:
            self.shoot_sound.set_volume(vol_effects)
        if self.destroyed_sound:
            self.destroyed_sound.set_volume(vol_effects)
        if self.death_sound:
            self.death_sound.set_volume(vol_effects)

    def toggle_mute(self):
        if self.muted:
            # Restaurar valores anteriores
            self.volume_general = self.saved_volume_general
            self.volume_musica = self.saved_volume_musica
            self.volume_efectos = self.saved_volume_efectos
            self.muted = False
        else:
            # Guardar valores actuales antes de silenciar
            self.saved_volume_general = self.volume_general
            self.saved_volume_musica = self.volume_musica
            self.saved_volume_efectos = self.volume_efectos

            # Poner volúmenes en 0 visualmente
            self.volume_general = 0.0
            self.volume_musica = 0.0
            self.volume_efectos = 0.0
            self.muted = True
    
        # Aplicar cambios de volumen
        self.update_volumes()

    def run(self):
        # Mostrar cinemática de inicio solo si es nuevo juego
        if self.show_intro_cinematic:
            self.cinematics.show_intro()
            self.show_intro_cinematic = False
        
        # Bucle principal del juego
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            
            # Salir del bucle si el juego terminó
            if self.game_over or self.victory:
                break
        
        # Mostrar cinemática final ANTES de volver al menú
        if self.game_over:
            self.cinematics.show_ending(victory=False)  # Muestra cinematic_loser.png
            self.delete_save()
        elif self.victory:
            self.cinematics.show_ending(victory=True)  # Muestra cinematic_win.png
            self.delete_save()
        
        # Volver al menú principal DESPUÉS de mostrar la cinemática
        from .menu import Menu
        menu = Menu()
        menu.run()