#!/usr/bin/python3
# created by Ahmed G on 26/03/2021
import os, pickle, select, sys, options, signal,time


def verbose():
    if options.args_opt.verbose != None:
        return options.args_opt.verbose
    else: return 0

def quiet():
    if options.args_opt.quiet:
        return True
    return False



def send(tag,writefd,msg):
    os.write(writefd,tag.encode()) # we send tag first
    size = len(msg)


    # we send tag + size of message to read
    os.write(writefd, size.to_bytes(3,'big'))
    #if size >= 72697: # scaling problem to solve

    while msg:
        sent = os.write(writefd,msg)
        msg = msg[sent:]
    return sent




def alarm():
    timevalue = options.timeout()
    if timevalue > 0:
            signal.alarm(timevalue)


def receive(fd):
    BUFF = 10000
    data = []
    count = 0
    # lecture tag
    

    try:
        tag = os.read(fd,4)
    # lecture taille message
        size = os.read(fd,3)
        taille = int.from_bytes(size, byteorder='big')



        try: 
            if taille > 10000: # redondance ici et plus bas, normalement on a qu'un cas à gérer
                               # en bouclant, sauf que c'est la partie qui m'a empêché d'avancer
                               # lecture et ecriture dans le tube, j'ai perdu beaucoup trop de temps
                               # désolé
                while count < taille:
                    buff = os.read(fd, BUFF)
                    data.append(buff)
                    count+=len(buff)+1
                
                data_arr = pickle.loads(b"".join(data))
                return (tag, data_arr)

            else:
                buff = os.read(fd, taille)
                liste = pickle.loads(buff)
                return (tag,liste)
            
                
                
        except Exception as e:print(e, "retry transfer"); pass

    except OSError as e:
        print(e)
        if verbose():
            print("Tube fermé, à l'arrêt")



    



