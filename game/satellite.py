import pygame
import os
import random
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, útil para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Satellite:
    def __init__(self, screen_width, screen_height):
        images_dir = resource_path('images')
        image_path = os.path.join(images_dir, 'satelite1.png')

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(
                self.image,
                (random.randint(60, 100), random.randint(40, 70))
            )
            if random.random() < 0.5:
                self.image = pygame.transform.flip(self.image, True, False)
        except Exception as e:
            print(f"Error cargando imagen de satélite: {image_path} - {e}")
            self.image = pygame.Surface((80, 50))
            self.image.fill((150, 150, 150))

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-self.rect.width, -20)
        self.rect.y = random.randint(50, screen_height // 2 - self.rect.height)

        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_offscreen(self, screen_width):
        return self.rect.left > screen_width

