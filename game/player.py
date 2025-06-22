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

class Player:
    def __init__(self, x, y):
        images_dir = resource_path('images')
        sounds_dir = resource_path('sounds')

        # Cargar imagen
        try:
            image_path = os.path.join(images_dir, 'nave.png')
            print(f"Intentando cargar imagen desde: {image_path}")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.image = pygame.Surface((50, 40))
            self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 5
        self.lives = 5

        self.bullets = []
        self.bullet_speed = 7
        self.cooldown = 0

        # Animación daño
        self.damage_timer = 0
        self.damage_duration = 15

        # Cargar sonidos
        def load_sound(filename, volume):
            try:
                path = os.path.join(sounds_dir, filename)
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                return sound
            except Exception as e:
                print(f"Error cargando sonido {filename}: {e}")
                return None

        self.shoot_sound = load_sound('disparo_protagonista.mp3', 0.3)
        self.damage_sound = load_sound('daño_recibido_prota.mp3', 0.5)
        self.death_sound = load_sound('sonido_muerte_prota.mp3', 0.7)

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
            if self.shoot_sound:
                self.shoot_sound.play()

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
        self.lives -= 1
        self.damage_timer = self.damage_duration
        if self.damage_sound:
            self.damage_sound.play()
        if self.lives <= 0:
            if self.death_sound:
                self.death_sound.play()

    def draw(self, screen):
        if self.damage_timer > 0:
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




