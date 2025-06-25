import pygame
import sys
import os
import gif_pygame
from .game import Game

class Menu:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Menú Principal - Invasión Espacial")

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gif_path = os.path.join(BASE_DIR, 'images', 'fondo_menu.gif')
        self.background_gif = gif_pygame.load(gif_path)
        self.title = pygame.image.load(os.path.join(BASE_DIR, 'images', 'titulo.png')).convert_alpha()

        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 30)

        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.volume = 0.5
        self.muted = False
        self.saved_volume = 0.5  # Para restaurar después del mute

        # Música de fondo
        try:
            pygame.mixer.init()
            music_path = os.path.join(BASE_DIR, 'sounds', 'menu_principal.mp3')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error al cargar la música del menú: {e}")

        # Sonido al pasar el mouse por botones
        try:
            hover_sound_path = os.path.join(BASE_DIR, 'sounds', 'seleccionar_menu.mp3')
            self.hover_sound = pygame.mixer.Sound(hover_sound_path)
            self.hover_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de selección de menú: {e}")
            self.hover_sound = None

        # Sonido al hacer clic en un botón
        try:
            click_sound_path = os.path.join(BASE_DIR, 'sounds', 'eleccion_menu.mp3')
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            self.click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de elección de menú: {e}")
            self.click_sound = None

        self.hovered_buttons = set()  # Para evitar repetir sonido
        self.slider_rect = pygame.Rect(300, 300, 200, 20)  # Rectángulo para el control deslizante
        self.slider_knob = pygame.Rect(300 + int(self.volume * 200), 295, 10, 30)  # Control deslizante
        self.dragging = False  # Para controlar si se está arrastrando el control deslizante

        self.saved_level = self.load_progress()

    def load_progress(self):
        """Carga el progreso guardado del juego desde un archivo."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_path = os.path.join(base_path, 'savegame.txt')
        
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    level = int(f.read())
                    if 1 <= level <= 3:
                        return level
            except Exception as e:
                print(f"Error al leer el archivo de guardado: {e}")
                return None
        return None

    def draw_button(self, text, x, y, font, mouse_pos, w=250, h=60,
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0),
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)
        hovered = rect.collidepoint(mouse_pos)

        # Reproducir sonido al pasar por primera vez
        if hovered and text not in self.hovered_buttons:
            self.hovered_buttons.add(text)
            if self.hover_sound:
                self.hover_sound.play()
        elif not hovered:
            self.hovered_buttons.discard(text)

        if hovered:
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = font.render(text, True, text_color)

        text_rect = rendered_text.get_rect(center=rect.center)
        self.screen.blit(rendered_text, text_rect)
        return rect

    def draw_text(self, text, x, y, font, color=(255, 255, 255)):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        frame_surface = self.background_gif.blit_ready()
        frame_surface = pygame.transform.scale(frame_surface, (self.screen_width, self.screen_height))
        self.screen.blit(frame_surface, (0, 0))
        
        if self.state != "sound":
            self.screen.blit(self.title, (self.screen_width // 2 - self.title.get_width() // 2, 80))

        mouse_pos = pygame.mouse.get_pos()
        buttons = []

        if self.state == "menu":
            if self.saved_level is not None:
                continue_button = self.draw_button("Continuar", 400, 240, self.font, mouse_pos)
                buttons.append(continue_button)
                y_start = 320
            else:
                y_start = 260

            play_button = self.draw_button("Iniciar Juego", 400, y_start, self.font, mouse_pos)
            options_button = self.draw_button("Opciones", 400, y_start + 80, self.font, mouse_pos)
            quit_button = self.draw_button("Salir", 400, y_start + 160, self.font, mouse_pos)
            buttons.extend([play_button, options_button, quit_button])
            return buttons

        elif self.state == "options":
            self.draw_text("Opciones", 400, 180, self.font)
            sound_button = self.draw_button("Sonido", 400, 260, self.small_font, mouse_pos, w=200, h=50)
            controls_button = self.draw_button("Controles", 400, 330, self.small_font, mouse_pos, w=200, h=50)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return sound_button, controls_button, back_button

        elif self.state == "sound":
            # Dibujar controles de volumen
            self.draw_text("Ajustes de Sonido", 400, 180, self.font)
            
            # Barra del control deslizante
            pygame.draw.rect(self.screen, (100, 100, 100), self.slider_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), 
                           (self.slider_rect.x, self.slider_rect.y, 
                            int(self.volume * self.slider_rect.width), 
                            self.slider_rect.height))
            
            # Control deslizante
            pygame.draw.rect(self.screen, (255, 255, 255), self.slider_knob)
            
            # Texto del volumen
            self.draw_text(f"Volumen: {int(self.volume * 100)}%", 400, 250, self.small_font)
            
            # Botón de mute
            mute_text = "Activar sonido" if self.muted else "Silenciar"
            mute_button = self.draw_button(mute_text, 400, 350, self.small_font, mouse_pos, w=200, h=50)
            
            # Botón de volver
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            
            return mute_button, back_button

        elif self.state == "controls":
            self.draw_text("Controles (pendiente)", 400, 250, self.small_font)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return (back_button,)

    def toggle_mute(self):
        if self.muted:
            # Restaurar volumen
            self.volume = self.saved_volume
            self.muted = False
        else:
            # Guardar volumen actual y silenciar
            self.saved_volume = self.volume
            self.volume = 0
            self.muted = True
        self.update_volume()

    def update_volume(self):
        pygame.mixer.music.set_volume(self.volume)
        if self.hover_sound:
            self.hover_sound.set_volume(self.volume * 0.5)
        if self.click_sound:
            self.click_sound.set_volume(self.volume * 0.5)
        self.slider_knob.x = self.slider_rect.x + int(self.volume * self.slider_rect.width) - 5

    def run(self):
        while True:
            self.clock.tick(60)
            buttons = self.draw_menu()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    button_offset = 1 if self.saved_level is not None else 0
                
                    if self.state == "menu":
                        if self.saved_level is not None and buttons[0].collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
                            pygame.mixer.music.stop()
                            game = Game()  # Usa la clase ya importada
                            game.current_level = self.saved_level
                            game.load_level_background()
                            game.create_enemies()
                            if self.saved_level in [2, 3]:
                                game.create_shields()
                            game.run()
                            continue
                        
                        if buttons[button_offset].collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
                            pygame.mixer.music.stop()
                            game = Game()  # Usa la clase ya importada
                            game.run()
                        elif buttons[button_offset + 1].collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
                            self.state = "options"
                        elif buttons[button_offset + 2].collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
                            pygame.quit()
                            sys.exit()
                
                    elif self.state == "options":
                        if buttons[0].collidepoint(mouse_pos):
                            self.state = "sound"
                        elif buttons[1].collidepoint(mouse_pos):
                            self.state = "controls"
                        elif buttons[2].collidepoint(mouse_pos):
                            self.state = "menu"

                    elif self.state == "sound":
                        if buttons[0].collidepoint(mouse_pos):  # Botón de mute
                            if self.click_sound:
                                self.click_sound.play()
                            self.toggle_mute()
                        elif buttons[1].collidepoint(mouse_pos):  # Botón de volver
                            self.state = "options"
                        
                        # Verificar si se hizo clic en el control deslizante
                        if self.slider_knob.collidepoint(mouse_pos):
                            self.dragging = True
                        elif self.slider_rect.collidepoint(mouse_pos):
                            # Calcular el volumen basado en la posición del clic
                            self.volume = (mouse_pos[0] - self.slider_rect.x) / self.slider_rect.width
                            self.volume = max(0, min(1, self.volume))
                            self.update_volume()

                    elif self.state == "controls":
                        if buttons[0].collidepoint(mouse_pos):
                            self.state = "options"

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = False

                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    # Actualizar volumen mientras se arrastra el control deslizante
                    mouse_pos = pygame.mouse.get_pos()
                    self.volume = (mouse_pos[0] - self.slider_rect.x) / self.slider_rect.width
                    self.volume = max(0, min(1, self.volume))
                    self.update_volume()
                    self.slider_knob.x = self.slider_rect.x + int(self.volume * self.slider_rect.width) - 5