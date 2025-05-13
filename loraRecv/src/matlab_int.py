import pygame
import matlab.engine

# Start MATLAB engine
eng = matlab.engine.start_matlab()

pygame.init()
screen = pygame.display.set_mode((500, 200))
pygame.display.set_caption("MATLAB Control")

font = pygame.font.Font(None, 36)
start_button = pygame.Rect(100, 60, 120, 50)
stop_button = pygame.Rect(280, 60, 120, 50)

running = True
matlab_running = False

while running:
    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 128, 0), start_button)
    pygame.draw.rect(screen, (128, 0, 0), stop_button)

    screen.blit(font.render("Start", True, (255, 255, 255)), (130, 75))
    screen.blit(font.render("Stop", True, (255, 255, 255)), (310, 75))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                if not matlab_running:
                    print("Running MATLAB code...")
                    eng.eval("run('pathVisual.m')", nargout=0)
                    matlab_running = True
            elif stop_button.collidepoint(event.pos):
                print("Stopping...")
                eng.eval("clear all; close all;", nargout=0)
                matlab_running = False

    pygame.display.flip()

pygame.quit()
eng.quit()
