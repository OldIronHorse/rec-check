#!/usr/bin/python

from collections import namedtuple
import json
import glob
import os
from datetime import datetime
from pytz import timezone

london=timezone('Europe/London')

Service=namedtuple("Service",["service_id","mux_id","name"])
Programme=namedtuple('Programme',["title","channel","start","stop"])

def service_from_JSON(service_id,mux_id,json_text):
  values=json.loads(json_text)
  return Service(service_id,mux_id,values['svcname'])

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

def programme_from_JSON(json_text):
  values=json.loads(json_text)
  return Programme(values['title']['eng'],values['channel'],
                   london.localize(datetime.fromtimestamp(values['start'])),
                   london.localize(datetime.fromtimestamp(values['stop'])))

#TODO: simplify this?
def is_clashing(prog1,prog2):
  return prog2.start>=prog1.start and prog2.start<=prog1.stop or\
         prog2.stop>=prog1.start and prog2.stop<=prog1.stop or\
         prog1.start>=prog2.start and prog1.start<=prog2.stop or\
         prog1.stop>=prog2.start and prog1.stop<=prog2.stop
