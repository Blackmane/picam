# -*- coding: utf-8 -*-

'''
Created on 03/set/2015

@author: Niccolò Pieretti

@todo: load immagini in multithreading -> THREAD SAFE
'''

import fnmatch
import os
import threading
import time
from pygame import display, Surface
from image_list import ListaImmagini, Immagine
from util import *
from view import *
from operator import pos
from widget import Icona

LEFT = -1
RIGHT = 1
NOSHIFT = 0

screen = None
th = None
busy = False
busyImage = None
waitImg = None
line = None
work = None
opz = None
numb = None
loading = None
textpos = None

imgPath = None
zoomSize = (640, 480)

def getNomeImg(id):
    ''' Dato un id, genera il path '''
    global imgPath
    return imgPath + '/IMG_' + '%04d' % id + '.JPG'

def getMaxId():
    ''' Scorre la directory indicata da path, cerca i file JPG con il nome nel 
        formato IMG_XXXX.JPG, e restituisce 
        (max, n)    max = il massimo identificativo utilizzato;
                    n = totale delle foto presenti
        None        se la cartella non contiene immagini '''
    global imgPath
    n = 0
    max = -1
    try:
        for file in os.listdir(imgPath):
            if fnmatch.fnmatch(file, 'IMG_[0-9][0-9][0-9][0-9].JPG'):
                n += 1
                i = int(file[4:8])
                if (i > max): max = i
    finally:
        print "tot:", n
        return None if max == -1 else (max, n)

def loadImmagineGalleria(id):
    ''' Restituisce un oggetto Immagine, contenente l'immagine scalata a (320, 240). 
        se non trova nulla, restituisce None'''
    res = None
    nomeFoto = getNomeImg(id)
    if os.path.isfile(nomeFoto):
        img = pygame.image.load(nomeFoto)
        res = Immagine(pygame.transform.scale(img, (320, 240)).convert(), id)        
    return res

def loadPrecImg(n):
    ''' Restituisce un oggetto Immagine, contenente la prima immagine (scalata) precedente a quella
        di nome n
        se non trova nulla, restituisce None '''
    res = None
    n -= 1
    while n >= 0:    # ? metodo lento...
        nomeFoto = getNomeImg(n)
        if os.path.isfile(nomeFoto): 
            img = pygame.image.load(nomeFoto)
            return Immagine(pygame.transform.scale(img, (320, 240)).convert(), n)
        n -= 1
    return res

def loadNextImg(n):
    ''' Restituisce un oggetto Immagine, contenente la prima immagine (scalata) successiva a quella
        di nome n
        se non trova nulla, restituisce None '''
    print "LoadNextImg:", n
    res = None
    n += 1
    while n <= 9999:    # ? metodo lento...
        nomeFoto = getNomeImg(n)
        if os.path.isfile(nomeFoto): 
            img = pygame.image.load(nomeFoto)
            return Immagine(pygame.transform.scale(img, (320, 240)).convert(), n)
        n += 1
    return res

def calcZoomPos(pos, size):
    posx = pos[0] - 80
    if posx <= 0:
        x = 0
    elif posx > 160:
        x = size[0] - 320
    else:
        x = (posx * size[0] / 320)
    posy = pos[1] - 60
    if posy <= 0:
        y = 0
    elif posy > 120:
        y = size[1] - 240
    else:
        y = (posy * size[1] / 240)
    return (-1 * x, -1* y)

class Galleria(Schermata):
    
    def __init__(self, obj, funs, path, s, **args):
        global imgPath, zoomSize, screen
        Schermata.__init__(self, obj, funs, **args)
        imgPath = path # path della cartella contenente le immagini
        screen = s
        self.imgBlitPosition = (0, 0)
        self.list = None
        self.nameLastFoto = -1
        self.totaleFoto = 0 # Numero totale di foto presenti
        self.idCurrentFoto = -1 # idCurrentFoto è il numero della foto, rispetto al totale (i-esima foto) <totalefoto
        
        self.anoherRight = False    # False se si è in fondo a destra
        
        self.shift = NOSHIFT
        self.ghost = False # Fai sparire l'interfaccia, controllato dai CLICK #? animazione?
        self.alpha = 255
        self.zoom = False # Attiva la modalità zoom
        self.zoomImg = None
        self.zoomPosition = (0,0)
        self.mouseDown = False
        self.mouseDownPos = (0, 0)
        
        self.objMouseDown = None

    def inizializza(self):#?
        global path, work, waitImg, line, opz, numb, loading, textpos
        if not os.path.isdir(imgPath):
            try:    # Se non esiste, crea la cartella
                os.makedirs(imgPath)
                # Set new directory ownership to pi user, mode to 755
                # os.chown(imgPath, uid, gid)
                os.chmod(imgPath,
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | 
                    stat.S_IRGRP | stat.S_IXGRP | 
                    stat.S_IROTH | stat.S_IXOTH)
            except OSError as e:
                print errno.errorcode[e.errno]
        
        (self.nameLastFoto, self.totaleFoto) = getMaxId()
        img = loadImmagineGalleria(self.nameLastFoto)
        self.list = ListaImmagini(img,self.totaleFoto)
        self.idCurrentFoto = self.totaleFoto
        # ha caricato solo una immagine!
        # in multithreading carica le altre?
        work = [Icona(80, 80, bg='/home/pi/picam/icone/spirale01.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale02.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale03.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale04.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale05.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale06.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale07.png'),
                Icona(80, 80, bg='/home/pi/picam/icone/spirale08.png')
        ]
        waitImg = pygame.Surface((320, 240), pygame.SRCALPHA, 32)
        waitImg.fill((200,200,200))
        pygame.draw.polygon(waitImg, (90,90,90), [(20,20), (20,220), (300,220), (300,20)], 20)
        pygame.draw.polygon(waitImg, (90,90,90), [(80,120), (50,200), (160,200)])
        pygame.draw.polygon(waitImg, (90,90,90), [(170,140), (130,160), (170,200), (210, 200)])
        pygame.draw.polygon(waitImg, (90,90,90), [(280,170), (200,170), (220,200), (280, 200)])
        pygame.draw.circle(waitImg, (90,90,90), (240, 80), 25, 0)
        font = pygame.font.Font(None, 50)
        text = font.render('Loading..', 1, (0,0,0))
        waitImg.blit(text, (50,70))
        
        line = pygame.Surface((5, 240), pygame.SRCALPHA, 32)
        line.fill((0,0,0))
        opz = Icona(320,44, colore=(200, 200, 200))
        numb = Icona(120,23, fg='/home/pi/picam/icone/numbback.png')
        
        font = pygame.font.Font(None, 60)
        loading = font.render('Loading..', 1, (10,10,10))
        textpos = loading.get_rect()
        textpos.centerx = screen.get_rect().centerx
        textpos.centery = screen.get_rect().centery-20
        
        '''
        opz =  pygame.Surface((320, 44), pygame.SRCALPHA, 32)   # ICONA()
        opz.fill((200,200,200))
        '''
    
    def next(self):
        '''
            Se a destra ho None o sono sul 6, devo aggiungere, altrimenti solo scorrere (?)
            [0, 1 ,2 ,3 ,4 ,5 ,6]
        '''
        screen.blit(loading, (textpos[0], textpos[1]))   
        display.update(textpos)
        
        if self.list.scorriDestra():
            pass
        else:
            id = self.list.lastId()
            if id is not None:
                img = loadNextImg(id)
                if img is not None:
                    self.list.aggiungiDaDestra(img)
        self.zoomImg = None
    
    def prec(self):        
        screen.blit(loading, (textpos[0], textpos[1]))   
        display.update(textpos)
        
        if self.list.scorriSinistra():
            pass
        else:
            id = self.list.firstId()
            if id is not None:
                img = loadPrecImg(id)
                if img is not None:
                    self.list.aggiungiDaSinistra(img)
        self.zoomImg = None
    
    def elimina(self): #?
        img = self.list.getCurrentImg()
        if img is not None:
            nomeFoto = getNomeImg(img.nome)
            os.remove(nomeFoto)
            self.totaleFoto -= 1
            
            self.list.elimina()
            c = self.list.getCurrentImg()
            if c is None:
                (self.nameLastFoto, self.totaleFoto) = getMaxId()
                img = loadImmagineGalleria(self.nameLastFoto)
                self.list = ListaImmagini(img,self.totaleFoto)
                self.idCurrentFoto = self.totaleFoto
            self.zoomImg = None
        
    def contiene(self, punto):
        ''' Restituisce l'oggetto su cui è posizionato il mouse.
                Scorre in modo FIFO. '''
        if not self.zoom and not self.ghost:
            for o in self.widgets:
                if o.contiene(punto):
                    return o
        return None
    
    def muovi(self):
        '''
        f = self.funs[f_smuovi]
        if f is not None:
            f(self)'''
        pass
    
    def rilascia(self):
        '''
        f = self.funs[f_srilascia]
        if f is not None:
            f()'''
        pass
    
    def drawNoPhoto(self, screen):
        #? va rifatta in modo più carino
        screen.fill((200, 200, 200))
        write_topcenter_text('NO PHOTO', 36, (10, 10, 10), screen)
    
    def drawCurrentPhoto(self, screen):
        global numb
        i = self.list.attiva
        if 0 <= i <= 6:
            img = self.list.struct[i]
            if img is not None and img.img is not None:
                screen.blit(img.img, (0,0))
                if not self.ghost:
                    blit_alpha(screen, numb.surface, (101,2), 150)
                    stringa = '%04d' % self.list.currentIndex() + '/' + '%04d' % self.totaleFoto #? voglio spazi bianchi e non 0
                    write_topcenter_text(stringa, 36, (10, 10, 10), screen)
            else:
                self.drawNoPhoto(screen)
        else: # i out of range
            self.drawNoPhoto(screen)
        
    def drawShifting(self, screen):
        global waitImg, line
        # Shift != NOSHIFT
        i = self.list.attiva
        if not self.mouseDown:
            # Mouse Up
            '''
            screen.blit(waitImg, (0, 0))
            write_topcenter_text('BLBLLBLBBLBL', 36, (10, 10, 10), (255, 255, 255), screen)
            '''
            if 0 <= i <= 6:
                img = self.list.struct[i]
                if img is not None and img.img is not None:
                    if self.shift == LEFT:
                        screen.blit(img.img, (self.imgBlitPosition[0] + 325, 0))
                        if 0 < i <= 6:
                            img = self.list.struct[i-1]
                            if img is not None and img.img is not None:
                                screen.blit(img.img, self.imgBlitPosition)
                        screen.blit(line, (self.imgBlitPosition[0] + 320, 0))
                    if self.shift == RIGHT:
                        screen.blit(img.img, (self.imgBlitPosition[0] - 325, 0))
                        if 0 <= i < 6:
                            img = self.list.struct[i+1]
                            if img is not None and img.img is not None:
                                screen.blit(img.img, self.imgBlitPosition)
                        screen.blit(line, (self.imgBlitPosition[0] - 5, 0))
            # Infine aggiorna posizione
            val = self.imgBlitPosition[0]
            if -315 < val < 0:
                self.imgBlitPosition = (val - 10, 0)
            elif 315 > val > 0:
                self.imgBlitPosition = (val + 10, 0)
            else:
                self.imgBlitPosition = (0,0)    #'''
                self.shift = NOSHIFT
                self.alpha = 0
                #Fine
        else: # Mouse down
            if self.shift == LEFT:
                if i < 6:
                    img = self.list.struct[i+1]
                    if img is not None and img.img is not None:
                        screen.blit(img.img, (self.imgBlitPosition[0] + 325, 0))
                    else:
                        screen.blit(waitImg, (self.imgBlitPosition[0] + 325, 0))
                else:
                    screen.blit(waitImg, (self.imgBlitPosition[0] + 325, 0))
                screen.blit(line, (self.imgBlitPosition[0] + 320, 0))
            if self.shift == RIGHT:
                if i > 0:
                    img = self.list.struct[i-1]
                    if img is not None and img.img is not None:
                        screen.blit(img.img, (self.imgBlitPosition[0] - 325, 0))
                    else:
                        screen.blit(waitImg, (self.imgBlitPosition[0] - 325, 0))
                else:
                    screen.blit(waitImg, (self.imgBlitPosition[0] - 325, 0))
                screen.blit(line, (self.imgBlitPosition[0] - 5, 0)) #-330
            if 0 <= i <= 6:
                img = self.list.struct[i]
                if img is not None and img.img is not None:
                    screen.blit(img.img, self.imgBlitPosition)
    
    def drawZoomed(self, screen):
        if self.zoomImg is not None:
            screen.blit(self.zoomImg, self.zoomPosition)
            pygame.draw.rect(screen, (255, 255, 255), (10, 10, 40, 30), 2)
            px = 10 - self.zoomPosition[0] / 16
            py = 10 - self.zoomPosition[1] / 16
            pygame.draw.rect(screen, (255, 255, 255), (px, py, 20, 15))
    
    def draw(self, screen):
        global opz
        '''
            Casi:
            -> Foto singola zoomed
            
            -> Shift (mouse down + shift)
                - Right
                - Left
            -> Rilascio Shift (mouse up + shift)
                - Right
                - Left
                
            -> Foto singola/No Photo
            -> Foto singola e interfaccia
        '''
        if self.zoom:
            # Modalità zoom
            # Draw immagine grande grande!
            self.drawZoomed(screen)
        elif self.shift != NOSHIFT:
            # Shift
            self.drawShifting(screen)
        else: # Single (lady) photo
            #? deve disegnare solo NOPHOTO se non c'è ne sono
            self.drawCurrentPhoto(screen)
            if not self.ghost:
                blit_alpha(screen, opz.surface, (0,194), 150)

                #screen.blit(opz.surface, (0,194))
                for o in self.widgets:
                    if o.float:
                        o.drawFloat(screen, self.offset)
                    else:
                        o.draw(screen) 
            else: # ghost
                if self.alpha >= 50:
                    for o in self.widgets:
                        o.drawOpacity(screen, self.alpha)
                    self.alpha -= 50 #'''
                else:
                    self.alpha = 0
    
    def onMouseDown(self, pos):
        self.mouseDown = True
        self.mouseDownPos = pos
        
        obj = self.contiene(pos)
        if obj:
            obj.selezionato = True
        self.objMouseDown = obj
        
    def onMouseUp(self, pos):
        global busy
        if (not self.zoom) and self.mouseDown and self.objMouseDown is None:
            diffX = self.mouseDownPos[0] - pos[0]
            if diffX > 20:
                if self.list.currentIndex() < self.totaleFoto:
                    self.shift = LEFT
                    # THREAD!
                    a = self.list.attiva
                    if a >= -1 and a < 6:
                        if self.list.struct[a + 1] is None:
                            self.spinner()
                    elif a == 6:
                        self.spinner()
                    self.next()
                    busy = False
                    if th is not None:
                        th.join(500)
            elif diffX < -20:
                if self.list.currentIndex() > 1:
                    self.shift = RIGHT
                    # THREAD!
                    a = self.list.attiva
                    if a > 0 and a < 7:
                        if self.list.struct[a - 1] is None:
                            self.spinner()
                    elif a == 0:
                        self.spinner()
                    self.prec()
                    busy = False
                    if th is not None:
                        th.join(500)
            else:
                self.shift = NOSHIFT
                print "NOSHIFT"
            # if SHIFT!
        #self.shift = NOSHIFT
        self.mouseDown = False
        if self.objMouseDown:
            self.objMouseDown.selezionato = False
            self.objMouseDown = None
    
    def onMouseMove(self, pos):
        if self.zoom and self.zoomImg is not None:
            self.zoomPosition = calcZoomPos(pos, zoomSize)
        if (not self.zoom) and self.mouseDown and self.objMouseDown is None:
            # Float current img
            self.imgBlitPosition = (pos[0] - self.mouseDownPos[0], 0)
            if self.imgBlitPosition[0] < 0:
                if self.list.attiva < 6:
                    pass
                else:
                    pass
                    # Multithread loading
                    #self.next()
                    #self.prec()
                if self.list.currentIndex() < self.totaleFoto:
                    self.shift = LEFT
                # richiama quella a destra
                
            if self.imgBlitPosition[0] > 0:
                if self.list.attiva > 0:
                    pass
                else:
                    pass
                    # Multithread loading
                    #self.prec()
                    #self.next()
                if self.list.currentIndex() > 1:
                    self.shift = RIGHT
                # richiama quella a sinistra
                
            if not self.ghost:
                self.ghost = True
                self.alpha = 100
    
    def Click(self, pos):
        if not self.zoom and not self.ghost:
            obj = self.contiene(pos)
            if obj: 
                obj.Click(pos)
            else:
                self.ghost = not self.ghost
        elif 0 <= self.list.attiva <= 6:
            self.ghost = not self.ghost
        if self.ghost:
            self.alpha = 200
    
    def DoubleClick(self, pos):
        if 0 <= self.list.attiva <= 6:
            self.zoom = not self.zoom
            if self.zoom and self.zoomImg is None:
                try:
                    id = self.list.struct[self.list.attiva].nome
                    nomeFoto = getNomeImg(id)
                    if os.path.isfile(nomeFoto):
                        self.zoomImg = pygame.transform.scale(pygame.image.load(nomeFoto), zoomSize).convert()
                except:
                    pass
            else:
                self.ghost = False
            self.zoomPosition = calcZoomPos(pos, zoomSize)
    
    def getCurrentImg(self):
        return self.list.getCurrentImg()
    
    def printStatus(self):
        stringa = "("
        for i in range(0,7):
            if self.list.struct[i] is None:
                stringa += "None,"
            else:
                stringa += str(i) + ","
        stringa += ")"
        print stringa
    
    def spinnerThread(self):
        global busy, screen, busyImage, work, waitImg, line
        val = self.imgBlitPosition[0]
        inc = 0
        if -325 < val < 0:
            inc = ( (-325) - val ) / 25
        elif 325 > val > 0:
            inc = ( (325) - val ) / 25
        
        i = 0
        while busy:
            val = self.imgBlitPosition[0]
            val += inc
            if val < -325:
                val = -325
            if val > 325:
                val = 325
            
            '''
            if val < 0:
                if -320 < val:
                    val -= 5
                else:
                    val = -325
            elif val > 0:
                if 0 < val < 320:
                    val += 5
                else:
                    val = 325
            else:
                val = 0#'''
            self.imgBlitPosition = (val, 0)
            
            if busyImage is not None and abs(val) != 325:
                screen.blit(busyImage, self.imgBlitPosition)
            if self.shift == LEFT:
                screen.blit(waitImg, (self.imgBlitPosition[0] + 325, 0))
            if self.shift == RIGHT:
                screen.blit(waitImg, (self.imgBlitPosition[0] - 325, 0))
            
            if val > 0:
                screen.blit(line, (val-5,0))
                screen.blit(work[i/4].surface, (val-125,40))
            else:
                screen.blit(line, (val+325,0))
                screen.blit(work[i/4].surface, (val+525,40))
            i = (i + 1) % 32
            
            display.flip()
            
            #print "SLEEP THREAD"
            time.sleep(0.03)

    def spinner(self):
        global busy, th, busyImage
        busy = True
        
        busyImage = None
        i = self.list.attiva
        if 0 <= i <= 6 and self.list.struct[i].img is not None:
            busyImage = self.list.struct[i].img
        
        th = threading.Thread(target=self.spinnerThread)
        th.start()
        time.sleep(0.001)
