import unittest

import numpy as np
import xarray as xr
import pandas as pd
from data.write import auto_chunk


class TestAutoChunk(unittest.TestCase):
    def test_chunks_output(self):
        np.random.seed(0)
        temperature = 15 + 8 * np.random.randn(100, 100, 1000)
        precipitation = 10 * np.random.rand(100, 100, 1000)
        lon = np.random.rand(100)
        lat = np.random.rand(100)
        time = pd.date_range("1998-09-06", periods=1000)
        test_ds = xr.Dataset(
            data_vars=dict(
                temperature=(["lat", "lon", "time"], temperature),
                precipitation=(["lat", "lon", "time"], precipitation),
            ),
            coords=dict(
                lon=lon,
                lat=lat,
                time=time,
            ),
            attrs=dict(description="Weather related data."),
        )
        chunks_created = auto_chunk(test_ds, target_mb=1)
        expected_chunks = {'lat': 50, 'lon': 50, 'time': 31}
        self.assertEqual(expected_chunks, chunks_created)


if __name__ == '__main__':
    unittest.main()
