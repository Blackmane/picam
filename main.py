#! /usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import print_function
import atexit
import errno
import fnmatch
import pygame.font
import os
import picamera
import pygame
import stat
import thread
import time
from pygame.locals import *
from PIL import Image
from src.gallery import *
from src.option import *
from src.tap_system import *
from src.util import *
from src.view import *
from src.widget import *
from src.adafruit import *

'''
Sensor: Omnivision 5647, five megapixel
Lens: 3.6mm F/2.0 fixed-focus
Dimensions: 21.6mm x 25mm x 8.65mm (excluding cable)
Weight: 3g (excluding cable)
Connection: Camera Serial Interconnect (CSI)
Maximum Still Resolution: 2,592×1,944 (currently limited to 1,920×1,080)
Maximum Video Resolution: 1,920×1,080 (1080p) 30fps

# --- PIANO DI SVILUPPO ---
Slider                    Gestione galleria
Menù opzioni              Modifica immagine e stampala
Grafica delle schermate   Animazioni

# ----- FEATURE -----------
>> Mostra lo stream
>> Fa le foto
>> Salva le foto
>> Applica i filtri
>> Mostrare le foto scattatte
>> Zoom galleria
>> Trasparenze -> trovare un modo per gestirlo -> Trovato! blit_alpha in util


# -- DA VERIFICARE---------
>> Rimuovi foto
>> Salva le opzioni
>> Migliorare la gestione dei click
>> Swift nella galleria
>> Aggiungere le opzioni
        -> Monoschermata (vedi adafruit) con le frecce e/oppure con la barra centrale
>> Gestire le scritte
>> Animazioni
>> Multithreading -> solo con un Raspberry Pi 2 -> t = Multithreading di python => t = Merda
>> Disegnare l'interfaccia
>> Scritte con numeri, es: [3/17]
>> Salvare le opzioni
>> Caricare le opzioni
>> Bottone on/off
>> Pallino degli slider
>> Finire schermata OPZIONI!
>> Bottone exit


#-- BOZZA -----------------
>> Mostra anteprima foto appena scattata -> opzione per disattivarla #Maybe #orMaybeNot


# ----- MANCANTI ----------
>> Bottoni "pressed"
'''

import warnings
warnings.filterwarnings('default', category=DeprecationWarning)

# Funzioni varie ------------------------------------------------------------------------
def imgPath(nome):
    return path[2] + '/' + nome + '.png'

def getNomeImg(id):
    ''' Dato un id, genera il path '''
    return path[0] + '/IMG_' + '%04d' % id + '.JPG'

def getMaxId(path):
    ''' Scorre la directory indicata da path, cerca i file JPG con il nome nel 
        formato IMG_XXXX.JPG, e restituisce il massimo identificativo utilizzato
        None se non ce ne ?? nessuna 
        Aggiorna anche il numero totale di foto presenti nella cartella'''
    global totaleFoto
    n = 0
    max = -1
    try:
        for file in os.listdir(path):
            n += 1
            if fnmatch.fnmatch(file, 'IMG_[0-9][0-9][0-9][0-9].JPG'):
                i = int(file[4:8])
                if(i > max): max = i
    finally:
        totaleFoto = n
        return None if max == -1 else max

def getImageId():
    ''' Verifica che sia presente la cartella del path, se assente la crea.
        Legge fino a che numero sono arrivate le foto e restituisce l'identificativo 
        da usare per salvare le foto '''
    #'''
    global path
    if not os.path.isdir(path[0]):
        try:    # Se non esiste, crea la cartella
            os.makedirs(path[0])
            # Set new directory ownership to pi user, mode to 755
            # os.chown(path[0], uid, gid)
            os.chmod(path[0],
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | 
                stat.S_IRGRP | stat.S_IXGRP | 
                stat.S_IROTH | stat.S_IXOTH)
        except OSError as e:
            print "errno:", e.errno
            print ":", errno.errorcode[e.errno]
    # ? else 0
    i = getMaxId(path[0])
    if i is None:
        return 0
    else:
        if i >= 9999: return 0
        else: return i + 1  #    '''

def scattaFotoThread(camera):
    global nextFotoId, totaleFoto
    nomeFoto = getNomeImg(nextFotoId)
    if os.path.isfile(nomeFoto): c = 0
    else: c = 1        # Se non è già presente aumenta il numero di foto
    try:
        camera.resolution = (2592, 1944)
        camera.led = False
        camera.capture(nomeFoto, use_video_port=False, format='jpeg', thumbnail=None)
        camera.led = True
        camera.resolution = (320, 240)
        # Set image file ownership to pi user, mode to 644
        # os.chown(nomeFoto, uid, gid) # Not working, why?
        os.chmod(nomeFoto, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        print nomeFoto
    finally:
        s_galleria.totaleFoto += c
        totaleFoto += c        # Incrementa il numero di foto salvate
        # Aggiorna galleria
        # Perché caricarlo ora in memoria? Avvisa la galleria che c'è una nuova immagine
        # e che venga caricata da essa quando ha effettivamente bisogno
        '''
        if imgGalleria[2][0] is None:        #? Soluzione pesante!!!!!!!!!!!!!!!!!!!!!!---------------------
            img, id = getImg(nextFotoId)
            if img is not None:
                imgGalleria[2] = (img, totaleFoto, nextFotoId)
        '''
        nextFotoId = (nextFotoId + 1) % 10000 # Incrementa l'identificativo per la prossima foto
        # Add error handling/indicator (disk full, etc.)

def stampaFotoThread(args, n):
    global stampa
    try:
        img = s_galleria.getCurrentImg()
        photoName = "/home/pi/picam/photo/IMG_%04d.JPG" % img.nome
        photoResize = 512, 384
        photoTitle = "Your photo!"
        printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
        i = Image.open(photoName).resize(photoResize, Image.ANTIALIAS).transpose(2)
        # Print the foto
        printer.begin(90) # Warmup time
        printer.setTimes(40000, 3000) # Set print and feed times
        printer.justify('C') # Center alignment
        printer.println(photoTitle)
        printer.feed(2) # Add a blank line
        printer.printImage(i, True) # Specify image to print
        printer.feed(3) # Add a few blank lines
    except:
        print "ERRORE"
    finally:
        stampa = False


# Funzioni dei bottoni ------------------------------------------------------------------

def navigaCallback(widget, pos, n):
    ' Si sposta nella schermata n '
    print "naviga: ", n
    schermate.setView(n)
    if n == sid_fotocamera or n > sid_menuFoto:
        camera.led = True
    else: 
        camera.led = False
    #; tapSys.setSchermata(idxSchermata)
    
def backToOptionCallback(widget, pos, n):
    salvaOpzioni()
    schermate.setView(sid_menuFoto)
    
def scattaFotoCallback(widget, pos, arg):
    global s_fotocamera
    s_fotocamera.flashAnimation()
    # THREAD parallelo
    #t = thread.start_new_thread (scattaFotoThread, (camera, ))
    scattaFotoThread(camera) #?

def stampaFotoCallback(widget, pos, n):
    global stampa
    if stampa:
        pass
    else:
        stampa = True
        print "STAMPA"
        t = thread.start_new_thread (stampaFotoThread, (None, None))
        print "FINE"

def navigaGalleriaCallback(widget, pos, dir):
    global idFotoGalleria, imgGalleria, idxFoto, s_galleria
    if dir == 1: s_galleria.next()
    if dir == -1: s_galleria.prec()

def cancellaCallback(widget, pos, arg):
    global s_galleria, s_confermaCancella
    img = s_galleria.getCurrentImg()
    s_confermaCancella.setImg(img)
    schermate.setView(sid_cancella)
    
def rimuoviFotoCallback(widget, pos, arg):
    global opz
    font = pygame.font.Font(None, 40)
    text = font.render('Deleating..', 1, (100,100,100))
    blit_alpha(screen, opz.surface, (0,194), 150)
    screen.blit(text, (85,200))
    pygame.display.flip()
    s_galleria.elimina()
    schermate.setView(sid_galleria)

def navigaOptValueCallback(widget, pos, n):
    if n == -1:
        schermate.listaView[schermate.idxCurrentView].prec()
    elif n == 1:
        schermate.listaView[schermate.idxCurrentView].next()

def pressOptButtonCallback(widget, pos, n):
    schermate.listaView[schermate.idxCurrentView].press()

def resetCallback(widget, pos, n):
    reset(camera)
    navigaCallback(widget, pos, n)
    #schermata reset

def exitCallback(widget, pos, n):
    global stop
    stop = True

def scroll(schermata):
    global tapSys, schermate
    p1 = tapSys.tapDownPos
    p2 = tapSys.tapPos
    x = schermata.offset[1]
    x += int(round((p2[1] - p1[1]) / 5))
    if x > schermata.limSup[1]:
        x = schermata.limSup[1]
    elif x < schermata.limInf[1]:
        x = schermata.limInf[1]
    schermata.offset = (0, x)

def sliderClick(fun):
    p = tapSys.tapPos
    o = tapSys.tapDownObj
    l = o.fgOffset[2]        # larghezza dello slider
    diff = (p[0] - o.rect[0], p[1] - o.rect[1])
    # diff[1] : l = x : 100
    # diff[1] * 100 / l
    # fun(val)

# Globale -------------------------------------------------------------------------------

stop = False        # Guardia ciclo principale
idFotoGalleria = None        # Identificativo della prima foto da mostrare in galleria
# Lista di tuple (img, idx, id) dove img è una immagine precaricate della galleria, id il suo identificativo e idx l'indice
#imgGalleria = [(None, -1, -1), (None, -1, -1), (None, -1, -1)]
totaleFoto = 0        # Totale delle foto salvate
stampa = False          # True se c'è una stampa in corso

path = [
    '/home/pi/picam/photo',        # Cartella foto
    '/home/pi/picam/video',        # Cartella Video
    '/home/pi/picam/icone',        # Cartella icone
    '/home/pi/picam/opzioni',        # Cartella opzioni
]

# "Enum" funzioni bottoni 
f_click = 0        # Funzione click
f_dclick = 1        # Funzione doppio click
f_rclick = 2        # Funzione right click
f_muovi = 3        # Funzione muovi oggetto
f_rilascia = 4        # Funzione rilascia oggetto
# "Enum" funzioni schermate
f_smuovi = 0        # Funzione muovi schermata
f_srilascia = 1        # Funzione rilascia schermata

# Inizializza schermate (vuoto)
schermate = Schermate()

# Sistema di gestione dei tap
tapSys = Tap(schermate)

# Frame al secondo
FPS = 30

# Inizializza Framebuffer e Touchscreen (TFT adafruit)
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# Inizializza pygame e lo schermo
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((320, 240), pygame.FULLSCREEN)

# Inizializza la fotocamera
camera = picamera.PiCamera()
atexit.register(camera.close)
camera.resolution = (320, 240)  # Per rendere fluido lo streaming

# "Enum" schermate <- python non ha gli enum...
sid_fotocamera = 0
sid_galleria = 1
sid_cancella = 2
sid_menuFoto = 3

sid_opzFilter = 4
#sid_opzColorEffect = 9
sid_opzExposure = 5
#sid_opzShutterSpeed = 10
sid_opzRotation = 6
sid_opzHflip = 7
sid_opzVflip = 8
sid_opzAwb = 9
sid_opzBrightness = 10
sid_opzContrast = 11
sid_opzSaturation = 12
sid_opzSharpness = 13
sid_opzIso = 14
sid_opzMeter = 15
sid_opzDenoise = 16

sid_reset = 17


'''
sid_menuVideo = 4
sid_menu = 5
sid_menuOpzioni = 6
sid_filtri = 7
sid_rotazione = 8
'''

i_back = Icona(40, 40, fg=imgPath('back'), bg=imgPath('bg4040t'))
ip_back = Icona(40, 40, fg=imgPath('back'))

# Schermata 0 -> fotocamera
s_fotocamera = CameraView (
[BottoneWidget((4, 4, 40, 40), [None, None, None, (navigaCallback, sid_menuFoto), None, None], img=Icona(40,40, fg=imgPath('opzioni'), bg=imgPath('bg4040t')), imgPressed=Icona(40,40, fg=imgPath('opzioni')) ),
 BottoneWidget((275, 4, 40, 40), [None, None, None, (navigaCallback, sid_galleria), None, None], img=Icona(40,40, fg=imgPath('photo'), bg=imgPath('bg_40_40')), imgPressed=Icona(40,40, fg=imgPath('photo')) ),
], [None, None], camera,
 BottoneWidget((130, 196, 60, 40), [None, None, None, (scattaFotoCallback, None), None, None], img=Icona(60,40, fg=imgPath('snap'), bg=imgPath('bg6040t')), imgPressed=Icona(60,40, fg=imgPath('snap_pressed')) )
)

# Schermata 1 -> galleria
s_galleria = Galleria (
[BottoneWidget((0, 0, 40, 192), [None, None, None, (navigaGalleriaCallback, -1), (navigaGalleriaCallback, -1), (navigaGalleriaCallback, -1)], img=Icona(40, 192, bg=imgPath('goleft')) ), # imgPressed=Icona(40, 192, bg=imgPath('goleft'), colore=(100,100,100)) ),
 BottoneWidget((280, 0, 40, 192), [None, None, None, (navigaGalleriaCallback, 1), (navigaGalleriaCallback, 1), (navigaGalleriaCallback, 1)], img=Icona(40, 192, bg=imgPath('goright')) ), # imgPressed=Icona(40, 192, bg=imgPath('goright'), colore=(100,100,100)) ),
 BottoneWidget((272, 196, 40, 40), [None, None, None, (navigaCallback, sid_fotocamera), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((4, 196, 40, 40), [None, None, None, (cancellaCallback, None), None, None], img=Icona(40,40, fg=imgPath('trash'), bg=imgPath('bg4040t')), imgPressed=Icona(40,40, fg=imgPath('trash')) ),
 BottoneWidget((54, 196, 40, 40), [None, None, None, (stampaFotoCallback, None), None, None], img=Icona(40,40, fg=imgPath('print'), bg=imgPath('bg4040t')), imgPressed=Icona(40,40, fg=imgPath('print')) ),
 #BottoneWidget((104, 196, 40, 40), [None, None, None, None, None, None], img=Icona(40,40, fg=imgPath('edit'), bg=imgPath('bg4040t')) ),
 ], [None, None], path[0], screen)

# Schermata 2 -> conferma cancellazione
opz = Icona(320,44, colore=(200, 200, 200))
s_confermaCancella = DeleteView (
[#BottoneWidget((4, 40, 312, 60), [None, None, None, None, None, None], bg='cancella', colore=(0, 255, 255)), #LABEL       # Testo: Cancellare?
 BottoneWidget((30, 60, 120, 120), [None, None, None, (rimuoviFotoCallback, None), (rimuoviFotoCallback, None), None], img=Icona(120,120, fg=imgPath('confermatrash')) ),
 BottoneWidget((170, 60, 120, 120), [None, None, None, (navigaCallback, sid_galleria), (navigaCallback, sid_galleria), None], img=Icona(120,120, fg=imgPath('backtrash')) ),
 ], [None, None])

'''
i_indietro =    Icona(160, 40, bg=imgPath('indietro'),      colore=(  0, 100, 255) )
i_menuFoto =    Icona( 50, 65, bg=imgPath('menu_foto'),     colore=(  0, 200, 100) )
ip_menuFoto =   Icona( 50, 50, bg=imgPath('menu_foto'),     colore=(100, 200, 100) )
i_menuVideo =   Icona( 50, 50, bg=imgPath('menu_video'),    colore=(100,   0, 255) )
ip_menuVideo =  Icona( 50, 50, bg=imgPath('menu_video'),    colore=(100, 200, 100) )
i_menu =        Icona( 50, 50, bg=imgPath('menu_'),         colore=(  0, 200, 255) )
ip_menu =       Icona( 50, 50, bg=imgPath('menu_'),         colore=(100, 200, 100) )
i_menuOpzioni = Icona( 50, 50, bg=imgPath('menu_opzioni'),  colore=(100,   0, 255) )
ip_menuOpzioni = Icona( 50, 50, bg=imgPath('menu_opzioni'),  colore=(100, 200, 255) )
'''

i_left40 = Icona(40, 40, fg=imgPath('goleft4040')) #, bg=imgPath('bg4040t')) ),
i_right40 = Icona(40, 40, fg=imgPath('goright4040'))
i_left140 = Icona(40, 140, bg=imgPath('goleft40140'))
i_right140 = Icona(40, 140, bg=imgPath('goright40140'))
i_inc120 = Icona(40, 120, fg=imgPath('incrementa'), bg=imgPath('bg4040t'))
i_dec120 = Icona(40, 120, fg=imgPath('decrementa'), bg=imgPath('bg4040t'))

#iso exit colorbalance effects rotation shutter


# Schermata 3 -> Menù Foto
s_menuFoto = MenuView (
[
 BottoneWidget((  4,  4,308, 50), [None, None, None, (navigaCallback, sid_opzFilter), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('effects')), img=LeftIcona(308, 50, fg=imgPath('effects')) ),
 BottoneWidget((  4, 58,308, 50), [None, None, None, (navigaCallback, sid_opzRotation), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('rotation')), img=LeftIcona(308, 50, fg=imgPath('rotation')) ),
 BottoneWidget((  4,112,308, 50), [None, None, None, (navigaCallback, sid_opzExposure), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('shutter')), img=LeftIcona(308, 50, fg=imgPath('shutter')) ),
 BottoneWidget((  4,166,308, 50), [None, None, None, (navigaCallback, sid_opzAwb), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('colorbalance')), img=LeftIcona(308, 50, fg=imgPath('colorbalance')) ),
 BottoneWidget((  4,220,308, 50), [None, None, None, (navigaCallback, sid_opzIso), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('iso')), img=LeftIcona(308, 50, fg=imgPath('iso')) ),
 BottoneWidget((  4,274,308, 50), [None, None, None, (navigaCallback, sid_opzMeter), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('other')), img=LeftIcona(308, 50, fg=imgPath('other')) ),
 BottoneWidget((  4,328,308, 50), [None, None, None, (navigaCallback, sid_reset), None, None], float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('reset')), img=LeftIcona(308, 50, fg=imgPath('reset')) ),
 BottoneWidget((  4,382,308, 50), [None, None, None, (exitCallback, None), None, None], img=LeftIcona(308, 50, fg=imgPath('exit')), float='True', imgPressed=LeftIcona(308, 50, colore=(195,176,145), fg=imgPath('exit')) ),
 
 BottoneWidget((272, 196, 40, 40), [None, None, None, (navigaCallback, sid_fotocamera), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((316,  0,  4,240), [None, None, None, None, None, None], img=Icona(4,240, colore=(150,150,150)) ),
 ], [scroll, None], limI=(0, -200), limS=(0, 0))
 
# Schermata 4 -> Effetti macchina fotografica
l_filter = [
    ('none', 'No effect'), ('negative', 'Negative'), ('solarize', 'Solarize'), ('sketch', 'Sketch'), 
    ('denoise', 'Denoise'), ('emboss', 'Emboss'), ('oilpaint', 'Oil paint'), ('hatch', 'Hatch'), 
    ('gpen', 'Gpen'), ('pastel', 'Pastel'), ('watercolor', 'Watercolor'), ('film', 'Film'), 
    ('blur', 'Blur'), ('colorswap', 'Color swap'), ('washedout', 'Washedout'), 
    ('posterise', 'Posterise'), ('cartoon', 'Cartoon')
# 'colorpoint', 'colorbalance', 'saturation', 'deinterlace1', 'deinterlace2'
]
s_opzFilter = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 #BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, 3), None, None], img=i_left40 ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzExposure), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_image_effect, l_filter, 17, Opz.image_effect) )

# Schermata 5 -> Exposure mode
l_exposure = [
    ('off', 'Off'), ('auto', 'Auto'), ('night', 'Night'), ('nightpreview', 'Night preview'), 
    ('backlight', 'Backlight'), ('spotlight', 'Spotlight'), ('sports', 'Sports'), 
    ('snow', 'Snow'), ('beach', 'Beach'), ('verylong', 'Very long'), ('fixed fps', 'Fixedfps'), 
    ('antishake', 'Antishake'), ('fireworks', 'Fireworks')
]
s_opzExposure = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzFilter), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzRotation), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_exposure_mode, l_exposure, 13, Opz.exposure_mode) )

# Schermata 6 -> Rotation
l_rotation = [
    (0, '0'), (90, '90'), (180, '180'), (270, '270') 
]
s_rotation = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzExposure), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzHflip), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_rotation, l_rotation, 4, Opz.rotation) )

# Schermata 7 -> Hflip
s_hflip = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzRotation), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzVflip), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((135, 110, 50, 65), [None, None, None, (pressOptButtonCallback, None), None, None]),
 ], [None, None], camera,
TwoValueOption(CID_hflip, (True, 'On'), (False, 'Off'), 0 if Opz.hflip else 1) )

# Schermata 8 -> Vflip
s_vflip = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzHflip), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzAwb), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((135, 110, 50, 65), [None, None, None, (pressOptButtonCallback, None), None, None]),
 ], [None, None], camera,
TwoValueOption(CID_vflip, (True, 'On'), (False, 'Off'), 0 if Opz.vflip else 1) )

# Schermata 9 -> Awb mode
l_awb = [
    ('off', 'Off'), ('auto', 'Auto'), ('sunlight', 'Sunlight'), ('cloudy', 'Cloudy'), 
    ('shade', 'Shade'), ('tungsten', 'Tungsten'), ('fluorescent', 'Fluorescent'), 
    ('incandescent', 'Incandescent'), ('flash', 'Flash'), ('horizon', 'Horizon'), 
]
s_opzAwb = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzVflip), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzBrightness), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_awb_mode, l_awb, 10, Opz.awb_mode) )

# Schermata 10 -> Brightness
s_brightness = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzAwb), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzContrast), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 75, 40, 120), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_dec120 ),
 BottoneWidget((280, 75, 40, 120), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_inc120 ),
 ], [None, None], camera,
SliderOption(CID_brightness, 0, 100, Opz.brightness) )

# Schermata 11 -> Contrast
s_contrast = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzBrightness), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzSaturation), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 75, 40, 120), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_dec120 ),
 BottoneWidget((280, 75, 40, 120), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_inc120 ),
 ], [None, None], camera,
SliderOption(CID_contrast, -100, 100, Opz.contrast) )

# Schermata 12 -> Saturation
s_saturation = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzContrast), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzSharpness), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 75, 40, 120), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_dec120 ),
 BottoneWidget((280, 75, 40, 120), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_inc120 ),
 ], [None, None], camera,
SliderOption(CID_saturation, -100, 100, Opz.saturation) )

# Schermata 13 -> Sharpness
s_sharpness = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzSaturation), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzIso), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 75, 40, 120), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_dec120 ),
 BottoneWidget((280, 75, 40, 120), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_inc120 ),
 ], [None, None], camera,
SliderOption(CID_sharpness, -100, 100, Opz.sharpness) )

# Schermata 14 -> ISO
l_iso = [
    (0, 'Auto'), (100, '100'), (200, '200'), (320, '320'), 
    (400, '400'), (500, '500'), (640, '640'), (800, '800')
]
s_opzIso = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzSharpness), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzMeter), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_iso, l_iso, 8, Opz.iso) )

# Schermata 15 -> Meter mode
l_meter = [
    ('average', 'Average'), ('spot', 'Spot'), ('backlit', 'Backlit'), ('matrix', 'Matrix')
]
s_opzMeter = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzIso), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzDenoise), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((0, 49, 40, 140), [None, None, None, (navigaOptValueCallback, -1), (navigaOptValueCallback, -1), (navigaOptValueCallback, -1)], img=i_left140 ),
 BottoneWidget((280, 49, 40, 140), [None, None, None, (navigaOptValueCallback, 1), (navigaOptValueCallback, 1), (navigaOptValueCallback, 1)], img=i_right140 ),
 ], [None, None], camera,
ListOption(CID_meter_mode, l_meter, 4, Opz.meter_mode) )

# Schermata 16 -> Image Denoise
s_denoise = CameraOptionView (
[BottoneWidget((272, 196, 40, 40), [None, None, None, (backToOptionCallback, None), None, None], img=i_back, imgPressed=ip_back ),
 BottoneWidget((0, 6, 40, 40), [None, None, None, (navigaCallback, sid_opzMeter), None, None], img=i_left40 ),#, bg=imgPath('bg4040t')) ),
 #BottoneWidget((280, 6, 40, 40), [None, None, None, (navigaCallback, 17), None, None], img=i_right40 ),#, bg=imgPath('bg4040t')) ),
 BottoneWidget((135, 110, 50, 65), [None, None, None, (pressOptButtonCallback, None), None, None]),
 ], [None, None], camera,
TwoValueOption(CID_image_denoise, (True, 'On'), (False, 'Off'), 0 if Opz.image_denoise else 1) )

# Schermata 17 -> conferma reset
opz = Icona(320,44, colore=(200, 200, 200))
s_confermaReset = DeleteView (
[#BottoneWidget((4, 40, 312, 60), [None, None, None, None, None, None], bg='cancella', colore=(0, 255, 255)), #LABEL       # Testo: Cancellare?
 BottoneWidget((30, 60, 120, 120), [None, None, None, (resetCallback, sid_menuFoto), None, None], img=Icona(120,120, fg=imgPath('confermareset')) ),
 BottoneWidget((170, 60, 120, 120), [None, None, None, (navigaCallback, sid_menuFoto), None, None], img=Icona(120,120, fg=imgPath('backtrash')) ),
 ], [None, None])

# Lista di schermate, ogni schermata contiene una serie di widget presenti in quella schermata.
schermate.inizializza([
    s_fotocamera, s_galleria, s_confermaCancella, s_menuFoto, 
    s_opzFilter, s_opzExposure, s_rotation, s_hflip, s_vflip, 
    s_opzAwb, s_brightness, s_contrast, s_saturation, s_sharpness,
    s_opzIso, s_opzMeter, s_denoise, s_confermaReset
])

# Inizializzazione ----------------------------------------------------------------------

# Inizializza l'identificativo della prossima foto da salvare
nextFotoId = getImageId()
# Inizializza galleria foto
s_galleria.inizializza()


# Ciclo principale ----------------------------------------------------------------------
while(not(stop)):
    
    # Gestione tempo
    currentTime = int(round(time.time() * 1000))
    # Test timer
    tapSys.timerTest(currentTime)
    # Gestione FPS
    pygame.time.Clock().tick(FPS)
    
    # Disegna
    schermate.draw(screen)
    if stampa:
        #screen.blit
        font = pygame.font.Font(None, 30)
        text = font.render('Printing', 1, (100,80,80))
        screen.blit(text, (195,215))
    pygame.display.flip()        # Aggiorna tutto lo schermo -> stream camera
    
    # Gestione degli eventi
    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
            tapSys.onMouseDown(pos)
        if(event.type is MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            tapSys.onMouseUp(pos)
        if(event.type is MOUSEMOTION):
            pos = pygame.mouse.get_pos()
            tapSys.onMouseMove(pos)
        elif (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
            stop = True
            break

print "Bye" #"Tenna ento lye omenta"
