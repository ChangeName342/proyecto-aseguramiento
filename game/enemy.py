import pygame
import random
import os

class Enemy:
    def __init__(self, x, y, bullet_speed=3, lives=1, image_name='cat.png'):
        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, '..', 'images', image_name)
            image_path = os.path.abspath(image_path)

            print(f"Intentando cargar imagen del enemigo desde: {image_path}")
            self.image_original = pygame.image.load(image_path).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (90, 80))
        except Exception as e:
            print(f"Error cargando imagen del enemigo: {e}")
            self.image_original = pygame.Surface((90, 80))
            self.image_original.fill((255, 0, 0))

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.direction = 1
        self.move_down_distance = 20
        self.bullets = []
        self.bullet_speed = bullet_speed
        self.lives = lives
        self.dead = False
        
        # Agregamos valor por defecto para evitar errores en try_shoot
        self.shoot_probability = 0

    def update(self, screen_width):
        if self.dead:
            return False

        self.rect.x += self.speed * self.direction

        if self.rect.right >= screen_width or self.rect.left <= 0:
            return True
        return False

    def move_down(self):
        if not self.dead:
            self.rect.y += self.move_down_distance

    def try_shoot(self):
        if not self.dead:
            # Debug para ver si se llama y cuál es la probabilidad
            # print(f"Enemy en ({self.rect.x}, {self.rect.y}) intentando disparar con probabilidad {self.shoot_probability:.4f}")
            if random.random() < self.shoot_probability:
                bullet = pygame.Rect(self.rect.centerx - 2, self.rect.bottom, 4, 10)
                self.bullets.append(bullet)

    def update_bullets(self, screen_height):
        for bullet in self.bullets[:]:
            bullet.y += self.bullet_speed
            if bullet.top > screen_height:
                self.bullets.remove(bullet)

    def draw(self, screen):
        if not self.dead:
            screen.blit(self.image, self.rect)

        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 100, 100), bullet)

    def receive_damage(self):
        if self.dead:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
            self.bullets.clear()


class BasicEnemy(Enemy):
    def __init__(self, x, y, bullet_speed=3, level=1):
        super().__init__(x, y, bullet_speed=bullet_speed, lives=1, image_name='cat.png')
        # Probabilidad aumentada exponencial para que se note diferencia entre niveles
        self.shoot_probability = 0.06 * (3 ** (level - 1))


class StrongEnemy(Enemy):
    def __init__(self, x, y, bullet_speed=3, level=1):
        super().__init__(x, y, bullet_speed=bullet_speed, lives=2, image_name='ship.png')
        # Probabilidad más alta que BasicEnemy para que se note
        self.shoot_probability = 0.12 * (3 ** (level - 1))