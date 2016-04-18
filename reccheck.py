#!/usr/bin/python

from collections import namedtuple
import json
import glob

import os
def rm(path):
  os.remove(path)

Service=namedtuple("Service",["service_id","mux_id","name"])
Mux=namedtuple('Mux',['mux_id','path'])

def service_from_JSON(service_id,mux_id,json_text):
  values=json.loads(json_text)
  return Service(service_id,mux_id,values['svcname'])

def muxes_from_path(path):
  muxes=[]
  for p in glob.iglob(os.path.join(path,
                      'tvheadend/input/dvb/networks/*/muxes/*')):
    muxes.append(os.path.basename(p))
  return muxes

def services_from_mux(path):
  services=[]
  for p in glob.iglob(os.path.join(path,'services/*')):
    with open(p) as f:
      services.append(service_from_JSON(os.path.basename(p),
                                        os.path.basename(path),
                                        f.read()))
  return services

def services_from_path(path):
  services=[]
  for mux_path in glob.iglob(os.path.join(path,
                      'tvheadend/input/dvb/networks/*/muxes/*')):
    services+=services_from_mux(mux_path)
  return services
