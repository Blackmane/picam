# -*- coding: utf-8 -*-

'''
Created on 02/set/2015

@author: Niccolò Pieretti

@todo: classe animazione
'''

class Animazione:
    
    def __init__(self, list, fun=None, **args):
        self.list = list
        self.current = 0
        self.fun = fun
    
    def start(self):
        self.current = 0
    
    def next(self):
        if self.fun is None:
            self.current = (self.current + 1) % len(self.list)
        else:
            self.current = self.fun(self.current)
            
    def draw(self, screen, pos):
        screen.blit(self.list[self.current], pos)
        
class TransparentAnimation(Animazione):
    
    def __init__(self, larghezza, altezza, frame=1, **args):
        pass
        
        
    
    

