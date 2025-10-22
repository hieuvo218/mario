import pygame

from entities.EntityBase import EntityBase
from classes.Maths import Vec2D


class BossFire(EntityBase):
    def __init__(self, screen, spriteColl, x, y, vx, vy, level, sound):
        super(BossFire, self).__init__(x, y, 0)
        self.screen = screen
        self.spriteCollection = spriteColl
        self.levelObj = level
        self.sound = sound
        self.type = "Projectile"
        # velocity components (pixels per frame)
        self.vx = vx
        self.vy = vy
        # make projectile larger for visibility (centered on tile)
        self.rect = pygame.Rect(x * 32 + 8, y * 32 + 8, 16, 16)
        self.timer = 0
        print(f"BossFire instantiated at tile ({x},{y}) vx={vx:.2f} vy={vy:.2f}")

    def update(self, camera):
        # move by velocity vector
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.timer += 1
        # remove after some time
        if self.timer > 300:
            self.alive = None
            return
        # check collision with level tiles (solid ground)
        # get the tile indices the projectile currently overlaps
        try:
            left_tile = self.rect.left // 32
            right_tile = self.rect.right // 32
            top_tile = self.rect.top // 32
            bottom_tile = self.rect.bottom // 32
            # check tiles under/around projectile
            # if any of the tiles the projectile occupies have a rect (solid), remove projectile
            for ty in range(top_tile, bottom_tile + 1):
                for tx in range(left_tile, right_tile + 1):
                    try:
                        tile = self.levelObj.level[ty][tx]
                        if tile is not None and tile.rect is not None:
                            # hit a solid tile
                            print(f"BossFire hit tile at {tx},{ty}")
                            self.alive = None
                            return
                    except IndexError:
                        # outside level bounds
                        continue
        except Exception:
            pass
        # check collision with player
        for ent in self.levelObj.entityList:
            if ent.__class__.__name__ == 'Mario':
                if self.rect.colliderect(ent.rect):
                    # apply damage to Mario (use existing collision handling in Mario if needed)
                    ent.invincibilityFrames = 60
                    # remove projectile
                    self.alive = None
                    return
        # draw a glowing projectile (two concentric circles)
        try:
            center_x = int(self.rect.x + self.rect.width / 2 + camera.x)
            center_y = int(self.rect.y + self.rect.height / 2)
            # outer glow
            pygame.draw.circle(self.screen, (255, 180, 50), (center_x, center_y), 10)
            # inner core
            pygame.draw.circle(self.screen, (255, 80, 0), (center_x, center_y), 5)
        except Exception:
            pass
