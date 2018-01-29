# -*- coding: utf-8 -*-

'''
Created on 01/set/2015

@author: Niccolò Pieretti

@todo:  animazioni!
        muovi
        rilascia
        schermata foto
'''
import io
import atexit
import pygame
from widget import *

stream = io.BytesIO()
atexit.register(stream.close)

f_smuovi = 0
f_srilascia = 1

line = None

class Schermata:

    def __init__(self, obj, funs, **args):
        self.widgets = obj        # Lista di widgets [bottoni] che possono essere fissi o mobili
        self.funs = funs          # Lista delle funzioni di schermata [MS, RS] -> tapmuovi schermata, rilascia schermata
        self.offset = (0, 0)      # Slittamento della schermata (x, y) -> influisce solo sulle aree fluttuanti
        self.limInf = None        # Lunghezza e larghezza minima dell'area / dell'offset
        self.limSup = None        # Lunghezza e larghezza massima dell'area / dell'offset
        self.alpha = 255
        self.objMouseDown = None    # Oggetto che è stato selezionato con il mouse down
        for chiave, valore in args.iteritems():
            if      chiave == 'limI': self.limInf = valore
            elif    chiave == 'limS': self.limSup = valore

    def contiene(self, punto):
        ''' Restituisce l'oggetto su cui è posizionato il mouse.
            Scorre in modo LIFO. '''
        p = (punto[0] - self.offset[0], punto[1] - self.offset[1])
        for o in reversed(self.widgets):
            if o.float:
                if o.contiene(p):
                    return o
            else:
                if o.contiene(punto):
                    return o
        return None
    
    def muovi(self):
        f = self.funs[f_smuovi]
        if f is not None:
            f(self)
        pass
    
    def rilascia(self):
        f = self.funs[f_srilascia]
        if f is not None:
            f(self)
        pass
    
    def draw(self, screen):
        #  if animazione is not none...?
        for o in self.widgets:
            if o.float:
                o.drawFloat(screen, self.offset)
            else:
                o.draw(screen) 
        # pass #? le aree dovrebbero anzi avere un parametro float=true/false -> problema chi disegno prima

    def onMouseDown(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.onMouseDown(pos)
        self.objMouseDown = obj
    
    def onMouseUp(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.onMouseUp(pos)
        if self.objMouseDown:
            self.objMouseDown.selezionato = False
    
    def onMouseMove(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.onMouseMove(pos)
    
    def Click(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.Click(pos)
    
    def RightClick(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.RightClick(pos)
    
    def DoubleClick(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.DoubleClick(pos)

class CameraView(Schermata):
    # Animazioni sui bottoni => scompaiono/ricompaiono (eventualmente da abilitare o meno)
    
    def __init__(self, obj, funs, camera, cButton, **args):
        Schermata.__init__(self, obj, funs, **args)
        self.camera = camera
        self.flash = False
        self.thickness = 0
        self.t = 0
        self.cButton = cButton # Camera button
        self.ghost = True # Per nascondere l'interfaccia
        
        self.lastScreen = None
    
    def setOpzioni(self, **args):
        pass
    
    def draw(self, screen):
        # camera
        # white -> flash & 0 -> not flash or not 0
        # camera bordo
        if not self.flash: #or (self.thickness <> 0):
            try:
                for foo in self.camera.capture_continuous(stream, use_video_port=True, format='jpeg', quality=85): #quality=qualita_JPEG):
                    stream.truncate()
                    stream.seek(0)
                    stream_copy = io.BytesIO(stream.getvalue())
                    self.lastScreen = pygame.image.load(stream_copy, 'jpeg')
                    screen.blit(self.lastScreen, (0, 0))
                    break
            except Exception as err:
                # Non fare nulla
                print 'Errore sullo streaming: ', err        # __str__ allows args to be printed directly
            
            if not self.ghost:
                Schermata.draw(self, screen)
            else:
                if self.alpha > 0:
                    for o in self.widgets:
                        o.drawOpacity(screen, self.alpha)
                    self.alpha -= 50
            self.cButton.draw(screen)
            # Draw + alpha -> animazione
        else:
            # Draw riquadro bianco
            # Draw area semitrasparente
            if self.thickness == 0:
                screen.fill((255,255,255))
                self.thickness = 1
            else:
                screen.blit(self.lastScreen, (0, 0))
                
                t = (self.thickness - self.t)
                s = t * 10
                color = pygame.Color(215 + s,215 + s,215 + s)
                area = (t-1,t-1,322 - (2*t),242 - (2*t))
                pygame.draw.rect(screen, color, area, 2*t)
                if self.thickness >= 3:
                    self.t += 1
                else:
                    self.thickness += 1
                if self.t >= 3:
                    self.flash = False

    
    def flashAnimation(self):
        '''
        Animazione: avvia l'animazione del "flash" a schermo (bordi bianchi o schermata lampeggiante)
        '''
        self.flash = True
        self.thickness = 0
        self.t = 0
        
    def contiene(self, punto):
        ''' Restituisce l'oggetto su cui è posizionato il mouse.
            Il bottone camera è il primo '''
        if self.cButton.contiene(punto):
            return self.cButton
        elif not self.ghost:
            obj = Schermata.contiene(self, punto)
            return obj
        return None
    
    def Click(self, pos):
        obj = self.contiene(pos)
        if obj: 
            obj.Click(pos)
        else:
            self.ghost = not self.ghost
            if self.ghost:
                self.alpha = 200
    


    '''
    def onMouseDown(self, pos):
        #contiene(self, pos).onMouseDown
        pass
    
    
    
    def onMouseMove(self, pos):
        pass

    
    def RightClick(self, pos):
        pass
    
    def DoubleClick(self, pos):
        pass
    #'''

class CameraOptionView(Schermata):
    '''
        >> Opzione
        >> Disegnarla in modo parametrico
        >> Interagire con essa
        >> Salvarla
    '''
    
    def __init__(self, obj, funs, camera, option, **args):
        Schermata.__init__(self, obj, funs, **args)
        self.camera = camera
        self.option = option
        self.ghost = False  #? nascondere l'interfaccia?
    
    def next(self):
        self.option.next(self.camera)
    
    def prec(self):
        self.option.prec(self.camera)
        
    def press(self):
        self.option.press(self.camera)
    
    def draw(self, screen):
        try:
            for foo in self.camera.capture_continuous(stream, use_video_port=True, format='jpeg', quality=85): #quality=qualita_JPEG):
                stream.truncate()
                stream.seek(0)
                stream_copy = io.BytesIO(stream.getvalue())
                self.lastScreen = pygame.image.load(stream_copy, 'jpeg')
                screen.blit(self.lastScreen, (0, 0))
                break
        except Exception as err:
            # Non fare nulla
            print 'Errore sullo streaming: ', err        # __str__ allows args to be printed directly
        Schermata.draw(self, screen)        
        self.option.draw(screen)
    
    def onMouseDown(self, pos):
        Schermata.onMouseDown(self, pos)
        self.option.onMouseDown(pos)
    
    def onMouseUp(self, pos):
        Schermata.onMouseUp(self, pos)
        self.option.onMouseUp(pos)
        
    def onMouseMove(self, pos):
        Schermata.onMouseMove(self, pos)
        self.option.onMouseMove(pos, self.camera)
    
    def Click(self, pos):
        Schermata.Click(self, pos)
        self.option.Click(pos)
    
    def RightClick(self, pos):
        Schermata.RightClick(self, pos)
        self.option.RightClick(pos)
    
    def DoubleClick(self, pos):
        Schermata.DoubleClick(self, pos)
        self.option.DoubleClick(pos)
    

class DeleteView(Schermata):
    
    def __init__(self, obj, funs, **args):
        Schermata.__init__(self, obj, funs, **args)
        self.img = None
        
    def setImg(self, img):
        self.img = img
        
    def draw(self, screen):
        if self.img is not None and self.img.img is not None:
            screen.blit(self.img.img, (0, 0))
        else:
            screen.fill((230,230,230))
        Schermata.draw(self, screen)

class MenuView(Schermata):
    
    def __init__(self, obj, funs, **args):
        global line
        Schermata.__init__(self, obj, funs, **args)
        line = pygame.Surface((4, 140), pygame.SRCALPHA, 32)
        line.fill((230,230,230))
        
    def draw(self, screen):
        screen.fill((200, 200, 200))
        
        pygame.draw.line(screen, (150,150,150), (10,  2 + self.offset[1]), (306,  2 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10, 56 + self.offset[1]), (306, 56 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,110 + self.offset[1]), (306,110 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,164 + self.offset[1]), (306,164 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,218 + self.offset[1]), (306,218 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,272 + self.offset[1]), (306,272 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,326 + self.offset[1]), (306,326 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,380 + self.offset[1]), (306,380 + self.offset[1]), 1)
        pygame.draw.line(screen, (150,150,150), (10,434 + self.offset[1]), (306,434 + self.offset[1]), 1)
        
        Schermata.draw(self, screen)  
        
        write_center_text("Effects", 40, (40,40,40), screen,  4 + 12 + self.offset[1])
        write_center_text("Rotations", 40, (40,40,40), screen, 58 + 12 + self.offset[1])
        write_center_text("Exposure", 40, (40,40,40), screen,112 + 12 + self.offset[1])
        write_center_text("Colors", 40, (40,40,40), screen, 166 + 12 + self.offset[1])
        write_center_text("ISO", 40, (40,40,40), screen,220 + 12 + self.offset[1])
        write_center_text("Others", 40, (40,40,40), screen,274 + 12 + self.offset[1])
        write_center_text("Reset Option", 40, (40,40,40), screen,328 + 12 + self.offset[1])
        write_center_text("EXIT", 40, (200,40,40), screen,382 + 12 + self.offset[1])
        
        screen.blit(line, (316, int(-self.offset[1] * 240 /440)))
          

class Schermate():
    
    def __init__(self):
        self.idxCurrentView = -1
        self.listaView = []
        
    def inizializza(self, listaView):
        #iconPath = path     #'/home/pi/picam/icone'
        self.idxCurrentView = 0
        self.listaView = listaView

    def setView(self, n):
        if n < 0:
            self.idxCurrentView = 0
        else:
            self.idxCurrentView = n
            
    def draw(self, screen):
        self.listaView[self.idxCurrentView].draw(screen)


    def contiene(self, punto):
        return self.listaView[self.idxCurrentView].contiene(punto)
    
    def muovi(self):
        self.listaView[self.idxCurrentView].muovi()
    
    def rilascia(self):
        self.listaView[self.idxCurrentView].rilascia()

    def onMouseDown(self, pos):
        self.listaView[self.idxCurrentView].onMouseDown(pos)
    
    def onMouseUp(self, pos):
        self.listaView[self.idxCurrentView].onMouseUp(pos)
    
    def onMouseMove(self, pos):
        self.listaView[self.idxCurrentView].onMouseMove(pos)
    
    def Click(self, pos):
        self.listaView[self.idxCurrentView].Click(pos)
    
    def RightClick(self, pos):
        self.listaView[self.idxCurrentView].RightClick(pos)
    
    def DoubleClick(self, pos):
        self.listaView[self.idxCurrentView].DoubleClick(pos)



