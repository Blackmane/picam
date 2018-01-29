# -*- coding: utf-8 -*-

'''
Created on 09/nov/2015

@author: Niccolò Pieretti

@todo:  
'''
import pygame

def write_topcenter_text(stringa, size, color_t, surface):
    font = pygame.font.Font(None, size)
    text = font.render(stringa, 1, color_t)#, color_b)        # Nero su sfondo bianco
    textpos = text.get_rect()
    textpos.centerx = surface.get_rect().centerx        # Centra con lo schermo
    surface.blit(text, textpos)
    
def write_center_text(stringa, size, color_t, surface, vertical):
    font = pygame.font.Font(None, size)
    text = font.render(stringa, 1, color_t)
    textpos = text.get_rect()
    textpos.centerx = surface.get_rect().centerx        # Centra orizzontalmente con lo schermo
    surface.blit(text, (textpos[0], vertical))

def write_right_text(stringa, size, color_t, surface, vertical):
    font = pygame.font.Font(None, size)
    text = font.render(stringa, 1, color_t)
    textpos = text.get_rect()
    textpos.right = surface.get_rect().right
    #textpos.centerx = surface.get_rect().centerx        # Centra orizzontalmente con lo schermo
    surface.blit(text, (textpos[0], vertical))

def blit_alpha(screen, img, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((img.get_width(), img.get_height())).convert()
    temp.blit(screen, (-x, -y))
    temp.blit(img, (0, 0))
    temp.set_alpha(opacity)        
    screen.blit(temp, location)