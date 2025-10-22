import pygame
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from entities.Mario import Mario


windowSize = 1280, 720
logical_size = 640, 480


def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    # Create a logical surface where the game will be drawn at native 640x480
    logical_surface = pygame.Surface(logical_size)
    max_frame_rate = 60
    # Pass the logical_surface to game systems so all drawing happens at 640x480
    dashboard = Dashboard("./img/font.png", 8, logical_surface)
    sound = Sound()
    level = Level(logical_surface, sound, dashboard)
    menu = Menu(logical_surface, dashboard, level, sound)

    while not menu.start:
        # Draw menu into the logical surface at its native resolution
        menu.update()
        # Scale logical surface to window size (nearest-neighbour) and blit
        scaled = pygame.transform.scale(logical_surface, windowSize)
        screen.blit(scaled, (0, 0))
        pygame.display.update()

    mario = Mario(0, 0, level, logical_surface, dashboard, sound)
    # expose player on level for easier targeting by entities like Boss
    level.player = mario
    clock = pygame.time.Clock()

    while not mario.restart:
        pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
        if mario.pause:
            mario.pauseObj.update()
        else:
            level.drawLevel(mario.camera)
            dashboard.update()
            mario.update()

        # Debug visuals: Draw a rectangle and text on the logical surface
        pygame.draw.rect(logical_surface, (255, 0, 0), (10, 10, 100, 50))  # Red rectangle
        font = pygame.font.Font(None, 36)
        debug_text = font.render("Debug Mode", True, (255, 255, 255))
        logical_surface.blit(debug_text, (10, 70))

        # Scale logical surface to the window size (nearest neighbour for pixel-art)
        scaled = pygame.transform.scale(logical_surface, windowSize)
        screen.blit(scaled, (0, 0))
        pygame.display.update()
        clock.tick(max_frame_rate)
    return 'restart'


if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = main()
