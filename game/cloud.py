import pygame
import os
import random
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Carpeta temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Cloud:
    def __init__(self, screen_width, screen_height):
        cloud_images_paths = [
            resource_path(os.path.join('images', 'nube1.png')),
            resource_path(os.path.join('images', 'nube2.png')),
        ]

        selected_image_path = random.choice(cloud_images_paths)

        try:
            self.image = pygame.image.load(selected_image_path).convert_alpha()
            self.image = pygame.transform.scale(
                self.image,
                (random.randint(100, 200), random.randint(50, 100))
            )
        except Exception as e:
            print(f"Error cargando imagen de nube: {selected_image_path} - {e}")
            self.image = pygame.Surface((150, 75))
            self.image.fill((200, 200, 200))  # Fallback gris

        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-self.rect.height, -20)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_offscreen(self, screen_height):
        return self.rect.top > screen_height

