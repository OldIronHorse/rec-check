#!/usr/bin/python

from reccheck import Service,service_from_JSON
from reccheck import services_from_mux,services_from_path
from reccheck import Programme,programme_from_JSON,is_clashing
import unittest
from datetime import datetime
from pytz import timezone

class TestService(unittest.TestCase):
  def test_service_from_JSON(self):
    service_json=\
    '{\
      "svcname": "BBC One"\
    }'
    self.assertEqual(Service('1234','5678','BBC One'),
                     service_from_JSON('1234','5678',service_json))

  def test_services_from_mux(self):
    services=services_from_mux('test_data/services_from_mux/m1')
    self.assertEqual({Service('s1','m1','BBC One'),
                      Service('s2','m1','BBC Two')},
                     set(services))

  def test_services_from_path(self):
    services=services_from_path('test_data/services_from_path')
    self.assertEqual({Service('s1','m1','BBC One'),
                      Service('s2','m1','BBC Two'),
                      Service('s3','m2','ITV')},
                     set(services))


class TestProgramme(unittest.TestCase):
  def test_programme_from_JSON(self):
    prog_json=\
    '{\
      "start": 1461096000,\
      "stop": 1461102000,\
      "channel": "f01fa94c246c4b49492f5f3e0f9150dd",\
      "channelname": "Film4",\
      "title": {\
        "eng": "Locke"\
      }\
    }'
    london=timezone('Europe/London')
    self.assertEqual(Programme(title="Locke",
                               channel="f01fa94c246c4b49492f5f3e0f9150dd",
                               start=london.localize(
                                  datetime(hour=21,
                                           day=19,month=4,year=2016)),
                               stop=london.localize(
                                  datetime(hour=22,minute=40,
                                           day=19,month=4, year=2016))),
                     programme_from_JSON(prog_json))

class TestIsClashhing(unittest.TestCase):
  def setUp(self):
    self.london=timezone('Europe/London')

  def test_no_clash_different_day(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,
                                                     day=20,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=20,month=4, year=2016)))
    self.assertFalse(is_clashing(p1,p2))

  def tes_mo_clash_different_times(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=9,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=10,minute=40,
                                                    day=19,month=4, year=2016)))
    self.assertFalse(is_clashing(p1,p2))

  def test_clash_equal_times(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    self.assertTrue(is_clashing(p1,p2))
    
  def test_clash_p1_contains_p2(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,minute=15,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=20,
                                                    day=19,month=4, year=2016)))
    self.assertTrue(is_clashing(p1,p2))
    
  def test_clash_p2_contains_p1(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,minute=20,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=10,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,minute=15,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=20,
                                                    day=19,month=4, year=2016)))
    self.assertTrue(is_clashing(p1,p2))
    
  def test_clash_p1_first(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,minute=15,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=50,
                                                    day=19,month=4, year=2016)))
    self.assertTrue(is_clashing(p1,p2))
    
  def test_clash_p2_first(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4, year=2016)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=20,minute=15,
                                                     day=19,month=4,year=2016)),
                 stop=self.london.localize(datetime(hour=22,minute=20,
                                                    day=19,month=4, year=2016)))
    self.assertTrue(is_clashing(p1,p2))


if '__main__'==__name__:
  unittest.main()
