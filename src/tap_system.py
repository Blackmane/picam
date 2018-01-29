# -*- coding: utf-8 -*-

'''
Created on 01/set/2015

@author: Water
'''

import time

def distanza(punto1, punto2):
    dx = abs(punto1[0] - punto2[0])
    dy = abs(punto1[1] - punto2[1])
    if dy > dx:
        return (0.41) * dx + (0.941246) * dy
    else:
        return (0.941246) * dx + (0.41) * dy

class Tap:
    '''
        Obiettivo di Tap è quello di estendere gli eventi del mouse, introducendo il doppio click,
        il click destro e il trascinamento
    '''
    
    def __init__(self, s, **args):
        self.schermate = s      # Lista delle schermate
        #self.idxS = 0    # Indice schermata corrente
        self.times = (250, 2000)    # Click Time e Press Time
        self.stato = 0
        # Decrivono lo stato iniziale 0
        self.tapDown = False        # Vero se c'è un tap in corso
        self.tapMove = False        # Vero se c'è stato un movimento dal primo tap
        self.pressTimer = -1        # Timer del tasto premuto
        self.doppioClickTimer = -1  # Timer per gestire il click singolo e doppio
        self.rightTap = False       # Vero se è nello stato "right click"
        self.tapPos = (0, 0)        # Posizione del tap
        # Utilità al tap
        #self.tapDownObj = None    # Oggetto cliccato per primo
        self.tapDownPos = None    # Posizione cliccata per prima
        #self.tapMoveObj = None    # ? 
        self.tapMovePos = None    # Ultima posizione mossa
        self.lastTime = int(round(time.time() * 1000))
    
    # def tapOggetto(self, punto, Funzione) -> esempio: funzione evidenzia
    #def tapOggetto(self, punto): 
    #    ''' Restituisce l'oggetto su cui è posizionato il mouse. '''
    #    return self.schermate.contiene(punto)

    
    def timerStart(self, i):
        self.lastTime = int(round(time.time() * 1000))
        if i == 0:    # (250, 2000) (Click Time, Press Time)
            self.doppioClickTimer = self.times[0]
        elif i == 1:
            self.pressTimer = self.times[1]
    
    def timerStop(self):
        self.doppioClickTimer = -1
        self.pressTimer = -1
    
    def timerTest(self, currentTime):
        d = currentTime - self.lastTime
        self.lastTime = currentTime    
        # if self.doppioClickTimer >= 0: 
        if self.stato == 4:
        # Se nello stato 4    
            self.doppioClickTimer -= d
            if self.doppioClickTimer <= 0:
                # Da stato 4 a stato 0 -> CLICK
                self.doppioClickTimer = -1
                self.schermate.Click(self.tapPos)
                self.stato = 0
        if self.pressTimer >= 0: 
            # Se nello stato 1     
            self.pressTimer -= d
            if self.pressTimer <= 0: 
            # Da stato 1 a stato 3
                self.pressTimer = -1
                self.rightTap = True
                self.stato = 3
    
    def onMouseDown(self, punto):
        self.tapPos = punto
        self.schermate.onMouseDown(punto)
        # if self.doppioClickTimer >= 0: 
        if self.stato == 4:
        # Da stato 4 a stato 0 -> DOPPIOCLICK"
            self.doppioClickTimer = -1
            #self.tapDownObj = self.tapOggetto(punto)    #?
            #self.schermate.DoubleClick(self.tapDownPos)
            self.schermate.DoubleClick(punto) #? perché?, perché non self.tapDownPos?
            self.tapDownPos = punto
            print "DOUBLECLICK"
            self.stato = 0
        else:
            # Da stato 0 a stato 1
            self.tapDown = True
            self.timerStart(1)
            self.schermate.onMouseDown(punto)
            self.tapDownPos = punto
            self.tapMovePos = punto
            self.stato = 1
    
    def onMouseMove(self, punto):
        #print "onMouseMove" # Chiama a randa...
        if self.tapDown:    # evita problemi con l'uso di un mouse usb
            dis = distanza(punto, self.tapDownPos)
            diff = (punto[0] - self.tapDownPos[0], punto[1] - self.tapDownPos[1])
            # SE il movimento è stato un movimento consistente
            if dis > 5: # OR siamo durante un movimento
                #print "on[consistent]MouseMove"
                self.tapPos = punto
                if self.rightTap:
                    # Da stato 5 a stato 5
                    # Da stato 3 a stato 5
                    self.schermate.onMouseMove(punto)
                    self.stato = 5
                else:
                    # Da stato 1 a stato 2
                    # Da stato 2 a stato 2
                    self.pressTimer = -1
                    self.schermate.muovi() #?
                    self.schermate.onMouseMove(punto) #?
                    self.stato = 2
                self.tapMovePos = punto
                self.tapMove = True
    
    def onMouseUp(self, punto):
        self.tapPos = punto
        self.schermate.onMouseUp(punto)
        if self.rightTap:
            # Da stato 3 a 0
            # Da stato 5 a 0
            #if self.tapDownObj is not None:
            #    self.tapDownObj.onMouseUp(punto)
                #self.tapDownObj.esegui(f_rilascia)
            self.schermate.onMouseUp(punto)
            self.stato = 0
        else:
            # if self.pressTimer >= 0:
            if self.stato == 1:
                # Da stato 1 a 4
                self.pressTimer = -1
                self.timerStart(0)
                self.stato = 4
            else:
                # Da stato 2 a 0
                self.schermate.rilascia()
                self.schermate.onMouseUp(punto)
                self.stato = 0
        self.tapDown = False
        self.tapMove = False
        self.rightTap = False
        # self.tapDownObj = None
        self.tapDownPos = None
        self.tapMovePos = None
        # self.schermate.offset = (0, 0)
'''
self.tapDownObj.DoubleClick(punto)
self.tapDownObj.RightClick(punto)
self.tapDownObj.Click(punto)
self.tapDownObj.onMouseUp(punto)
self.tapDownObj.onMouseDown(punto)
self.tapDownObj.onMouseMove(punto)
'''