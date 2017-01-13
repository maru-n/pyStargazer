import unittest
import numpy as np
from pystargazer import StargazerData, StargazerException

class TestStargazerData(unittest.TestCase):

    def setUp(self):
        self.output_str_multiid_1 = "~^124706|-96.61|-48.13|-21.35|221.64`"
        self.output_str_multiid_2 = "~^224706|-96.28|-48.90|-21.13|220.50|24594|-94.27|+101.58|-17.80|230.71`"
        self.output_str_deadzone = "~*DeadZone`"
        self.marker_map = {
            #marker_id: [x,y,z]
            24706: [1.5, -1.5, 0.0],
            24594: [0.0, -1.5, 0.0]
        }
        self.data_multiid_1 = StargazerData(self.output_str_multiid_1, marker_map=self.marker_map)
        self.data_multiid_2 = StargazerData(self.output_str_multiid_2, marker_map=self.marker_map)
        self.data_without_map = StargazerData(self.output_str_multiid_2)
        self.data_no_match_map = StargazerData(self.output_str_multiid_2, marker_map={1:[1,1,1],2:[2,2,2]})
        self.data_deadzone = StargazerData(self.output_str_deadzone)

    def tearDown(self):
        pass

    def test_raw_string(self):
        self.assertEqual(self.data_multiid_1.raw_string, self.output_str_multiid_1)
        self.assertEqual(self.data_multiid_2.raw_string, self.output_str_multiid_2)
        self.assertEqual(self.data_deadzone.raw_string, self.output_str_deadzone)

    def test_deadzone(self):
        self.assertTrue(self.data_deadzone.is_deadzone)
        self.assertFalse(self.data_multiid_1.is_deadzone)
        self.assertFalse(self.data_multiid_2.is_deadzone)

    def test_invalid_input(self):
        with self.assertRaises(StargazerException):
            StargazerData(None)
        with self.assertRaises(StargazerException):
            StargazerData(self.output_str_multiid_1, multi_id=False)
        with self.assertWarns(RuntimeWarning):
            StargazerData("invalid string")

    def test_invalid_marker_map(self):
        with self.assertRaises(StargazerException):
            StargazerData("", marker_map={1:[1,2]})
        with self.assertRaises(StargazerException):
            StargazerData("", marker_map=[1,2])

    def test_have_location_data(self):
        self.assertTrue(self.data_multiid_1.have_location_data)
        self.assertTrue(self.data_multiid_2.have_location_data)
        self.assertFalse(self.data_without_map.have_location_data)
        self.assertFalse(self.data_no_match_map.have_location_data)

    def test_marker_id_1(self):
        m = self.data_multiid_1.observed_markers
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0], 24706)

    def test_local_data_1(self):
        d = self.data_multiid_1.local_location
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0].marker_id, 24706)
        self.assertAlmostEqual(d[0].x, -48.13*0.01)
        self.assertAlmostEqual(d[0].y, -21.35*0.01)
        self.assertAlmostEqual(d[0].z, -221.64*0.01)
        self.assertAlmostEqual(d[0].angle, -96.61 * np.pi / 180)

    def test_marker_id_2(self):
        m = self.data_multiid_2.observed_markers
        self.assertEqual(len(m), 2)
        self.assertEqual(m[0], 24706)
        self.assertEqual(m[1], 24594)

    def test_local_data_2(self):
        d = self.data_multiid_2.local_location
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0].marker_id, 24706)
        self.assertAlmostEqual(d[0].x, -48.90*0.01)
        self.assertAlmostEqual(d[0].y, -21.13*0.01)
        self.assertAlmostEqual(d[0].z, -220.50*0.01)
        self.assertAlmostEqual(d[0].angle, -96.28 * np.pi / 180)
        self.assertEqual(d[1].marker_id, 24594)
        self.assertAlmostEqual(d[1].x, 101.58*0.01)
        self.assertAlmostEqual(d[1].y, -17.80*0.01)
        self.assertAlmostEqual(d[1].z, -230.71*0.01)
        self.assertAlmostEqual(d[1].angle, -94.27 * np.pi / 180)

    def test_global_location_1(self):
        d = self.data_multiid_1
        self.assertEqual(len(d.marker_id), 1)
        self.assertEqual(d.marker_id[0], 24706)
        self.assertAlmostEqual(d.x, -48.13*0.01 + 1.5)
        self.assertAlmostEqual(d.y, -21.35*0.01 - 1.5)
        self.assertAlmostEqual(d.z, -221.64*0.01 + 0.0)
        self.assertAlmostEqual(d.angle, -96.61 * np.pi / 180 + 0.0)

    def test_global_location_2(self):
        d = self.data_multiid_2
        self.assertEqual(len(d.marker_id), 2)
        self.assertEqual(d.marker_id[0], 24706)
        self.assertEqual(d.marker_id[1], 24594)
        self.assertAlmostEqual(d.x, (-48.90*0.01+1.5 + 101.58*0.01+0.0)/2)
        self.assertAlmostEqual(d.y, (-21.13*0.01-1.5 -  17.80*0.01-1.5)/2)
        self.assertAlmostEqual(d.z, -(220.50*0.01+0.0 + 230.71*0.01+0.0)/2)
        self.assertAlmostEqual(d.angle, (-96.28 - 94.27) * np.pi / 180 / 2)


if __name__ == '__main__':
    unittest.main()
