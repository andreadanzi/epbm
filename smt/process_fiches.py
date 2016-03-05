# -*- coding: utf-8 -*-
import glob,io
import csv
import sys, getopt, os
from minimongo import Model, Index
# danzi.tn@20160229 - estrazione sensibilita
# danzi.tn@20160301 - completamento estrazione tabelle
# danzi.tn@20160303 - aggiunto il modello Mongo DB
t1 = u"Altitude du terrain naturel (NGF)  " #35 
t2 = u"Altitude du toit du tunnel  " # 5 
t3 = u"Profondeur du toit du tunnel/ terrain naturel (à ce PK)  " #30 
t4 = u"Profondeur plancher bas/ terrain naturel (m)  " #3 
t5 = u"Altitude du plancher bas (NGF)  " #32 
t6 = u"Profondeur du toit du tunnel par rapport au plancher bas  " #27 
t7 = u"Distance bord du bâtiment/axe du tracé  " #10m < D <= 20m 
t8 = u"Angle entre l’axe principal du bâtiment/axe du tracé  " #entre 60° et 90°
t9 = u"Nombre de sous-sols  " #1 
t10 = u"Nombre d'étages au-dessus du Rdc (R+?)  "#1 
t11 = u"Nb de niveaux de combles  " #1 
t12 = u"Nb d'ascenseurs  "
t13 = u"Emprise au sol (Lxl)  " #12 X 10 
t14 = u"Hauteur superstructure/ terrain naturel (m)  " #7 
t15  = u"Commentaire éventuel"

sStart = u"Sensibilité globale du bâti aux déformations"

poco = u"Peu Sensible"
sens = u"Sensible"
tres = u"Très Sensible"

sensLevels = [poco,sens,tres]

sensDict = {poco:"poco", sens: "sensibile", tres:"molto"}

def getValFromTemplate(temp,line):
    retval = ""
    if temp in line:
        splitted_line = line.split(temp)
        retval = splitted_line[1]
    return retval.strip().encode('ascii', 'ignore')
        

def processFiles(sPath):
    sWildcardPath = os.path.join(sPath,'*.pdf.txt' )
    sCsvPath = os.path.join(sPath,'processed_results.csv' )
    with open(sCsvPath, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow(["Nome File", "Codice Edificio","Particella","No Edificio","Livello","Altitude du terrain","Altitude du toit","Profondeur du toit","Profondeur plancher", "Altitude du plancher","Profondeur du toit/planches","Distance bord","Angle entre","Nombre de sous-sols","Nombre etages","Nb de niveaux","Nb ascenseurs","Emprise", "Hauteur superstructure","Commentaire"])
        for name in glob.glob(sWildcardPath):
            #print "Processing %s " % name[:-4]
            splittedname = name.split('_')
            sParticella = splittedname[0]
            sEdificio = splittedname[1]
            sCodice = "%s_%s" % (sParticella,sEdificio)
            sensLevel = "ND"
            altTerrain = "ND1"
            altToit = "ND2"
            profToit ="ND3"
            profPlanches = "ND4"
            altPlanches = "ND5"
            profToitPlanches = "ND6"
            distance = "ND7"
            angle = "ND8"
            nombreSousSol = "ND9"
            nombreEtages = "ND10"
            nbNiveaux = "ND11"
            nbAscens = "ND12"
            emprise = "ND13"
            haut = "ND14"
            comment = "ND15"
            with io.open(name,encoding='utf8') as f:
                bFoundStart = False
                iCountStart = 0
                for line in f:
                    if bFoundStart:
                        iCountStart += 1
                    if sStart in line:
                        bFoundStart = True                
                    if iCountStart >= 2:
                        if line.strip() in sensLevels:
                            sensLevel = sensDict[line.strip()]
                            iCountStart = 0
                            bFoundStart = False
                    if t1 in line:
                        altTerrain = getValFromTemplate(t1,line)
                    if t2 in line:
                        altToit = getValFromTemplate(t2,line)
                    if t3 in line:
                        profToit = getValFromTemplate(t3,line)
                    if t4 in line:
                        profPlanches = getValFromTemplate(t4,line)
                    if t5 in line:
                        altPlanches = getValFromTemplate(t5,line)
                    if t6 in line:
                        profToitPlanches = getValFromTemplate(t6,line)
                    if t7 in line:
                        distance = getValFromTemplate(t7,line)
                    if t8 in line:
                        angle = getValFromTemplate(t8,line)
                    if t9 in line:
                        nombreSousSol = getValFromTemplate(t9,line)
                    if t10 in line:
                        nombreEtages = getValFromTemplate(t10,line)
                    if t11 in line:
                        nbNiveaux = getValFromTemplate(t11,line)
                    if t12 in line:
                        nbAscens = getValFromTemplate(t12,line)
                    if t13 in line:
                        emprise = getValFromTemplate(t13,line)
                    if t14 in line:
                        haut = getValFromTemplate(t14,line)
                    if t15 in line:
                        comment = getValFromTemplate(t15,line)
                spamwriter.writerow([name[:-4], sCodice,sParticella,sEdificio,sensLevel,altTerrain,altToit,profToit,profPlanches,altPlanches,profToitPlanches,distance,angle,nombreSousSol,nombreEtages,nbNiveaux,nbAscens,emprise,haut,comment])
                
def main(argv):
    sPath = "NONE"
    sSyntax = "process_fiches.py -p <folder path>"
    try:
        opts, args = getopt.getopt(argv,"hp:",["path="])
    except getopt.GetoptError:
        print sSyntax
        sys.exit(1)
    if len(opts) < 1:
        print sSyntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sSyntax
            sys.exit()
        elif opt in ("-p", "--path"):
            sPath = arg
            if os.path.isdir(sPath):
                processFiles(sPath)
            else:
                print sSyntax
                print "Directory %s does not exists!" % sPath
                sys.exit(3)
    
    
    
if __name__ == "__main__":
    main(sys.argv[1:])