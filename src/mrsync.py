#!/usr/bin/python3
# created by Ahmed G on 26/03/2021
# pour ajouter le fichier a la variable d'environnement PATH
# export path=$PATH:. (lorsqu'on est dans le repertoire de mrsync)
# modifier le fichier ~/.bash_profile (redémarrer la machine)

import src.options as op
import src.filelist as fl
import src.sender as s
import src.server as server, os, time,signal, builtins
from pathlib import Path
import src.message as msg

import os, sys

if __name__ == "__main__":
    rfd1, wfd1 = os.pipe()  # tube père vers fils
    rfd2, wfd2 = os.pipe()  # tube fils vers père
    #op.blocking_io(rfd1,rfd2,wfd1,wfd2)

    cmd_input = op.args_opt.files

    if len(cmd_input) == 1:
            print(cmd_input)
            source = cmd_input[0]
            dest = []

    else: # last argument is dest and arguments before are sources

            source = cmd_input[:len(cmd_input)-1]
            dest = [cmd_input[-1:][0]]
            
            if os.path.isfile(dest[0]): # ERROR DEST IS NOT DIR CASE
                print("ERROR: Destination is a file, transfer impossible")
                sys.exit(1)
            
            elif (source == dest): # ERROR IF SOURCE IS DEST
                print('skipping %s' % source)
            else:
                None

    if op.args_opt.server == True: # commencée le 09/05/2021 à 22h
        n_source = op.path_parse(source[0])
        n_dest = op.path_parse(dest[0])

        if n_source[0] == 1 and n_dest[0] == 1: # this is local path
            print("source and dest are local, ssh not needed")
            pass
        
        elif n_source[0] == 2: # source is remote

            user = n_source[1]
            host = n_source[2]
            path = n_source[3]

            dest = n_dest[3]
            args = ['-e', '-l',user,host,'--','./mrsync.py --server',path, dest]

            if op.args_opt.recursive is True:
                args.append('-r')
            elif op.args_opt.list_only is True:
                args.append('--list-only')

            if msg.verbose() > 0:
                print(msg.verbose())
                for i in range(msg.verbose()):
                    args.append('-v')

            os.execvp('ssh',args)

        elif n_dest[0] == 2: # destination is remote
            user = n_dest[1]
            host = n_dest[2]
            path = n_dest[3]
            args = ['-e','-l',user,host,'--','./mrsync.py --server',n_source[3], path]
                
            if op.args_opt.recursive is True:
                args.append('-r')
            elif op.args_opt.list_only is True:
                args.append('--list-only')

            if msg.verbose() > 0:
                for i in range(msg.verbose()):
                    args.append('-v')

            os.dup2(rfd2,1)
            os.dup2(wfd1,0)

            os.execvp('ssh',args)
    else:
        childpid = os.fork()
        if childpid == 0: # SERVER CODE 

            os.close(wfd2)
            os.close(rfd1)
            if op.args_opt.recursive is True:
                # if msg.verbose():
                #     print("Recursively going through folders")
                inst = server.server(dest,rfd2,wfd1,'r')
                if inst == 10:
                    print("Erreur fatale")
                    sys.exit(10)

            elif op.args_opt.list_only is True: # List only mode
                inst = server.server(dest,rfd2,wfd1,'list')

                if inst == 10:
                    print("Erreur fatale")
                    sys.exit(10)
            else: # Normal mode
                inst = server.server(dest,rfd2,wfd1,'trsf')
                if inst == 10:
                    print("Erreur fatale")
                    sys.exit(10)
        else: # CLIENT CODE 
            
            os.close(wfd1)
            os.close(rfd2)
            if op.args_opt.recursive is True:
                s.sender(source,dest,'r',wfd2,rfd1)

            elif op.args_opt.list_only is True: # List only mode
                s.sender(source,dest,'list',wfd2,rfd1)
            else: 
                s.sender(source,dest,'trsf',wfd2,rfd1)
            os.wait()
            sys.exit(0)