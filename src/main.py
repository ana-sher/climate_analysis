from typing import Optional
from data.load import read_raw_tempanomalies, read_raw_co2
from visualization.plotting import plot_analysis
from utils.location import get_location
from datetime import datetime, timezone
import argparse

def main(year_range: int = 1, lon: Optional[float] = None, lat: Optional[float] = None, loc_range: int = 10):
    utc_now = datetime.now(timezone.utc)
    year_from = utc_now.year - year_range

    if lon is None or lat is None:
        lon, lat = get_location()

    lat_min = lat - loc_range
    lat_max = lat + loc_range
    lon_min = lon - loc_range
    lon_max = lon + loc_range
    temp_anomalies_df = read_raw_tempanomalies(year_from, lat_min, lat_max, lon_min, lon_max)
    co2_df = read_raw_co2(year_from, lat_min, lat_max, lon_min, lon_max)

    plot_analysis(temp_anomalies_df, co2_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year_range",
        type=int,
        default=1,
        help="Years range from current"
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=None,
        help="Longitude of location"
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=None,
        help="Latitude of location"
    )
    parser.add_argument(
        "--loc_range",
        type=int,
        default=10,
        help="Location range (+/- to lat, lon)"
    )
    args = parser.parse_args()
    main(args.year_range, args.lon, args.lat, args.loc_range)