import pygame
import sys
import os
import gif_pygame

class Menu:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Menú Principal - Invasión Espacial")

        # Ruta base para cargar recursos (GIF y título)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gif_path = os.path.join(BASE_DIR, 'images', 'fondo_menu.gif')
        self.background_gif = gif_pygame.load(gif_path)
        self.title = pygame.image.load(os.path.join(BASE_DIR, 'images', 'titulo.png')).convert_alpha()

        # Fuentes para textos y botones
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 30)

        self.clock = pygame.time.Clock()

        # Estado actual del menú ("menu", "options", "sound", "controls")
        self.state = "menu"

        # Control de volumen (pendiente implementación)
        self.volume = 0.5
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)

        # Cargar progreso guardado (nivel)
        self.saved_level = self.load_progress()

    def load_progress(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_path = os.path.join(base_path, 'savegame.txt')
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    level = int(f.read())
                    if 1 <= level <= 3:
                        return level
            except Exception:
                pass
        return None

    def draw_button(self, text, x, y, font, mouse_pos, w=250, h=60,
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0),
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        """Dibuja un botón con efecto hover y retorna su rect para detectar clics."""
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)

        if rect.collidepoint(mouse_pos):
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
        """Dibuja texto centrado en la pantalla."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        """Dibuja el fondo animado y los botones según el estado actual."""
        # Fondo animado GIF escalado a la ventana
        frame_surface = self.background_gif.blit_ready()
        frame_surface = pygame.transform.scale(frame_surface, (self.screen_width, self.screen_height))
        self.screen.blit(frame_surface, (0, 0))

        # Título centrado horizontalmente
        self.screen.blit(self.title, (self.screen_width // 2 - self.title.get_width() // 2, 80))

        mouse_pos = pygame.mouse.get_pos()

        if self.state == "menu":
            buttons = []

            # Si hay progreso guardado, dibujar botón "Continuar"
            if self.saved_level is not None:
                continue_button = self.draw_button("Continuar", 400, 220, self.font, mouse_pos)
                buttons.append(('continuar', continue_button))

            # Ajustar posiciones de otros botones
            y_start = 300 if self.saved_level is not None else 260
            play_button = self.draw_button("Iniciar Juego", 400, y_start, self.font, mouse_pos)
            options_button = self.draw_button("Opciones", 400, y_start + 80, self.font, mouse_pos)
            quit_button = self.draw_button("Salir", 400, y_start + 160, self.font, mouse_pos)

            buttons.extend([
                ('iniciar', play_button),
                ('opciones', options_button),
                ('salir', quit_button)
            ])

            return buttons

        elif self.state == "options":
            self.draw_text("Opciones", 400, 180, self.font)
            sound_button = self.draw_button("Sonido", 400, 260, self.small_font, mouse_pos, w=200, h=50)
            controls_button = self.draw_button("Controles", 400, 330, self.small_font, mouse_pos, w=200, h=50)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return [('sonido', sound_button), ('controles', controls_button), ('volver', back_button)]

        elif self.state == "sound":
            self.draw_text("Ajustes de Sonido (pendiente)", 400, 250, self.small_font)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return [('volver', back_button)]

        elif self.state == "controls":
            self.draw_text("Controles (pendiente)", 400, 250, self.small_font)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return [('volver', back_button)]

    def run(self):
        """Bucle principal del menú que maneja eventos y cambia de estado."""
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

                    if self.state == "menu":
                        for name, btn_rect in buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                if name == 'continuar':
                                    from game import Game
                                    game = Game()
                                    game.current_level = self.saved_level
                                    game.load_level_background()
                                    game.create_enemies()
                                    if self.saved_level in [2, 3]:
                                        game.create_shields()
                                    game.run()
                                elif name == 'iniciar':
                                    from game import Game
                                    game = Game()
                                    game.run()
                                elif name == 'opciones':
                                    self.state = "options"
                                elif name == 'salir':
                                    pygame.quit()
                                    sys.exit()

                    elif self.state == "options":
                        for name, btn_rect in buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                if name == 'sonido':
                                    self.state = "sound"
                                elif name == 'controles':
                                    self.state = "controls"
                                elif name == 'volver':
                                    self.state = "menu"

                    elif self.state in ("sound", "controls"):
                        for name, btn_rect in buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                if name == 'volver':
                                    self.state = "options"



