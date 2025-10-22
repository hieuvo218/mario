import pygame
from pygame.locals import *
import sys


class Input:
    def __init__(self, entity):
        self.mouseX = 0
        self.mouseY = 0
        self.entity = entity

    def checkForInput(self):
        events = pygame.event.get()
        self.checkForKeyboardInput()
        self.checkForMouseInput(events)
        self.checkForQuitAndRestartInputEvents(events)

    def checkForKeyboardInput(self):
        pressedKeys = pygame.key.get_pressed()

        if pressedKeys[K_LEFT] or pressedKeys[K_h] and not pressedKeys[K_RIGHT]:
            self.entity.traits["goTrait"].direction = -1
        elif pressedKeys[K_RIGHT] or pressedKeys[K_l] and not pressedKeys[K_LEFT]:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0

        isJumping = pressedKeys[K_SPACE] or pressedKeys[K_UP] or pressedKeys[K_k]
        self.entity.traits['jumpTrait'].jump(isJumping)

        self.entity.traits['goTrait'].boost = pressedKeys[K_LSHIFT]

    def checkForMouseInput(self, events):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.isRightMouseButtonPressed(events):
            self.entity.levelObj.addKoopa(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addGoomba(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addRedMushroom(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
        if self.isLeftMouseButtonPressed(events):
            self.entity.levelObj.addCoin(
                mouseX / 32 - self.entity.camera.pos.x, mouseY / 32
            )

    def checkForQuitAndRestartInputEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()
            # Debug: F2 teleport to boss (if present)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                # find boss in level
                boss = None
                for ent in self.entity.levelObj.entityList:
                    if ent.__class__.__name__ == 'Boss':
                        boss = ent
                        break
                if boss:
                    # place mario near boss
                    try:
                        self.entity.rect.x = boss.rect.x - 100
                        self.entity.rect.y = boss.rect.y
                    except Exception:
                        pass
            # Debug: F3 load boss level and teleport Mario there
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                try:
                    self.entity.levelObj.loadLevel('Level1-boss')
                    print('Loaded Level1-boss via F3')
                    # find boss spawn in level objects
                    # find boss entity in the loaded level and teleport Mario near it
                    boss = None
                    for ent in self.entity.levelObj.entityList:
                        if ent.__class__.__name__ == 'Boss':
                            boss = ent
                            break
                    if boss:
                        # place mario a bit to the left of boss and on top of the tile
                        try:
                            self.entity.rect.x = boss.rect.x - 100
                            # place Mario above boss's y so he's not embedded inside a tile
                            self.entity.rect.y = boss.rect.y - self.entity.rect.height - 1
                            # reset velocities and ensure Mario is not stuck inside tiles
                            try:
                                self.entity.vel.x = 0
                                self.entity.vel.y = 0
                                # run a collision check to snap Mario onto nearest ground tile
                                self.entity.collision.checkY()
                                self.entity.invincibilityFrames = 60
                            except Exception:
                                pass
                        except Exception:
                            # fallback to center of boss tile
                            self.entity.rect.x = boss.rect.x
                            self.entity.rect.y = boss.rect.y
                    else:
                        # fallback: teleport mario to tile 12,10 (narrow boss map default)
                        self.entity.rect.x = 12 * 32 - 100
                        self.entity.rect.y = 10 * 32
                except Exception as e:
                    print('Failed to load boss level via F3:', e)

    def isLeftMouseButtonPressed(self, events):
        return self.checkMouse(events, 1)

    def isRightMouseButtonPressed(self, events):
        return self.checkMouse(events, 3)

    def checkMouse(self, events, button):
        for e in events:
            if e.type == pygame.MOUSEBUTTONUP and e.button == button:
                return True
        return False
