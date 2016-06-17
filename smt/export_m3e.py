# -*- coding: utf-8 -*-
"""
Esporta i dati sui file come da formato indicato da M3E per elaborazione FEM
"""
# TODO: refactoring senza domain?
import os
import sys
import getopt
import logging
from shapely.affinity import affine_transform
from shapely.geometry import asShape

from project import Project
from domain import Domain
from alignment_set import AlignmentSet
from subdomain import Subdomain
from strata_surface import StrataSurface
import helpers

def write_file(folder, filename, extension, content):
    '''
    Scrive il contenuto in un file
    '''
    path = os.path.join(folder, "{}.{}".format(filename, extension))
    with open(path, "w") as text_file:
        text_file.writelines(content)

def export_subdomain(mongodb, project, subdomain, outdir, logger):
    '''
    Esporta il file .domain e avvia tutte le altre esportazioni all'interno del sottodominio
    '''
    # leggo dati e rototraslo
    subd_code = subdomain.item["code"]
    export_matrix = subdomain.item["export_matrix"]
    point = asShape(subdomain.item["boundaries"])[2]
    xmax, ymax = affine_transform(point, export_matrix) #trasformo x3 e y3 per avere xmax e ymax
    # creo cartella del sottodominio in out\M3E
    subdomain_outdir = os.path.join(outdir, subd_code)
    if not os.path.exists(subdomain_outdir):
        os.makedirs(subdomain_outdir)
    # esporto su file .domain
    domain_out_string = [
        "0 0 {} {}\n".format(xmax, ymax),
        "{}\n".format(subdomain.item.get("zmin", -100)),
        "{} {}\n".format(subdomain.item.get("nx", 100), subdomain.item.get("ny", 100))
        ]
    write_file(subdomain_outdir, subd_code, "domain", domain_out_string)
    export_dem(mongodb, project, subdomain, subdomain_outdir, logger)
    export_strata(mongodb, project, subdomain, subdomain_outdir, logger)
    export_alignment(mongodb, project, subdomain, subdomain_outdir, logger)


def export_dem(mongodb, project, subdomain, sub_outdir, logger):
    '''
    Esporta il file .xyzsup del DEM per il sottodominio indicato
    '''
    # cerco punti DEM interni al subdomain e rototraslo
    db_dem = mongodb.StrataSurface.find_one(
        {"project_id": project._id, "CODE": "DEM",
         "geom_wgs": {"$geoIntersects": {"$geometry" : subdomain.item["bound_wgs"]}}})
    if not db_dem:
        logger.error("Non ho trovato il DEM per il sottodominio %s!",
                     subdomain.item["code"])
        return
    surface = StrataSurface(mongodb, db_dem).load()
    # esporto su file .xzsup
    filename = "{}.xyzsup".format(subdomain.item["code"])
    multipoint = affine_transform(asShape(surface.item["geometry"]),
                                  subdomain.item["export_matrix"])
    with open(os.path.join(sub_outdir, filename), "w") as text_file:
        text_file.write("{}\n".format(len(multipoint)))
        for point in multipoint:
            text_file.write("{} {} {}\n".format(point.coords.x, point.coords.y, point.coords.z))


def export_strata(mongodb, project, subdomain, sub_outdir, logger):
    '''
    Esporta il file .strata e i file .xyz della stratigrafia per il sottodominio specificato
    '''
    # ottengo lista delle superfici in ordine decrescente secondo il loro punto più altro
    strata_list = list(mongodb.StrataSurface.find(
        {
            "project_id": project._id,
            "CODE": {"$ne": "DEM"},
            "geom_wgs": {"$geoIntersects": {"$geometry" : subdomain.item["bound_wgs"]}}
        }).sort("max_elev", -1))
    # cerco punti degli strati interni al subdomain e rototraslo
    strata_summary = ["{}\n".format(len(strata_list)),
                      "{} {}\n".format(subdomain.item["nx"], subdomain.item["ny"])]
    for strata in strata_list:
        surface = StrataSurface(mongodb, strata).load()
        if not surface:
            logger.error("Non ho trovato lo strato %s per il sottodominio %s!",
                         strata["_id"], subdomain.item["code"])
            return
        multipoint = affine_transform(asShape(surface.item["geometry"]),
                                      subdomain.item["export_matrix"])
        str_output = ["{}\n".format(len(multipoint))]
        for point in multipoint:
            str_output.append("{} {} {}\n".format(point.x, point.y, point.z))
        strata_filename = "{}_{}".format(strata["strata_id"], subdomain.item["code"])
        strata_summary.append("{}.xyz\n".format(strata_filename))
        # esporto su file .xzsup
        write_file(sub_outdir, strata_filename, "xyz", str_output)
    # esporto riepilogo strati su file .strata
    write_file(sub_outdir, subdomain.item["code"], "strata", strata_summary)


def export_unique_sections(mongodb, domain, subdomain, sub_outdir):
    '''
    Exporta tutte le Sezioni univoche del dominio nel file .sez e ne restituisce una lista
    Se raggruppo l'intero documento "SECTIONS" (con aggregate o distinct) mi restituisce
    dizionari doppi con chiavi in ordine differente, mi tocca controllare tutto
    '''
    # TODO: FUNZIONA SOLO CON SEZIONI CIRCOLARI!
    sections_list = list(mongodb.Alignment.aggregate([
        {
            "$match":
            {
                "domain_id": domain._id,
                "PH_wgs": {"$geoWithin": {"$geometry": subdomain.item["bound_wgs"]}}
            }
        },
        {
            "$group":
            {
                "_id":
                {
                    "extRadius":"$SECTIONS.Excavation.Radius",
                    "intRadius":"$SECTIONS.Lining.Internal_Radius",
                    "thickness":"$SECTIONS.Lining.Thickness",
                    #"offset":"$SECTIONS.Lining.Offset"
                }
            }
        }]))
    str_out = ["{}\n".format(len(sections_list))]
    for section in sections_list:
        str_out.append("1\n{} 20\n".format(section["_id"]["extRadius"]))
        str_out.append("1\n{} 20\n".format(section["_id"]["intRadius"]+section["_id"]["thickness"]))
        str_out.append("1\n{} 20\n".format(section["_id"]["intRadius"]))
    write_file(sub_outdir, subdomain.item["code"], "sez", str_out)
    return sections_list


def get_section_string(alignment, sections_list):
    '''
    cerca in sections_list l'id della sezione dell'alignment corrente
    '''
    for idx, sect in enumerate(sections_list):
        if (sect['_id']["extRadius"] == alignment.item["SECTIONS"]["Excavation"]["Radius"] and
                sect['_id']["intRadius"] == alignment.item["SECTIONS"]["Lining"]["Internal_Radius"] and
                sect['_id']["thickness"] == alignment.item["SECTIONS"]["Lining"]["Thickness"]
           ):
            return "{} {} {} {}\n".format(alignment.item["PK"], 3*idx+1, 3*idx+2, 3*idx+3)
    return None


def export_alignment(mongodb, project, subd, sub_outdir, logger):
    '''
    esporta i file .asse e .tunnel per il sottodominio specificato
    '''
    tottunnels = 0
    cr = Domain.find(mongodb, {"project_id": project._id})
    for c in cr:
        domain = Domain(mongodb, c).load()
        sections_list = export_unique_sections(mongodb, domain, subd, sub_outdir)
        tunnel_out_string = []
        asse_out_string = []
        asets = mongodb.AlignmentSet.find({"domain_id": domain._id})
        for aset in asets:
            a_set = AlignmentSet(mongodb, aset).load()
            #cerco i punti di alignment inclusi nel subdomain
            aligns = mongodb.Alignment.find({
                "alignment_set_id": a_set._id,
                "PH_wgs": {"$geoWithin": {"$geometry" : subd.item["bound_wgs"]}}
                }).sort("PK", 1)
            asse_out_string.append("{}\n".format(aligns.count()))
            for align in aligns:
                tottunnels += 1
                alignment = AlignmentSet(mongodb, align)
                alignment.load()
                # rototraslo i punti
                point = affine_transform(asShape(alignment.item["PH"]), subd.item["export_matrix"])
                z = point.z + alignment.item["SECTIONS"]["Lining"]["Offset"]
                asse_out_string.append("{} {} {}\n".format(point.x, point.y, z))
                tunnel_out_string.append(get_section_string(alignment, sections_list))
    # esporto su file .asse
    asse_out_string.insert(0, tottunnels)
    write_file(sub_outdir, subd.item["code"], "asse", asse_out_string)
    # esporto su file .tunnel
    tunnel_out_string.insert(0, tottunnels)
    write_file(sub_outdir, subd.item["code"], "tunnel", tunnel_out_string)


def export_subdomains(mongodb, project, subdomains, outdir, logger):
    '''
    lancia la funzione export_subdomain per i subdomains specificati
    Se non è stato specificato alcun subdomain esporta tutti i sottodomini del progetto
    '''
    if subdomains:
        for subdomain_code in subdomains:
            bcurr = mongodb.Subdomain.find_one({"project_id": project._id, "code": subdomain_code})
            if not bcurr:
                logger.error("Nessun Sottodominio trovato con il codice %s!", subdomain_code)
                return
            export_subdomain(mongodb, project, bcurr, outdir, logger)
    else:
        bcurr = Subdomain.find(mongodb, {"project_id": project._id})
        if bcurr.count() == 0:
            logger.error("Nessun Sottodominio trovato per il progetto %s!", project._id)
            return
        for item in bcurr:
            export_subdomain(mongodb, project, item, outdir, logger)


def export_m3e(project_code, subdomains, authenticate):
    '''
    funzione che fa il vero lavoro
    '''
    logger = helpers.init_logger('smt_main', os.path.basename(__file__) + '.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if not logged_in:
        logger.error("Not authenticated")
        return
    data_basedir = helpers.get_project_basedir(project_code)
    outdir = os.path.join(data_basedir, "out", "M3E")

    projdb = mongodb.Project.find_one({"project_code":project_code})
    if not projdb:
        logger.error("Il progetto dal codice %s non esiste!", project_code)
        return
    project = Project(mongodb, projdb)
    export_subdomains(mongodb, project, subdomains, outdir, logger)
    helpers.destroy_logger(logger)


def main(argv):
    '''
    funzione principale
    '''
    project_code = None
    authenticate = False
    subdomains = None
    syntax = ("Usage: {} -c <project code> -s <comma separated list of subdomains> "
              "[-a for autentication -h for help]").format(os.path.basename(__file__))
    try:
        opts, _ = getopt.getopt(argv, "hac:s:", ["code=", "subdomains="])
    except getopt.GetoptError:
        print syntax
        sys.exit(1)
    if len(opts) < 4:
        print syntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print syntax
            sys.exit()
        elif opt == '-a':
            authenticate = True
        elif opt in ("-c", "--code"):
            project_code = arg
        elif opt in ("-s", "--subdomains"):
            subdomains = arg.split(',')
    export_m3e(project_code, subdomains, authenticate)


if __name__ == "__main__":
    main(sys.argv[1:])
