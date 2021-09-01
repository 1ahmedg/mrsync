#!/usr/bin/python3
# created by Ahmed G on 26/03/2021
import os, sys, time
import message,filelist as fl,generator, sender
from options import timeout, perms , directories
from message import send,receive,verbose
from sender import pickling, cleaner
from generator import get_lastname, get_common


def server(add,readfd, writefd,mode):
    time.sleep(0.2)
    
    DD, DF, DL = fl.main(add,mode)
    time.sleep(1)
    tag, msg = receive(readfd)

    

    # premières informations
    if tag == b'info':
        liste = msg
    elif tag == b'erro':
        print("srv ~ transfert impossible dû a une erreur, sortie imminente")
        return 404

        

    SOURCE_LIST = liste
    DEST_LIST = [DD,DF,DL]
    
    ##################### on cree le generateur pour comparaison ######################
    childpid = os.fork()

    if childpid == 0: # child code
        if verbose() > 1:
            print("srv ~ lancement du générateur pour comparaison")
        generator.main(SOURCE_LIST,DEST_LIST,readfd,writefd)
        sys.exit(0)

    else:
        pid, status = os.wait()
        total = []
        if verbose() > 2:
            time.sleep(0.2)
            print(f"srv ~ {pid} has ended with {status}")



        if mode == 'r' or mode == 'transfer' or directories(): # if mode different than list only
            tag, msg = receive(readfd)

            os.chdir(add[0]) # we set destination as current working directory
            saved = os.getcwd()

            if tag == b'dirs': # we create the directories needed
                for p in msg:
                    for x in p[0].split('/'):
                        try:
                            os.mkdir(x)
                        except:pass
                        os.chdir(x)
                    os.chdir(saved)
            

            while tag != b'endt' and not(directories()): # t for transfer

                tag, msg = receive(readfd)

                if tag == b'file': # info of the file
                    filepath = msg[0]
                    total.append(msg[0])

                    file_in = os.open(filepath,os.O_CREAT|os.O_WRONLY|os.O_TRUNC)

                    if perms(): # if -p / --perms activated we set mask
                        os.chmod(filepath,int(msg[1]))

                    tag, msg = receive(readfd)
                    
                    while tag == b'data': # data of the file
                        os.write(file_in, msg)
                        try: 
                            tag, msg = receive(readfd)
                        except Exception as e:
                            print(f"srv ~ exception {e} on file {filepath} in, skipping..");pass

                    os.close(file_in)


            if tag == b'endt': # transfer done
                res=''

                if len(total) != 0: # display purposes
                    for x in total: res+=x+' ~ '
                    print(f"files updated ({len(total)}):",res)
                    sys.exit(0)
                else:
                    print("0 files updated")
                    sys.exit(0)

            else:
                if tag == b'erro':
                    print(f"srv ~ Has received an error from sender {msg}")
                print("err")
                sys.exit(5)
        else: # we are in list only mode -> no work to be done
            sys.exit(0)

