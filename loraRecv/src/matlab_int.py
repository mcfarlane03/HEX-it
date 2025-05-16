import pygame
import matlab.engine
import threading
import os

class MatlabControl:
    def __init__(self):
        self.running = False
        self.matlab_running = False
        self.thread = None
        self.eng = None
        self.script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pathVisual.m'))

    def start(self):
        if not self.running:
            self.running = True
            self.eng = matlab.engine.start_matlab()
            self.thread = threading.Thread(target=self._run_pygame_loop)
            self.thread.start()
            return True, "MATLAB control started"
        else:
            return False, "MATLAB control already running"

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            if self.eng:
                self.eng.quit()
                self.eng = None
            return True, "MATLAB control stopped"
        else:
            return False, "MATLAB control not running"

    def _run_pygame_loop(self):
        pygame.init()
        screen = pygame.display.set_mode((500, 200))
        pygame.display.set_caption("MATLAB Control")

        font = pygame.font.Font(None, 36)
        start_button = pygame.Rect(100, 60, 120, 50)
        stop_button = pygame.Rect(280, 60, 120, 50)

        while self.running:
            screen.fill((30, 30, 30))
            pygame.draw.rect(screen, (0, 128, 0), start_button)
            pygame.draw.rect(screen, (128, 0, 0), stop_button)

            screen.blit(font.render("Start", True, (255, 255, 255)), (130, 75))
            screen.blit(font.render("Stop", True, (255, 255, 255)), (310, 75))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        if not self.matlab_running:
                            print("Running MATLAB code...")
                            self.eng.eval(f"run('{self.script_path}')", nargout=0)
                            self.matlab_running = True
                    elif stop_button.collidepoint(event.pos):
                        print("Stopping...")
                        self.eng.eval("clear all; close all;", nargout=0)
                        self.matlab_running = False

            pygame.display.flip()

        pygame.quit()

matlab_control = MatlabControl()

def start_matlab_script_async():
    return matlab_control.start()

def stop_matlab_script():
    return matlab_control.stop()
