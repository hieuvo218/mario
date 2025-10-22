import pygame
import random

from entities.EntityBase import EntityBase
from entities.BossFire import BossFire


class Boss(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level, sound):
        super(Boss, self).__init__(x, y, 0)
        self.screen = screen
        self.spriteCollection = spriteColl
        self.levelObj = level
        self.sound = sound
        self.type = "Mob"
        self.timer = 0
        self.fireCooldown = 10  # frames between fires (very small for quick visual testing)
        self.health = 5
        print(f"Boss instantiated at tile ({x},{y})")

    def update(self, camera):
        if not self.alive:
            return
        self.timer += 1
        # attempt to fire periodically
        if self.timer >= self.fireCooldown:
            self.fireAtPlayer()
            self.timer = 0
        # draw boss as a simple rectangle for now
        try:
            pygame.draw.rect(
                self.screen,
                (150, 0, 150),
                (self.rect.x + camera.x, self.rect.y, self.rect.width, self.rect.height),
            )
        except Exception:
            pass

    def fireAtPlayer(self):
        # find mario and fire in his direction
        mario = getattr(self.levelObj, 'player', None)
        if mario is None:
            for ent in self.levelObj.entityList:
                if ent.__class__.__name__ == 'Mario':
                    mario = ent
                    break
        if mario is None:
            return
        # compute a velocity vector aimed at Mario's center
        mx, my = mario.rect.center
        bx, by = self.rect.center
        dx = mx - bx
        dy = my - by
        import math
        dist = math.hypot(dx, dy)
        if dist == 0:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = dx / dist, dy / dist
        speed = 6.0
        vx, vy = ux * speed, uy * speed
        # spawn projectile at boss center tile coordinates (convert to tile indices)
        tx = (self.rect.x // 32)
        ty = (self.rect.y // 32)
        proj = BossFire(self.screen, self.spriteCollection, tx, ty, vx, vy, self.levelObj, self.sound)
        self.levelObj.entityList.append(proj)
        print(f"Boss fired projectile vx={vx:.2f}, vy={vy:.2f} from tile ({tx},{ty})")
