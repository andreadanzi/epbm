# -*- coding: utf-8 -*-
import logging
import logging.handlers
import ConfigParser, os
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import csv
import numpy as np
from datetime import datetime
# create main logger
logger = logging.getLogger('moul_demodata')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('main.log',maxBytes=5000000, backupCount=5)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# reading config file
sCFGName = 'mosul.cfg'
mosulConfig = ConfigParser.RawConfigParser()
mosulConfig.read(sCFGName)
# setup DB parameter
host = mosulConfig.get('MONGODB','host')
database = mosulConfig.get('MONGODB','database')
source_database = mosulConfig.get('MONGODB','source_database')
username = mosulConfig.get('MONGODB','username')
password = mosulConfig.get('MONGODB','password')
# connect to MongoDB
client = MongoClient()
db = client[database]
# DB authentication
db.authenticate(username,password,source=source_database)
""" Get Base data for generating
project = 1
domain = 1
alignment_set = 2
alignment_length = 2800
alignment_steps = 2800
stages = 4
min_stage_duration = 30
max_stage_duration = 120
mixes = 4
stand_pipes = 16
pressure_min = 1
pressure_max = 10
flow_rate_min = 1
flow_rate_max = 5
"""
n_project = mosulConfig.getint('DEMODATA','project')        
n_domain = mosulConfig.getint('DEMODATA','domain')
n_alignment_set = mosulConfig.getint('DEMODATA','alignment_set')
n_alignment_length = mosulConfig.getfloat('DEMODATA','alignment_length')
n_alignment_steps = mosulConfig.getint('DEMODATA','alignment_steps')
n_stages = mosulConfig.getint('DEMODATA','stages')
min_stage_duration = mosulConfig.getint('DEMODATA','min_stage_duration')
max_stage_duration = mosulConfig.getint('DEMODATA','max_stage_duration')
n_mixes = mosulConfig.getint('DEMODATA','mixes')
n_stand_pipes = mosulConfig.getint('DEMODATA','stand_pipes')
pressure_min = mosulConfig.getfloat('DEMODATA','pressure_min')
pressure_max = mosulConfig.getfloat('DEMODATA','pressure_max')
flow_rate_min = mosulConfig.getfloat('DEMODATA','flow_rate_min')
flow_rate_max = mosulConfig.getfloat('DEMODATA','flow_rate_max')
export_file = mosulConfig.get('DEMODATA','export_file')
pressure_steps = mosulConfig.getint('DEMODATA','pressure_steps')
# calculated from config
delta_boreholes = float(n_alignment_length)/float(n_alignment_steps)
total_boreholes = n_project*n_domain*n_alignment_set*n_alignment_steps
print "total_boreholes = %d" % total_boreholes
print "distance between boreholes = %.02f m" % delta_boreholes
avg_stage_duration = (max_stage_duration + min_stage_duration)/2.0
avg_stage_duration = int(avg_stage_duration*60)
# durata media per ogni mix (considerando uniformemente distribuita)
sec_per_mix = avg_stage_duration/n_mixes
mixes = [ m*sec_per_mix for m in range(n_mixes)]
# durata media per ogni step (considerando uniformemente distribuita)
sec_per_step = avg_stage_duration/pressure_steps
steps = [ m*sec_per_step for m in range(pressure_steps)]
delta_pressure = (pressure_max - pressure_min)/pressure_steps
pressures = [ m*delta_pressure for m in range(pressure_steps)]
delta_flow_rate = (flow_rate_max - flow_rate_min)/pressure_steps
flow_rates = [ m*delta_flow_rate for m in range(pressure_steps)]
print "total stages = %d, %d seconds each, duration each borehole = %d " % (n_stages, avg_stage_duration, n_stages*avg_stage_duration)
print "total rows = %d" % (total_boreholes*n_stages*avg_stage_duration)
writer_list =[]
writer_file =[]
for i in range(n_stand_pipes):
    out_csvfile = open("%s_%02d.csv" % ( export_file, i), 'wb') 
    writer = csv.writer(out_csvfile, delimiter=";")
    writer.writerow(["Start_timestamp","delta_t","Project_ID", "Domain_ID", "Line_ID", "Borehole_ID","Standpipe_ID", "Stage_ID", "Mix_ID", "P", "Q"])
    writer_list.append(writer)
    writer_file.append(out_csvfile)
for npr in range(n_project):
    for nd in range(n_domain):
        for nas in range(n_alignment_set):
            for boreh in range(n_alignment_steps):
                boreh_id = "%02d%02d%02d_B%d" % (npr,nd,nas,boreh)
                n_stand_pipe = np.random.randint(n_stand_pipes)
                writer = writer_list[n_stand_pipe]
                for ns in range(n_stages):
                    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    for sec in range(avg_stage_duration):
                        if sec in steps:
                            idx_s = steps.index(sec)
                        if sec in mixes:
                            idx_m = mixes.index(sec)
                        p = pressures[idx_s] + np.random.rand()*delta_pressure
                        q = flow_rates[idx_s] + np.random.rand()*delta_flow_rate
                        row = [timestamp,sec, npr,nd,nas, boreh_id, n_stand_pipe, ns, idx_m, p, q]
                        writer.writerow(row)
# all sample files are noew available
for out_csvfile in writer_file:
    out_csvfile.close()





