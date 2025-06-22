import pygame
import os
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, útil para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Shield:
    def __init__(self, x, y, width=60, height=30, life=4):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_life = life
        self.life = life
        self.color = (255, 0, 0)

        # Cargar sonido estructura destruida
        try:
            sonido_path = resource_path(os.path.join('sounds', 'estructura_destruida.mp3'))
            self.destroy_sound = pygame.mixer.Sound(sonido_path)
            self.destroy_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de estructura destruida: {e}")
            self.destroy_sound = None

    def draw(self, screen):
        # Cambiar color según daño
        intensity = int(255 * (self.life / self.max_life))
        color = (intensity, intensity, 100)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)

    def take_damage(self):
        self.life -= 1
        if self.life <= 0:
            if self.destroy_sound:
                self.destroy_sound.play()

    def is_destroyed(self):
        return self.life <= 0
