#!/usr/bin/python3
# created by Ahmed G on 26/03/2021

import os, builtins
from datetime import datetime, timezone
import options as op
from message import verbose




directories = []
files = []
links = []

# basename lists for display
bn_directories = []
bn_files = []
bn_links = []
saved = ''


wd = os.getcwd()


def printlist(L):
    for e in L:
        print(f"{e[0]:<15} {e[1]:>10} {e[2]:<19} {e[3]:<20}")

def listing(path_t,mode):

    saved = os.getcwd() # current directory (neutral state)
    builtins.saved = saved
    if path_t == []: # if temporary path is empty list returned by argparse
        path = '' # we change it to empty string for comparison below


    else: # if path not empty we parse then choose the path using [3] since parser returns: mode (int), user, host, path
        if type(path_t) == list: # if path is list then we don't parse it
            path = path_t
        else: # if it's not list we parse it
        
            path = op.path_parse(path_t)[3]


    if len(path) == 0:
        list_of_paths = []

    elif path == ['.'] or path == ['/']:
        list_of_paths = os.listdir()

    elif type(path) == list: # special case for '*' argument
        list_of_paths = path
        

    else:
        if os.path.isdir(path): # we exit the neutral state to list our sources
            os.chdir(path)
            list_of_paths = os.listdir()
        else:
            list_of_paths = [path]


    wd = os.getcwd()

    for p in list_of_paths:
        if os.path.isdir(p) and (os.path.join(wd,p) not in directories):
            directories.append((os.path.relpath(p, start=saved),os.stat(p).st_size,stat_to_time(p),oct(os.stat(p).st_mode)[-3:]))
            bn_directories.append((um_to_fm(p), os.stat(p).st_size, stat_to_time(p),os.path.relpath(p, start=saved)))

        elif os.path.isfile(p) and (os.path.join(wd,p) not in files):
            files.append((os.path.relpath(p, start=saved),os.stat(p).st_size,stat_to_time(p),oct(os.stat(p).st_mode)[-3:]))
            bn_files.append((um_to_fm(p), os.stat(p).st_size, stat_to_time(p),os.path.relpath(p, start=saved)))

        elif os.path.islink(p) and (os.path.join(wd,p) not in links):
            links.append((os.path.relpath(p, start=""),os.stat(p).st_size,stat_to_time(p)))
            bn_links.append((um_to_fm(p), os.stat(p).st_size,stat_to_time(p),os.path.relpath(p, start=saved)))

        else:
            None

    os.chdir(saved)# here we go back neutral state for the next function call
    return (directories, files, links)



def stat_to_time(p):
    return str(datetime.fromtimestamp(os.stat(p).st_mtime, tz=timezone.utc))[:19]


def um_to_fm(obj): # umask octal to file mode
    mode = os.stat(obj).st_mode
    umask = oct(mode)[3:]
    perms = 'rwx'
    bmask = bin(int(umask,8))[2:]

    file_mode = ''

    if os.path.isdir(obj): # if path is directory then add d to file mode
        file_mode+='d'
    elif os.path.islink(obj):
        file_mode+='l'
    else:
        file_mode+='-'

    for i in range(len(bmask)): # conversion from binary to linux permission fomat
        if bmask[i] == '1':
            file_mode += perms[i%3]
        else:
            file_mode += '-'
    return file_mode



def main(path,mode):
    """Goes through path to list files in mode, returns (dirs(list), files(list), links(list))"""

    listing(path,mode)
    
    if mode == 'r':
        for element in directories:
            listing(element,mode)

        if verbose() > 1:
            printlist(sorted(bn_directories, key=lambda x: x[3]))
            printlist(sorted(bn_files, key=lambda x: x[3]))
            print("-"*50)
        return (directories, files,links)
    else:
        if verbose() > 0:
            printlist(sorted(bn_directories, key=lambda x: x[3]))
            printlist(sorted(bn_files, key=lambda x: x[3]))
            print("-"*50)

        return (directories,files,links)