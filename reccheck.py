#!/usr/bin/python

from collections import namedtuple
import json
import glob
import os
import sys
from datetime import datetime
from pytz import timezone

tz_london=timezone('Europe/London')

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
                   tz_london.localize(datetime.fromtimestamp(values['start'])),
                   tz_london.localize(datetime.fromtimestamp(values['stop'])))

def filter_passed(programmes):
  now=tz_london.localize(datetime.now())
  return filter(lambda p: p.stop>now,programmes)

#TODO: simplify this?
def is_clashing(prog1,prog2):
  return prog2.start>=prog1.start and prog2.start<=prog1.stop or\
         prog2.stop>=prog1.start and prog2.stop<=prog1.stop or\
         prog1.start>=prog2.start and prog1.start<=prog2.stop or\
         prog1.stop>=prog2.start and prog1.stop<=prog2.stop

if __name__=='__main__':
  #TODO: commandline arguments? .hts path? -V for visualise? 
  hts_root='/home/hts/.hts'
  #load programmes
  programmes=[]
  for prog_path in glob.iglob(os.path.join(hts_root,'tvheadend/dvr/log/*')):
    with open(prog_path) as prog_file:
      programmes.append(programme_from_JSON(prog_file.read()))
  #filter passed events
  programmes=filter_passed(programmes)
  print '{0} recording(s) scheduled.'.format(len(programmes))
  #find time clashes
  clashes=[]
  for i in range(len(programmes)):
    clashes+=map(lambda prog: (programmes[i],prog),
                 filter(lambda prog: is_clash(programmes[i],prog),
                        programmes[i:]))
  #exit if no clashes
  if not clashes:
    print "No clashes."
    sys.exit(0)
  #load services
  services_by_id={service_id: service
                  for service in services_from_path(hts_root)}
  #filter for multiplex clashes
  clashes=filter(lambda (p1,p2): services_by_id[p1.channel].multiplex!=services_by_id[p2.channel].multiplex, clashes)
  #report and exit
  print "There are {0} clash(es)".format(len(clashes))
  print clashes
  #TODO: visulisation of scheduled recordings?
  sys.exit(len(clashes))
