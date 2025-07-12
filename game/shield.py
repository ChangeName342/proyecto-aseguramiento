import pygame

class Shield:
    def __init__(self, x, y, width=60, height=30, life=4):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_life = life
        self.life = life
        self.color = (255, 0, 0)

    def draw(self, screen):
        # Cambiar color según daño
        intensity = int(255 * (self.life / self.max_life))
        color = (intensity, intensity, 100)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)

    def take_damage(self):
        self.life -= 1

    def is_destroyed(self):
        return self.life <= 0
