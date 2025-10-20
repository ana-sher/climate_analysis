
import matplotlib.pyplot as plt
from typing import cast
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.geoaxes as geoaxes
from cartopy.feature.nightshade import Nightshade


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
