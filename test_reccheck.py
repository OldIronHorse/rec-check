#!/usr/bin/python

from reccheck import Service,service_from_JSON
from reccheck import services_from_mux,services_from_path
from reccheck import Programme,programme_from_JSON,is_clashing,filter_passed
from reccheck import get_time_clashes
import unittest
from mock import patch
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

  def test_filter_passed_empty(self):
    self.assertEqual([],filter_passed([]))


class TestFilterPassed(unittest.TestCase):
  def setUp(self):
    self.london=timezone('Europe/London')

  @patch('reccheck.datetime')
  def test_filter_passed_all_passed(self,mock_dt):
    mock_dt.now.return_value=datetime(hour=17,day=17,month=9,year=2017)
    self.assertEqual([],
        filter_passed([Programme(title="prog1",channel="c1",
                                 start=self.london.localize(
                                    datetime(hour=21,day=19,month=4,year=2017)),
                                 stop=self.london.localize(
                                    datetime(hour=22,minute=40,
                                             day=19,month=4, year=2017))),
                       Programme(title="prog2",channel="c2",
                                 start=self.london.localize(
                                    datetime(hour=9,
                                             day=19,month=4,year=2017)),
                                 stop=self.london.localize(
                                    datetime(hour=10,minute=40,
                                             day=19,month=4, year=2017)))]))

  @patch('reccheck.datetime')
  def test_filter_passed_one_passed(self,mock_dt):
    mock_dt.now.return_value=datetime(hour=17,day=20,month=4,year=2017)
    self.assertEqual([Programme(title="prog2",channel="c2",
                                start=self.london.localize(
                                   datetime(hour=9,
                                            day=21,month=4,year=2017)),
                                stop=self.london.localize(
                                   datetime(hour=10,minute=40,
                                            day=21,month=4, year=2017)))],
        filter_passed([Programme(title="prog1",channel="c1",
                                 start=self.london.localize(
                                    datetime(hour=21,
                                             day=19,month=4,year=2017)),
                                 stop=self.london.localize(
                                    datetime(hour=22,minute=40,
                                             day=19,month=4, year=2017))),
                       Programme(title="prog2",channel="c2",
                                 start=self.london.localize(
                                    datetime(hour=9,
                                             day=21,month=4,year=2017)),
                                 stop=self.london.localize(
                                    datetime(hour=10,minute=40,
                                             day=21,month=4,year=2017)))]))

class TestGetTimeClashes(unittest.TestCase):
  def setUp(self):
    self.london=timezone('Europe/London')

  def test_empty(self):
    self.assertEqual([],get_time_clashes([]))

  def test_2_progs_no_clash(self):
    self.assertEqual([],
                     get_time_clashes([Programme(title="prog1",channel="c1",
                                                 start=self.london.localize(
                                                    datetime(hour=21,
                                                    day=19,month=4,year=2017)),
                                                 stop=self.london.localize(
                                                    datetime(hour=22,minute=40,
                                                    day=19,month=4,year=2017))),
                                       Programme(title="prog2",channel="c2",
                                                 start=self.london.localize(
                                                    datetime(hour=9,
                                                    day=21,month=4,year=2017)),
                                                 stop=self.london.localize(
                                                    datetime(hour=10,minute=40,
                                                    day=21,month=4,year=2017)))]))

  def test_2_progs_1_clash(self):
    p1=Programme(title="prog1",channel="c1",
                 start=self.london.localize(datetime(hour=21,
                                                     day=19,month=4,year=2017)),
                 stop=self.london.localize(datetime(hour=22,minute=40,
                                                    day=19,month=4,year=2017)))
    p2=Programme(title="prog2",channel="c2",
                 start=self.london.localize(datetime(hour=21,minute=30,
                                                     day=19,month=4,year=2017)),
                 stop=self.london.localize(datetime(hour=23,minute=40,
                                                    day=19,month=4,year=2017)))
    self.assertEqual([(p1,p2)],get_time_clashes([p1,p2]))

  #TODO: other filter tests


if '__main__'==__name__:
  unittest.main()
