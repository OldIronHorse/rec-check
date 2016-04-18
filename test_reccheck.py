#!/usr/bin/python

from reccheck import Mux,muxes_from_path,Service,service_from_JSON
from reccheck import services_from_mux,services_from_path
from reccheck import rm
import mock
import unittest

class TestMultiplex(unittest.TestCase):
  def test_muxes_from_path(self):
    muxes=muxes_from_path('test_data/mux_from_dir')
    self.assertEqual({'m1','m2','m3','m4'},set(muxes))


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

  @mock.patch('reccheck.os')
  def test_rm(self,mock_os):
    rm("any path")
    mock_os.remove.assert_called_with("any path")


if '__main__'==__name__:
  unittest.main()
