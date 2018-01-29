# -*- coding: utf-8 -*-

'''
Created on 01/set/2015

@author: Niccolò Pieretti

@todo: controllare "esegui"
        testo sul bottone?
        new widget: label
        new widget: slider
'''

import pygame
from src.util import *

class Widget:
    def __init__(self, rect, funcs, **args):    # funcs [mousedown, mouseup, mousemove, click, rightclick, doubleclick]
                                                #[Click, DoppioClick, Right Click, Muovi, Rilascia]
        self.rect = rect # Area rettangolare (left, top, width, height)
        self.onMouseDownFun = funcs[0]
        self.onMouseUpFun = funcs[1]
        self.onMouseMoveFun = funcs[2]
        self.ClickFun = funcs[3]
        self.RightClickFun = funcs[4]
        self.DoubleClickFun = funcs[5]
        self.selezionato = False
        self.float = False
        for chiave, valore in args.iteritems():
            if chiave == 'float': self.float = valore
            #if chiave == 'offset': self.offset = valore
            #elif chiave == 'float': self.float = valore
    
    def contiene(self, punto):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        if ((x1 <= punto[0] <= x2) and (y1 <= punto[1] <= y2)):
            return True
        return False
    
    def draw(self, screen):
        pass
    
    def drawFloat(self, screen, offset):
        pass
    
    def onMouseDown(self, pos):
        self.selezionato = True
        if self.onMouseDownFun is not None:
            if self.onMouseDownFun[0] is not None:
                self.onMouseDownFun[0](self, pos, self.onMouseDownFun[1])
    
    def onMouseUp(self, pos):
        if self.onMouseUpFun is not None and self.selezionato:
            if self.onMouseUpFun[0] is not None:
                self.onMouseUpFun[0](self, pos, self.onMouseUpFun[1])
        self.selezionato = False
    
    def onMouseMove(self, pos):
        if self.onMouseMoveFun is not None:
            if self.onMouseMoveFun[0] is not None:
                self.onMouseMoveFun[0](self, pos, self.onMouseMoveFun[1])
    
    def Click(self, pos):
        if self.ClickFun is not None:
            if self.ClickFun[0] is not None:
                self.ClickFun[0](self, pos, self.ClickFun[1])
    
    def RightClick(self, pos):
        if self.RightClickFun is not None:
            if self.RightClickFun[0] is not None:
                self.RightClickFun[0](self, pos, self.RightClickFun[1])
    
    def DoubleClick(self, pos):
        if self.DoubleClickFun is not None:
            if self.DoubleClickFun[0] is not None:
                self.DoubleClickFun[0](self, pos, self.DoubleClickFun[1])


class Icona:

    def __init__(self, larghezza, altezza, **args):
        self.altezza = altezza
        self.larghezza = larghezza
        colore = None    # Colore sfondo
        backgroundPath = None    # Immagine di sfondo
        foregroundPath = None    # Immagine in primo piano
        for chiave, valore in args.iteritems():
            if      chiave == 'bg': backgroundPath = valore
            elif    chiave == 'fg': foregroundPath = valore
            elif    chiave == 'colore': colore = valore
        self.surface = pygame.Surface((self.larghezza, self.altezza), pygame.SRCALPHA, 32)
        if colore:
            self.surface.fill(colore)
        try: #Prova a disegnare il background
            bitmap = pygame.image.load(backgroundPath)
            self.surface.blit(bitmap,
                              ((self.larghezza - bitmap.get_width()) / 2,
                               (self.altezza - bitmap.get_height()) / 2))
        except:
            pass
        try: #Prova a disegnare il foreground
            bitmap = pygame.image.load(foregroundPath)
            self.surface.blit(bitmap,
                              ((self.larghezza - bitmap.get_width()) / 2,
                               (self.altezza - bitmap.get_height()) / 2))
        except:
            pass
        self.surface = self.surface.convert_alpha()

class LeftIcona:
    
    def __init__(self, larghezza, altezza, **args):
        self.altezza = altezza
        self.larghezza = larghezza
        colore = None    # Colore sfondo
        backgroundPath = None    # Immagine di sfondo
        foregroundPath = None    # Immagine in primo piano
        for chiave, valore in args.iteritems():
            if      chiave == 'bg': backgroundPath = valore
            elif    chiave == 'fg': foregroundPath = valore
            elif    chiave == 'colore': colore = valore
        self.surface = pygame.Surface((self.larghezza, self.altezza), pygame.SRCALPHA, 32)
        if colore:
            self.surface.fill(colore)
        try: #Prova a disegnare il background
            bitmap = pygame.image.load(backgroundPath)
            self.surface.blit(bitmap,
                              (0, (self.altezza - bitmap.get_height()) / 2))
        except:
            pass
        try: #Prova a disegnare il foreground
            bitmap = pygame.image.load(foregroundPath)
            self.surface.blit(bitmap,
                              (0, (self.altezza - bitmap.get_height()) / 2))
        except:
            pass
        self.surface = self.surface.convert_alpha() 

class BottoneWidget(Widget):
    
    def __init__(self, rect, funs, **args):
        Widget.__init__(self, rect, funs, **args)
        #self.funs = funs#!SHIT!    # Funzioni del bottone [Click, DoppioClick, Right Click, Muovi, Rilascia]
        self.img = None
        self.imgPressed = None
        for chiave, valore in args.iteritems():
            if    chiave == 'img': self.img = valore
            elif    chiave == 'imgPressed': self.imgPressed = valore
    '''
    def esegui(self, i):
        if self.funs[i] is not None:
            fun = self.funs[i][0]
            arg = self.funs[i][1]
            if fun is not None and arg is not None: 
                fun(arg)
            elif fun is not None: 
                fun()
            # else: pass
    
    def contieneEdEsegui(self, punto, i):
        if self.contiene(punto):
            self.esegui(i)
            return True
        return False
    '''
    def draw(self, screen):
        if self.selezionato:
            if self.imgPressed is not None:
                print "imgpressed"
                screen.blit(self.imgPressed.surface, (self.rect[0], self.rect[1]))
        else:
            if self.img is not None:
                screen.blit(self.img.surface, (self.rect[0], self.rect[1]))
    
    def drawOpacity(self, screen, opacity):
        blit_alpha(screen, self.img.surface, (self.rect[0], self.rect[1]), opacity)
    
    def drawFloat(self, screen, offset):
        if self.selezionato:
            if self.imgPressed is not None:
                screen.blit(self.imgPressed.surface, (self.rect[0] + offset[0], self.rect[1] + offset[1]))
        else:
            if self.img is not None:
                screen.blit(self.img.surface, (self.rect[0] + offset[0], self.rect[1] + offset[1]))
