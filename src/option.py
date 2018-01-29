# -*- coding: utf-8 -*-

'''
Created on 18/dic/2015

@author: Niccolò Pieretti

@todo: 

# Opzioni -----------
TROPPE!!
-- List --
>> iso
>> exposure_mode
>> meter_mode
>> awb_mode
>> image_effect
>> rotation

-- Slider --
>> color_effects [Limiti]
>> shutter_speed [0,+inf)

>> brightness 0 and 100
>> contrast -100 and 100 [0 default]
>> saturation -100 and 100 [0 defaults]
>> sharpness -100 and 100 [0 defaults]

-- Two value --
>> image_denoise
>> hflip
>> vflip


camera.sharpness = 0
camera.contrast = 0
camera.brightness = 50
camera.saturation = 0
camera.ISO = 0
camera.video_stabilization = False
camera.exposure_compensation = 0
camera.exposure_mode = 'auto'
camera.meter_mode = 'average'
camera.awb_mode = 'auto'
camera.image_effect = 'none'
camera.color_effects = None
camera.rotation = 0
camera.hflip = False
camera.vflip = False
camera.crop = (0.0, 0.0, 1.0, 1.0)




>> ISO Valid values are between 0 (auto) and 800. [100, 200, 320, 400, 500, 640, 800]
        The default value is 0 which means the ISO is automatically set according to image-taking conditions.
        With ISO settings other than 0 (auto), the exposure_mode property becomes non-functional.
>> exposure_mode -> The default value is 'auto'.
        ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks']

-- SLIDER --
>> color_effects -> returns None which indicates that the camera is using normal color settings, 
                                        or a (u, v) tuple where u and v are integer values between 0 and 255.
        For example, to make the image black and white set the value to (128, 128). The default value is None.

-- FIX --
>> meter_mode -> ['average', 'spot', 'backlit', 'matrix'] The default value is 'average'. 
>> image_denoise -> correzione errori, The default value is False.

>> shutter_speed -> tempo di esposizione, the shutter speed of the camera in microseconds, or 0 which indicates that the speed will be automatically determined by the auto-exposure algorithm. The default value is 0 (auto).
>> awb_mode -> bilanciamento del bianco ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']




# NO ---------------
>> Resolution -> defaults to 1280x720 (720p).
>> Dimensione immagine + crop
>> Formato immagine -> fisso su jpg, gli altri formati creano complicazioni
>> preview_alpha -> value between 0 and 255 indicating the opacity of the preview window, where 0 is completely transparent and 255 is completely opaque. The default value is 255.


 
'''
import errno
import os
import pygame.draw
import string

from view import Schermata 
from util import write_center_text, write_right_text, blit_alpha
from widget import Icona

#Esposizione V
CID_exposure_mode   = 0
CID_shutter_speed   = 6

#ISO V
CID_iso             = 1

#Meter mode V
CID_meter_mode      = 2


#Effetti
CID_image_effect    = 4
CID_color_effects   = 5

# Gestione colori V
CID_brightness      = 7
CID_contrast        = 8
CID_saturation      = 9
CID_sharpness       = 10
#Bilanciamento del bianco
CID_awb_mode        = 3

#Riduzione rumore
CID_image_denoise   = 11

# Rotazioni varie V
CID_rotation        = 12
CID_hflip           = 13
CID_vflip           = 14

# Nome dell'opzione
optionName = ['Exposure Mode', 
              'ISO', 
              'Meter Mode', 
              'AWB Mode', 
              'Image Effect', 
              'Color Effects', 
              'Shutter Speed', 
              'Brightness', 
              'Contrast', 
              'Saturation', 
              'Sharpness', 
              'Image Denoise', 
              'Rotation', 
              'Horizontal Flip', 
              'Vertical Flip']
        
opz = None
opzMini = None
onImg = None
offImg = None
sliderBall = None

pathOption = '/home/pi/picam/opzioni'

class Opz():
    # Per poterli accedere da fuori
    exposure_mode = 'auto'
    iso           = 0
    meter_mode    = 'average'
    awb_mode      = 'auto'
    image_effect  = 'none'
    color_effects = 0
    shutter_speed = 0
    brightness    = 50
    contrast      = 0
    saturation    = 0
    sharpness     = 0
    image_denoise = False
    rotation      = 90
    hflip         = False
    vflip         = False
    
def reset(camera):
    print "RESET"
    setOption(CID_exposure_mode, 'auto', camera)
    setOption(CID_iso, 0, camera)
    setOption(CID_meter_mode, 'average', camera)
    setOption(CID_awb_mode, 'auto', camera)
    setOption(CID_image_effect, 'none', camera)
    #setOption(CID_color_effects, 0, camera)
    setOption(CID_shutter_speed, 0, camera)
    setOption(CID_brightness, 50, camera)
    setOption(CID_contrast, 0, camera)
    setOption(CID_saturation, 0, camera)
    setOption(CID_sharpness, 0, camera)
    setOption(CID_image_denoise, False, camera)
    setOption(CID_rotation, 90, camera)
    setOption(CID_hflip, False, camera)
    setOption(CID_vflip, False, camera)
    salvaOpzioni()
    

def setOption(option, value, camera):
    if      option == CID_exposure_mode : camera.exposure_mode  = Opz.exposure_mode  = value
    elif    option == CID_iso           : camera.iso            = Opz.iso            = value
    elif    option == CID_meter_mode    : camera.meter_mode     = Opz.meter_mode     = value
    elif    option == CID_awb_mode      : camera.awb_mode       = Opz.awb_mode       = value
    elif    option == CID_image_effect  : camera.image_effect   = Opz.image_effect   = value
    elif    option == CID_color_effects : camera.color_effects  = Opz.color_effects  = value
    elif    option == CID_shutter_speed : camera.shutter_speed  = Opz.shutter_speed  = value
    elif    option == CID_brightness    : camera.brightness     = Opz.brightness     = value
    elif    option == CID_contrast      : camera.contrast       = Opz.contrast       = value
    elif    option == CID_saturation    : camera.saturation     = Opz.saturation     = value
    elif    option == CID_sharpness     : camera.sharpness      = Opz.sharpness      = value
    elif    option == CID_image_denoise : camera.image_denoise  = Opz.image_denoise  = value
    elif    option == CID_rotation      : camera.rotation       = Opz.rotation       = value
    elif    option == CID_hflip         : camera.hflip          = Opz.hflip          = value
    elif    option == CID_vflip         : camera.vflip          = Opz.vflip          = value
    #elif    option == CID_    : camera. = value

def salvaOpzioni():    
    if not os.path.isdir(pathOption[3]):
        try:    # Se non esiste, crea la cartella
            os.makedirs(pathOption)
            # Set new directory ownership to pi user, mode to 755
            os.chmod(pathOption,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | 
                stat.S_IRGRP | stat.S_IXGRP | 
                stat.S_IROTH | stat.S_IXOTH)
        except OSError as e:
            print errno.errorcode[e.errno]
    pathfile = pathOption + '/opt.txt'    # cartella_opzioni/opt.txt
    try:
        # apri/crea il file
        out_fileopt = open(pathfile, 'w')
        # salva le opzioni
        out_fileopt.write('Exposure mode: ' + str(Opz.exposure_mode) + '\n')
        out_fileopt.write('ISO: ' + str(Opz.iso) + '\n')
        out_fileopt.write('Meter mode: ' + str(Opz.meter_mode) + '\n')
        out_fileopt.write('AWB mode: ' + str(Opz.awb_mode) + '\n')
        out_fileopt.write('Image effect: ' + str(Opz.image_effect) + '\n')
        out_fileopt.write('Color effects: ' + str(Opz.color_effects) + '\n')
        out_fileopt.write('Shutter speed: ' + str(Opz.shutter_speed) + '\n')
        out_fileopt.write('Brightness: ' + str(Opz.brightness) + '\n')
        out_fileopt.write('Contrast: ' + str(Opz.contrast) + '\n')
        out_fileopt.write('Saturation: ' + str(Opz.saturation) + '\n')
        out_fileopt.write('Sharpness: ' + str(Opz.sharpness) + '\n')
        out_fileopt.write('Image denoise: ' + str(Opz.image_denoise) + '\n')
        out_fileopt.write('Horizontal flip: ' + str(Opz.hflip) + '\n')
        out_fileopt.write('Vertical flip: ' + str(Opz.vflip) + '\n')
        out_fileopt.write('Rotation: ' + str(Opz.rotation) + '\n')
    except OSError as e:
        print errno.errorcode[e.errno]
    finally:
        # chiudi il file
        out_fileopt.close()
    
def caricaOpzioni(camera):
    pathfile = pathOption + '/opt.txt'    # cartella_opzioni/opt.txt
    try:
        in_fileopt = open(pathfile, 'r')     
        for linea in in_fileopt.readlines():
            p = string.find(linea, ':')
            chiave = linea[:p]
            valore = linea[(p + 2):(len(linea) - 1)]
            if   chiave == 'Exposure mode'  : camera.exposure_mode   = Opz.exposure_mode   = str(valore)
            elif chiave == 'ISO'            : camera.iso             = Opz.iso             = int(valore)
            elif chiave == 'Meter mode'     : camera.meter_mode      = Opz.meter_mode      = str(valore)
            elif chiave == 'AWB mode'       : camera.awb_mode        = Opz.awb_mode        = str(valore)
            elif chiave == 'Image effect'   : camera.image_effect    = Opz.image_effect    = str(valore)
            #elif chiave == 'Color effects'  : camera.color_effects   = Opz.color_effects   = str(valore)
            elif chiave == 'Shutter speed'  : camera.shutter_speed   = Opz.shutter_speed   = int(valore)
            elif chiave == 'Brightness'     : camera.brightness      = Opz.brightness      = int(valore)
            elif chiave == 'Contrast'       : camera.contrast        = Opz.contrast        = int(valore)
            elif chiave == 'Saturation'     : camera.saturation      = Opz.saturation      = int(valore)
            elif chiave == 'Sharpness'      : camera.sharpness       = Opz.sharpness       = int(valore)
            elif chiave == 'Image denoise'  : camera.image_denoise   = Opz.image_denoise   = True if valore == 'True' else False
            elif chiave == 'Rotation'       : camera.rotation        = Opz.rotation        = int(valore)
            elif chiave == 'Horizontal flip': camera.hflip           = Opz.hflip           = True if valore == 'True' else False
            elif chiave == 'Vertical flip'  : camera.vflip           = Opz.vflip           = True if valore == 'True' else False
    except OSError as e:
        print errno.errorcode[e.errno]
    finally:
        in_fileopt.close()   


class Option():
    '''
        Strettamente legato alle opzioni
    '''  
    def __init__(self, idopz):
        self.id = idopz
    
    def next(self):
        pass
    
    def prec(self):
        pass
    
    def onMouseDown(self, pos):
        pass
    
    def onMouseUp(self, pos):
        pass
        
    def onMouseMove(self, pos, camera):
        pass
    
    def Click(self, pos):
        pass
    
    def RightClick(self, pos):
        pass
    
    def DoubleClick(self, pos):
        pass
    
    def draw(self, screen):
        pass


class ListOption(Option):
  
    def __init__(self, idopz, values, limit, current = 0):
        global opz, opzMini
        Option.__init__(self, idopz)
        self.valuesList = values    # Lista di coppie (Nome Valore, Valore assunto) dell'opzione
        self.limit = limit          # Lunghezza di values
        self.current = 0            # Indice del valore corrente
        find = False
        for v in values:
            if str(v[0]) == str(current):
                find = True
                break
            else: 
                self.current += 1
        if not find: self.current = 0
        opz = Icona(320,44, colore=(200, 200, 200))
        opzMini = Icona(320,24, colore=(200, 200, 200))
    
    def next(self, camera):
        self.current = (self.current + 1) % self.limit
        setOption(self.id, self.valuesList[self.current][0], camera)
    
    def prec(self, camera):
        self.current = (self.current - 1) % self.limit
        setOption(self.id, self.valuesList[self.current][0], camera)
    
    def draw(self, screen):
        blit_alpha(screen, opz.surface, (0,4), 150)
        write_center_text(optionName[self.id], 40, (0,0,0), screen, 9)
        blit_alpha(screen, opzMini.surface, (0,50), 150)
        string = self.valuesList[self.current][1]
        write_center_text(string, 30, (0,0,0), screen, 50)
        string= '[' + str(self.current+1) + '/' + str(self.limit) + ']'
        write_right_text(string, 30, (0,0,0), screen, 50)

class SliderOption(Option):
    
    def __init__(self, idopz, inf, sup, current = 0):
        global opz, opzMini, sliderBall
        Option.__init__(self, idopz)
        self.inf = inf      # Limite inferiore
        self.sup = sup      # Limite superiore
        self.current = current      # Valore corrente
        
        self.sliderInf = 60
        self.sliderSup = 260
        
        sliderBall = Icona(20,20, fg='/home/pi/picam/icone/sliderball.png')
        opz = Icona(320,44, colore=(200, 200, 200))
        opzMini = Icona(320,24, colore=(200, 200, 200))
        
        self.mouseDown = False
        self.currentPosX = self.fromValToPos(current)

    
    def fromPosToVal(self, pos):
        if pos <= self.sliderInf:    return self.inf
        if pos >= self.sliderSup:   return self.sup
        posx = pos - self.sliderInf
        range = self.sup - self.inf
        val = int( posx * range / 200 ) + self.inf
        # pos : larghezza self.slider = current : range totale
        # current = range * pos / larghezza
        return val
    
    def fromValToPos(self, val):
        if val <= self.inf: return self.sliderInf
        if val >= self.sup: return self.sliderSup 
        value = val - self.inf
        range = self.sup - self.inf
        pos = int( (200 * value) / range ) + self.sliderInf
        return pos
    
    def update(self, x, camera):
        if self.sliderInf > x:
            self.currentPosX = self.sliderInf
        elif self.sliderSup < x:
            self.currentPosX = self.sliderSup
        else:
            self.currentPosX = x
        self.current = self.fromPosToVal(x)
        setOption(self.id, self.current, camera)
    
    def next(self, camera):
        self.current = self.current + 1 if self.current < self.sup else self.sup
        self.currentPosX = self.fromValToPos(self.current) 
        setOption(self.id, self.current, camera)
    
    def prec(self, camera):
        self.current = self.current - 1 if self.current > self.inf else self.inf
        self.currentPosX = self.fromValToPos(self.current)
        setOption(self.id, self.current, camera)
        
    def onMouseDown(self, pos):
        if self.sliderInf <= pos[0] <= self.sliderSup and 130 <= pos[1] <= 170:
            self.mouseDown = True
        #self.update(pos[0])
    
    def onMouseUp(self, pos):
        #if self.mouseDown:
        #    self.update(pos[0])
        self.mouseDown = False
        
    def onMouseMove(self, pos, camera):
        if self.mouseDown:
            self.update(pos[0], camera)
    
    def draw(self, screen):
        blit_alpha(screen, opz.surface, (0,4), 150)
        write_center_text(optionName[self.id], 40, (0,0,0), screen, 9)
        
        # Slider
        pygame.draw.line(screen, (80,80,80), (self.sliderInf,135), (self.sliderSup,135), 10)
        pygame.draw.line(screen, (10,200,200), (self.sliderInf+1,135), (self.currentPosX,135), 8)
        pygame.draw.line(screen, (200,200,200), (self.currentPosX,135), (self.sliderSup-1,135), 8)
        
        screen.blit(sliderBall.surface, (self.currentPosX-10, 125))
        #pygame.draw.circle(screen, (90,90,90), (self.currentPosX, 135), 15, 15)
        #pygame.draw.circle(screen, (200,200,200), (self.currentPosX, 135), 12, 10)

        blit_alpha(screen, opzMini.surface, (0,50), 150)
        string = str(self.current)
        write_center_text(string, 30, (0,0,0), screen, 50)
        '''    >> Nome Opzione
                > Current value
                /> Interaction -> view
        '''

class TwoValueOption(Option):
    
    def __init__(self, idopz, on, off, current = 0):
        global opz, opzMini, onImg, offImg
        Option.__init__(self, idopz)
        self.values = (on, off)
        self.current = current      # Valore corrente
        onImg = Icona(50,50, fg='/home/pi/picam/icone/on.png')
        offImg = Icona(50,50, fg='/home/pi/picam/icone/off.png')
        
        opz = Icona(320,44, colore=(200, 200, 200))
        opzMini = Icona(320,24, colore=(200, 200, 200))        
    
    def press(self, camera):
        self.current = (self.current + 1) % 2
        setOption(self.id, self.values[self.current][0], camera)
    
    def draw(self, screen):
        blit_alpha(screen, opz.surface, (0,4), 150)
        write_center_text(optionName[self.id], 40, (0,0,0), screen, 9)
        
        # Button
        if self.current == 0:
            screen.blit(offImg.surface, (135,125))
            screen.blit(onImg.surface, (135,110))
            #pygame.draw.circle(screen, (90,90,90), (160, 135), 20, 20)
            #pygame.draw.circle(screen, (10,200,200), (160, 135), 16, 14)
        else:
            screen.blit(onImg.surface, (135,110))
            screen.blit(offImg.surface, (135,125))
            #pygame.draw.circle(screen, (90,90,90), (160, 135), 20, 20)
            #pygame.draw.circle(screen, (200,200,200), (160, 135), 16, 14)

        blit_alpha(screen, opzMini.surface, (0,50), 150)
        string = str(self.values[self.current][1])
        write_center_text(string, 30, (0,0,0), screen, 50)
        '''    >> Nome Opzione
                > Current value
                /> Interaction -> view
        '''