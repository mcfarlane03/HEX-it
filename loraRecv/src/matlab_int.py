import pygame
import matlab.engine

# Start MATLAB engine
eng = matlab.engine.start_matlab()

pygame.init()
screen = pygame.display.set_mode((500, 200))
pygame.display.set_caption("MATLAB Control")

font = pygame.font.Font(None, 36)
live_button = pygame.Rect(100, 60, 120, 50)
map_button = pygame.Rect(280, 60, 120, 50)
map2_button = pygame.Rect(280, 60, 120, 50)

running = True
matlab_running = False

while running:
    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 128, 0), live_button)
    pygame.draw.rect(screen, (128, 0, 0), map_button)
    pygame.draw.rect(screen, (128, 0, 0), map2_button)

    screen.blit(font.render("Live", True, (255, 255, 255)), (130, 75))
    screen.blit(font.render("Map", True, (255, 255, 255)), (310, 75))
    screen.blit(font.render("Map 2", True, (255, 255, 255)), (310, 75))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if live_button.collidepoint(event.pos):
                if not matlab_running:
                    print("Running MATLAB code...")
                    eng.LidarSLAMSystem('COM9', nargout=0)
                    matlab_running = True
            elif map_button.collidepoint(event.pos):
                print("Mapping...")
                eng.eval("run('pathVisual.m')", nargout=0)
            elif map2_button.collidepoint(event.pos):
                print("Mapping 2...")
                eng.eval("run('roomMapper.m')", nargout=0)
                matlab_running = False

    pygame.display.flip()

pygame.quit()
eng.quit()
