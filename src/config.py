from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = Path(__file__).resolve().parents[1] / 'outputs' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
CO2_CSV = 'co2.csv'
TEMPANOMALIES_CSV = 'tempanomalies.csv'