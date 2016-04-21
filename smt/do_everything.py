# -*- coding: utf-8 -*-
'''
main.py
crea e popola il database MongoDB prendendo le informazioni dai file CSV
'''
import os
import sys
import getopt

from main import import_all_data
from process_calc import process_calc
from plot_data import plot_data as plt_data
from plot_data_ccg import plot_data as plt_data_ccg
from export_building_data import export_buildings_data as ebd

DEFAULT_PROJECT_CODE = "MDW029_S_E_05"

def do_everything(project_code, type_of_analysis, n_samples):
    '''
    chiama tutte le funzioni
    '''
    authenticate = True #CHECK!
    #import_all_data(project_code)
    #process_calc(project_code, authenticate, n_samples, type_of_analysis)
    #plt_data_ccg(project_code, authenticate, type_of_analysis)
    plt_data(authenticate, project_code, type_of_analysis)
    ebd(project_code, authenticate)

def main(argv):
    '''
    funzione principale
    '''
    project_code = DEFAULT_PROJECT_CODE
    type_of_analysis = 'c'
    n_samples = 1
    syntax = os.path.basename(__file__) + " -c <project code> [-t <type of analysis> -n <mumber of samples> -h for help]"
    try:
        opts = getopt.getopt(argv, "hc:t:", ["code=", "type="])[0]
    except getopt.GetoptError:
        print syntax
        sys.exit(1)
#    if len(opts) < 1:
#        print syntax
#        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print syntax
            sys.exit()
        elif opt in ("-c", "--code"):
            project_code = arg
        elif opt in ("-t", "--type"):
            type_of_analysis = arg
        elif opt in ("-n", "--nsamples"):
            n_samples = int(arg)
            if n_samples <= 0:
                print syntax
                sys.exit()
    if project_code:
        do_everything(project_code, type_of_analysis, n_samples)


if __name__ == "__main__":
    main(sys.argv[1:])
