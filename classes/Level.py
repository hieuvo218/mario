import json
import pygame

from classes.Sprites import Sprites
from classes.Tile import Tile
from entities.Coin import Coin
from entities.CoinBrick import CoinBrick
from entities.Goomba import Goomba
from entities.Mushroom import RedMushroom
from entities.Koopa import Koopa
from entities.CoinBox import CoinBox
from entities.RandomBox import RandomBox


class Level:
    def __init__(self, screen, sound, dashboard):
        self.sprites = Sprites()
        self.dashboard = dashboard
        self.sound = sound
        self.screen = screen
        self.level = None
        self.levelLength = 0
        self.entityList = []

    def loadLevel(self, levelname):
        print(f"Loading level: {levelname}")
        # reset current level state so reloading doesn't duplicate entities
        self.entityList = []
        self.level = None
        self.levelLength = 0
        print("Level state reset: cleared entityList and level data")
        with open("./levels/{}.json".format(levelname)) as jsonData:
            data = json.load(jsonData)
            self.loadLayers(data)
            self.loadObjects(data)
            self.loadEntities(data)
            self.levelLength = data["length"]

    def loadEntities(self, data):
        # Defensive handling when 'entities' or 'objects' keys are missing
        entities = data.get("level", {}).get("entities", {}) or {}
        print("loadEntities: entity keys:", list(entities.keys()))

        # Add entity types if present
        for x, y in entities.get("CoinBox", []):
            self.addCoinBox(x, y)
        for x, y in entities.get("Goomba", []):
            self.addGoomba(x, y)
        for x, y in entities.get("Koopa", []):
            self.addKoopa(x, y)
        for x, y in entities.get("coin", []):
            self.addCoin(x, y)
        for x, y in entities.get("coinBrick", []):
            self.addCoinBrick(x, y)
        for item_entry in entities.get("RandomBox", []):
            # RandomBox entries may include an item value
            if len(item_entry) >= 3:
                x, y, item = item_entry[0], item_entry[1], item_entry[2]
                self.addRandomBox(x, y, item)

        # boss spawn (optional) lives under objects
        objects = data.get("level", {}).get("objects", {}) or {}
        print("loadEntities: object keys:", list(objects.keys()))
        boss_spawns = objects.get("boss_spawn", [])
        if boss_spawns:
            print(f"Found boss_spawn entries: {boss_spawns}")
        for x, y in boss_spawns:
            print(f"Adding boss at {x},{y}")
            self.addBoss(x, y)

    def addBoss(self, x, y):
        try:
            from entities.Boss import Boss

            b = Boss(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
            self.entityList.append(b)
        except Exception:
            return

    def loadLayers(self, data):
        layers = []
        for x in range(*data["level"]["layers"]["sky"]["x"]):
            layers.append(
                (
                        [
                            Tile(self.sprites.spriteCollection.get("sky"), None)
                            for y in range(*data["level"]["layers"]["sky"]["y"])
                        ]
                        + [
                            Tile(
                                self.sprites.spriteCollection.get("ground"),
                                pygame.Rect(x * 32, (y - 1) * 32, 32, 32),
                            )
                            for y in range(*data["level"]["layers"]["ground"]["y"])
                        ]
                )
            )
        self.level = list(map(list, zip(*layers)))

    def loadObjects(self, data):
        for x, y in data["level"]["objects"].get("bush", []):
            self.addBushSprite(x, y)
        for x, y in data["level"]["objects"].get("cloud", []):
            self.addCloudSprite(x, y)
        for x, y, z in data["level"]["objects"].get("pipe", []):
            self.addPipeSprite(x, y, z)
        for x, y in data["level"]["objects"].get("sky", []):
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("sky"), None)
        for x, y in data["level"]["objects"].get("ground", []):
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("ground"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )

    def updateEntities(self, cam):
        for entity in self.entityList:
            entity.update(cam)
            if entity.alive is None:
                self.entityList.remove(entity)

    def drawLevel(self, camera):
        try:
            for y in range(0, 15):
                for x in range(0 - int(camera.pos.x + 1), 20 - int(camera.pos.x - 1)):
                    if self.level[y][x].sprite is not None:
                        if self.level[y][x].sprite.redrawBackground:
                            self.screen.blit(
                                self.sprites.spriteCollection.get("sky").image,
                                ((x + camera.pos.x) * 32, y * 32),
                            )
                        self.level[y][x].sprite.drawSprite(
                            x + camera.pos.x, y, self.screen
                        )
            self.updateEntities(camera)
            # Debug: draw projectile markers for visibility (small circles at projectile screen x)
            try:
                proj_count = 0
                for ent in self.entityList:
                    if ent.__class__.__name__ == 'BossFire':
                        proj_count += 1
                        try:
                            px = int(ent.rect.x + camera.x)
                            py = 16
                            pygame.draw.circle(self.screen, (255, 240, 50), (px, py), 5)
                        except Exception:
                            pass
                # draw projectile count using dashboard if available
                try:
                    self.dashboard.drawText(f"Bullets: {proj_count}", 10, 16, 8)
                except Exception:
                    pass
            except Exception:
                pass
        except IndexError:
            return

    def addCloudSprite(self, x, y):
        try:
            for yOff in range(0, 2):
                for xOff in range(0, 3):
                    self.level[y + yOff][x + xOff] = Tile(
                        self.sprites.spriteCollection.get("cloud{}_{}".format(yOff + 1, xOff + 1)), None, )
        except IndexError:
            return

    def addPipeSprite(self, x, y, length=2):
        try:
            # add pipe head
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("pipeL"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("pipeR"),
                pygame.Rect((x + 1) * 32, y * 32, 32, 32),
            )
            # add pipe body
            for i in range(1, length + 20):
                self.level[y + i][x] = Tile(
                    self.sprites.spriteCollection.get("pipe2L"),
                    pygame.Rect(x * 32, (y + i) * 32, 32, 32),
                )
                self.level[y + i][x + 1] = Tile(
                    self.sprites.spriteCollection.get("pipe2R"),
                    pygame.Rect((x + 1) * 32, (y + i) * 32, 32, 32),
                )
        except IndexError:
            return

    def addBushSprite(self, x, y):
        try:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("bush_1"), None)
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("bush_2"), None
            )
            self.level[y][x + 2] = Tile(
                self.sprites.spriteCollection.get("bush_3"), None
            )
        except IndexError:
            return

    def addCoinBox(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard,
            )
        )

    def addRandomBox(self, x, y, item):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            RandomBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                item,
                self.sound,
                self.dashboard,
                self
            )
        )

    def addCoin(self, x, y):
        self.entityList.append(Coin(self.screen, self.sprites.spriteCollection, x, y))

    def addCoinBrick(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBrick(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard
            )
        )

    def addGoomba(self, x, y):
        self.entityList.append(
            Goomba(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addKoopa(self, x, y):
        self.entityList.append(
            Koopa(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addRedMushroom(self, x, y):
        self.entityList.append(
            RedMushroom(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )
