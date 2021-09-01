#!/usr/bin/python3
# created by Ahmed G 26/03/2021
#
# · gestion des options et des paramètres
# · fonctions utilitaires d’affichage dépendant des options
# · gestion des messages d’erreurs
import argparse as ap
import os



#------------------- OPTIONAL ARGUMENTS -------------------------#
options = ap.ArgumentParser(description="")


q_v = options.add_mutually_exclusive_group() # Program cannot be verbose and quiet simultaneously
q_v.add_argument('-v', '--verbose',action='count',help="increase verbosity")
q_v.add_argument('-q', '--quiet',action='store_true',help="suppress non-error messages")


options.add_argument('-r', '--recursive',action='store_true',help="recurse into directories")
options.add_argument('-a', '--archive',action='store_true',help="archive mode; same as -rpt (no -H)")

options.add_argument('--server',action='store_true',default=False,help="server mode")

options.add_argument('-u', '--update',action='store_true',help="skip files that are newer on the receiver")
options.add_argument('-d', '--dirs',action='store_true',default=False,help="transfer directories without recursing")
options.add_argument('-p', '--perms',action='store_true',help="preserve permissions")


options.add_argument('-t', '--times',action='store_true',help="preserve times")
options.add_argument('--existing',action='store_true',help="skip creating new files on receiver")
options.add_argument('--ignore-existing',action='store_true',help="skip updating files that exist on receiver")
options.add_argument('--delete',action='store_true',help="delete extraneous files from dest dirs")


options.add_argument('--timeout=TIME',nargs='?',dest='timeout',action='store',type=int,required=False,default=0,help="set I/O timeout in seconds (default is 0)")
options.add_argument('--blocking-io',action='store_true',default=False,help="use blocking I/O for the remote shell")
options.add_argument('-I','--ignore-times',action='store_true',default=False,help="don't skip files that match size and time")

options.add_argument('--size-only',action='store_true',default=False,help="skip files that match in size")
options.add_argument('--list-only',action='store_true',help="skip files that match in size")


#------------------- REQUIRED ARGUMENTS -------------------------#

options.add_argument('files',type=str,nargs='+',default=None,help="source path")

args_opt = options.parse_args()


#------------------- FUNCTIONS FOR OPTIONS -------------------------#





def timeout():
    if type(args_opt.timeout) is int:
        #print("Setting alarm to %i second-s" % args_opt.timeout)
        return args_opt.timeout

def directories():
    if args_opt.dirs is True:
        return True

def blocking_io(*args):
    for fd in args:
        os.set_blocking(fd,args_opt.blocking_io)

def sizeonly():
    if args_opt.size_only is True:
        return True

def ignore_existing():
    if args_opt.ignore_existing is True:
        return True

def ignoretimes():
    if args_opt.ignore_times is True:
        return True
def update():
    if args_opt.update is True:
        return True

def perms():
    if args_opt.perms is True:
        return True

    

def path_parse(s):
    """Parses paths given to the function, returns tuple (mode, user, host, path)"""
    if type(s) == tuple:
        fullpath = s[0].split("@") #ou partition
    elif type(s) == list:
        fullpath = s
    else:
        fullpath = s.split("@")

    
    if len(fullpath) == 1: 
        return 1,None, None, fullpath[0] # integer 1 signals to local path
    
    elif len(fullpath) == 2: # we split distant@localhost:path
        user = fullpath[0] # contains distant
        host_path = fullpath[1] # contains localhost:path

        if host_path.count("::") >= 1: # if double colon is present we enter daemon mode
            temp = host_path.split("::") 
            host = temp[0] # contains localhost
            path = temp[1] # contains path
            
            return 3, user, host, path # integer 3 signals daemon mode
        else:
            temp = host_path.split(":")
            host = temp[0] # contains localhost
            path = temp[1] # contains path

            return 2, user, host, path # integer 2 signals distant path















