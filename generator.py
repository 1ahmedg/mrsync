#!/usr/bin/python3
import os,sys,time,pathlib
import filelist as fl
from datetime import datetime
from options import sizeonly,ignoretimes,update, ignore_existing
from message import send,receive,verbose
from sender import pickling, cleaner


def get_lastname(p):
    return os.path.normpath(os.path.basename(p))


def get_common(p):
    return pathlib.Path(*(pathlib.Path(p)).parts[1:])

def search_in_list(e, L):

    for x in L:
        if get_lastname(e) == get_lastname(x[0]):
            #print(get_common(e), get_common(x[0]))
            return True
    return False

def compare(SRC_LIST,DEST_LIST):
    GEN_LIST = []

    try:
        for S in SRC_LIST:
            for D in DEST_LIST:
            #print(f"comparing {get_lastname(S[0])} to {get_lastname(D[0])}")
                if os.path.isdir(S[0]) and S not in GEN_LIST:
                    GEN_LIST.append(S)

                if get_common(cleaner(S[0])) == get_common(cleaner(D[0])):
                    
                    if str(get_lastname(S[0])) == str(get_lastname(D[0])):
                        if os.path.isfile(S[0]):
                            if ignore_existing():
                                if verbose() > 1:
                                    print(f"gen ~ skipping {get_lastname(D[0])} (existing)")
                            
                            elif sizeonly():
                                if S[1] == D[1]:
                                    if verbose() > 1:
                                        print(f"gen ~ skipping {get_lastname(D[0])} (size-only)")
                            
                    
                            elif update():
                                date_source = datetime.strptime(S[2], "%Y-%m-%d %H:%M:%S")
                                date_dest = datetime.strptime(D[2], "%Y-%m-%d %H:%M:%S")
                                if search_in_list(S[0], DEST_LIST) and date_dest > date_source:
                                    print(f"gen ~ skipping {get_lastname(S[0])} (update)")


                elif not(search_in_list(S[0],GEN_LIST)) and not(search_in_list(S[0],DEST_LIST)):
                    GEN_LIST.append(S)
                

    except:
        print("gen ~ error while comparing")


    return GEN_LIST
        

def main(L1,L2,rfd,wfd):
    try:    
        S_DIRS = L1[0]
        S_FILES = L1[1]
        S_LINKS = L1[2]


        D_DIRS = L2[0]
        D_FILES = L2[1]
        D_LINKS = L2[2]



         
        GEN_DIRS = compare(S_DIRS,D_DIRS)
        if len(D_FILES) == 0:
            GEN_FILES = S_FILES
        else:
            GEN_FILES = compare(S_FILES,D_FILES)
        GEN_LINKS = compare(S_LINKS,D_LINKS)

        GEN_LIST = [GEN_DIRS,GEN_FILES,GEN_LINKS]
        content = pickling(GEN_LIST)



        while content:
            sent = send('rqst',wfd,content)
            if verbose() >1:
                print(f"gen ~ {sent} bytes sent")
            content = content[sent:]
        text = pickling("Generator closed")
        send('genQ', wfd, text)



    except Exception as e:
        send('erro',wfd,pickling(e))

    
    