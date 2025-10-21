
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Optional, cast
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.geoaxes as geoaxes
from cartopy.feature.nightshade import Nightshade

from config import PLOTS_DIR


def _save_plot(fig: Figure, name: str):
    fig.savefig(PLOTS_DIR / f"{name}.png", dpi=300, bbox_inches='tight')


def plot_analysis(temp_anomalies_df: pd.DataFrame, co2_df: pd.DataFrame):
    print(temp_anomalies_df)
    df_step = temp_anomalies_df[temp_anomalies_df["time"]
                                == temp_anomalies_df["time"].max()]
    ax = cast(geoaxes.GeoAxes, plt.axes(projection=ccrs.PlateCarree()))
    ax.set_extent([df_step["lon"].min()-1, df_step["lon"].max()+1,
                   df_step["lat"].min()-1, df_step["lat"].max()+1])

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES)
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    ax.stock_img()
    ax.gridlines()

    sc = ax.scatter(df_step["lon"], df_step["lat"], c=df_step["tempanomaly"],
                    cmap="coolwarm", s=50, edgecolor='k', transform=ccrs.PlateCarree())

    plt.colorbar(sc, ax=ax)
    plt.title(f"Temperature anomaly on {df_step['time'].iloc[0].date()}")
    plt.show()


def plot_temp_stats(df: pd.DataFrame, n_clusters: int = 5, save: bool = True):
    coords = df[['lat', 'lon']]
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, max_iter=15)
    df['cluster'] = kmeans.fit_predict(coords)

    merged = df.groupby(['cluster', 'time'], as_index=False).agg({
        'lat': 'mean',
        'lon': 'mean',
        'tempanomaly': 'mean',
    })
    merged[['lat', 'lon']] = merged[['lat', 'lon']].astype(float).round(2)

    for key, values in merged.groupby(['lat', 'lon']):
        a, b = key
        plt.plot(values['time'], values['tempanomaly'], label=f'{a}, {b}')

    plt.title('Temperature anomalies during same timeframe by clustered location')
    plt.ylabel('Temperature anomaly (K)')
    plt.xlabel('Date')
    plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(10, 4)
    if save:
        _save_plot(fig, 'tempanomalies')
    plt.show()
    plt.close(fig) 


def plot_co2_stats(df: pd.DataFrame, n_clusters: int = 5):
    pass
