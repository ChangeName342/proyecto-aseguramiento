import pygame
import os

class Player:
    def __init__(self, x, y):
        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, '..', 'images', 'nave.png')
            image_path = os.path.abspath(image_path)

            print(f"Intentando cargar imagen desde: {image_path}")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.image = pygame.Surface((50, 40))
            self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 5
        self.lives = 5  # aumentadas vidas

        self.bullets = []
        self.bullet_speed = 7
        self.cooldown = 0

        # Para animación de daño
        self.damage_timer = 0  # cuenta frames para animación daño
        self.damage_duration = 15  # duración animación en frames (~0.25 seg si 60fps)

    def move(self, direction, screen_width):
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == "right" and self.rect.right < screen_width:
            self.rect.x += self.speed

    def shoot(self):
        if self.cooldown == 0:
            bullet = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 10)
            self.bullets.append(bullet)
            self.cooldown = 20

    def update(self, screen_height):
        for bullet in self.bullets[:]:
            bullet.y -= self.bullet_speed
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.damage_timer > 0:
            self.damage_timer -= 1

    def take_damage(self):
        """Llamar cuando el jugador recibe daño."""
        self.lives -= 1
        self.damage_timer = self.damage_duration  # activar animación daño

    def draw(self, screen):
        # Si está en daño, dibujar con tintado rojo y parpadeo simple
        if self.damage_timer > 0:
            # Parpadeo: solo dibuja si damage_timer es par
            if self.damage_timer % 2 == 0:
                tint_surf = self.image.copy()
                tint_surf.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tint_surf, self.rect)
        else:
            screen.blit(self.image, self.rect)

        for bullet in self.bullets:
            glow_surface = pygame.Surface((12, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, (180, 0, 180, 120), glow_surface.get_rect())
            screen.blit(glow_surface, (bullet.centerx - 6, bullet.centery - 12))
            pygame.draw.rect(screen, (255, 0, 255), bullet)
            pygame.draw.rect(screen, (255, 255, 255), bullet, 1)
       
        



