#!/usr/bin/env python3
# created by Ahmed G on 26/03/2021
from src.filelist import main
from src.options import timeout, directories
import os, time, sys, pickle
from src.message import send, receive, alarm,verbose
from pathlib import Path


def pickling(content):
    dump = pickle.dumps(content)
    pack = memoryview(dump)
    return pack

def cleaner(name,pattern=''):
    if pattern == '':
        path = name.split('/')
        try:
            start = len(path) - path[::-1].index('..')
        except: start=0
        return "/".join(path[start:])
    else:
        path = name.split('/')
        try:
            start = len(path) - path[::-1].index(pattern)
        except: start=0
        return "/".join(path[start:])

def sender(source,dest,mode,wfd='',rfd=''):
    SD,SF,SL = main(source,mode) # je stocke les listes sources obtenues dans un triplet (dossiers, fichiers, liens)
    
    try:
        if (wfd == '') or (rfd == ''):
            print("cli ~ pipe not initialized")
            return 12 # error in mrsync protocol data stream

        ################# ENVOI LISTE SOURCE ####################
        L = [SD,SF,SL]
        data = pickling(L)
        while data:
            sent = send('info',wfd,data)
            if verbose() > 1:
                print(f"cli ~ {sent} bytes sent")
            data = data[sent:]
        time.sleep(0.5)
        ################# TRAITEMENT DES RÉPONSES ################
        tag, content = receive(rfd)
        if tag == b'rqst': # if generator has sent a request

            liste = content
            if mode == 'r' or mode == 'trsf' or directories(): 

            ################### /!\ TRANSFER /!\  ########################
                dirs = liste[0]
                files = liste[1]
                links = liste[2]
                temp = pickling(dirs) 
                send('dirs', wfd, temp) # we send dirs to receiver to create them
                for f in files: # for each tuple in files
                    tmp = os.path.commonpath([cleaner(f[0]), cleaner(dest[0])]) # We search for common sub path
                    second = cleaner(f[0],tmp) # we retract common subpath
                    send('file',wfd,pickling((second,f[3]))) # we send path to be created

                    try:
                        fd=os.open(f[0], os.O_RDONLY)
                    except Exception as e:
                        send('erro',wfd,pickling(e)) # send error message to close
                        os.write(wfd, b"error: can't open " + f[0] + b"\n")
                    else:
                        if verbose() > 0:
                            time.sleep(0.1)
                            print(f"cli ~ transfer of {f[0]}")
                        with open(fd, 'rb') as fileobject:
                            for line in fileobject: # we send line by line
                                
                                try:
                                    send('data',wfd,pickling(line))
                                except Exception as E: 
                                    print(f"cli ~ transfer stopped due to error {E}, retry"); sys.exit(1)
                            
                        send("next",wfd,pickling("prochain fichier"))

                send("endt",wfd,pickling('')) # end message
                time.sleep(0.1)
                if len(links) > 0:
                    if verbose() >1:
                        print(f"snd ~ {len(links)} ignored")
        elif tag == b'genQ':
            print(content)
        elif tag == b'erro':
            print("transfert impossible dû a une erreur, sortie..")
            return 10
    except Exception as E:
        print(f"snd ~ Program has encountered an unexpected error: {E}")