# -*- coding: utf-8 -*-

'''
Created on 03/set/2015

@author: Niccolò Pieretti

@todo:
'''

class Immagine():
    
    def __init__(self, img, nome):
        self.img = img # immagine
        self.nome = nome # nome dell'immagine (IMG_nome.jpg)

class ListaImmagini():

    def __init__(self, img=None, leftIndex=-1):
        ''' Crea una lista di immagini, contenente img se non None, vuota altrimenti '''
        self.struct = [img, None, None, None, None, None, None]
        if img is None:
            self.attiva = -1
        else:
            self.attiva = 0
        self.leftIndex = leftIndex # indice nella galleria dell'immagine più a sinistra (ovvero è l'i-esima foto della cartella)
    
    def scorriSinistra(self):
        ''' Sposta, idealmente, il puntatore dell'immagine attiva a sinistra '''
        if self.attiva > 0 and self.attiva < 7:
            if self.struct[self.attiva - 1] is not None:
                self.attiva -= 1
                return True
        return False
    
    def scorriDestra(self):
        ''' Sposta, idealmente, il puntatore dell'immagine attiva a destra '''
        if self.attiva >= -1 and self.attiva < 6:
            if self.struct[self.attiva + 1] is not None:
                self.attiva += 1
                return True
        return False
    
    def aggiungiDaSinistra(self, img):
        ''' Aggiunge una immagine, da sinistra, alla struttura '''
        if img is not None:
            if self.struct[0] is None:
                # struttura vuota
                self.struct[0] = img
                self.attiva = 0
                self.leftIndex -= 1
                return
            for i in range(6,0,-1): # [6, 5, 4, 3, 2, 1]
                # shift
                self.struct[i] = self.struct[i-1]
            self.struct[0] = img
            self.leftIndex -= 1 #?
        return
    
    def aggiungiDaDestra(self, img):
        ''' Aggiunge una immagine, da destra, alla struttura '''
        if img is not None:
            if self.struct[0] is None:
                # struttura vuota
                self.struct[0] = img
                self.attiva = 0
                self.leftIndex += 1
                return
            for i in range(0,7): # [0, 1, 2, 3, 4, 5, 6]
                if self.struct[i] is None:
                    # al primo None si ferma
                    self.struct[i] = img
                    self.scorriDestra()
                    return
            # se non trova spazi liberi, shifta
            for i in range(0,6): # [0, 1, 2, 3, 4, 5]
                self.struct[i] = self.struct[i+1]
            self.struct[6] = img
            self.leftIndex += 1 #?
        return
    
    def elimina(self): #?
        if 0 <= self.attiva < 7:
            deleted = self.struct[self.attiva]
            #ricompatta verso sinistra
            if 0 <= self.attiva <= 5:
                for i in range (self.attiva, 6): # [n, n+1, ... , 5]
                    self.struct[i] = self.struct[i+1]
            if self.attiva <= 6:
                self.struct[6] = None
            # self.attiva rimane invariato (di conseguenza prende l'immagine a destra) a meno che non sia None
            while self.attiva >= 0 and self.struct[self.attiva] is None:
                self.attiva -= 1
            if self.struct[0] is None:
                #self.aggiungiDaSinistra(self, img, leftIndex=0)
                self.leftIndex = -1

    def firstId(self):
        for i in range(0,7): # [0, 1, 2, 3, 4, 5, 6]
            if self.struct[i] is not None:
                return self.struct[i].nome
        return None

    def lastId(self):
        for i in range(6,-1,-1): # [6, 5, 4, 3, 2, 1, 0]
            if self.struct[i] is not None:
                return self.struct[i].nome
        return None
    
    def size(self):
        s = 0
        for i in range(0,7): # [0, 1, 2, 3, 4, 5, 6]
            if self.struct[i] is not None:
                s += 1
        return s
    
    def currentIndex(self):
        if self.struct[self.attiva] is not None:
            return self.leftIndex + self.attiva
        return -1
    
    def getCurrentImg(self):
        if 0 <= self.attiva < 7:
            return self.struct[self.attiva]
        return None
