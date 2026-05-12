"""Module for processing and analyzing GTFS data."""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import timedelta

logger = logging.getLogger(__name__)


class GTFSProcessor:
    """Process and analyze GTFS data for Tursib network."""

    def __init__(
        self,
        stops_df: pd.DataFrame,
        stop_times_df: pd.DataFrame,
        routes_df: pd.DataFrame,
        trips_df: pd.DataFrame,
    ):
        """
        Initialize GTFS processor with data files.

        Args:
            stops_df: DataFrame from stops.txt
            stop_times_df: DataFrame from stop_times.txt
            routes_df: DataFrame from routes.txt
            trips_df: DataFrame from trips.txt
        """
        self.stops = stops_df.copy()
        self.stop_times = stop_times_df.copy()
        self.routes = routes_df.copy()
        self.trips = trips_df.copy()

        logger.info("GTFS Processor initialized")

    def calculate_departures_per_stop(self) -> pd.DataFrame:
        """
        Calculate total departures per stop across all routes and times.

        Returns:
            pd.DataFrame: DataFrame with stop_id, stop_name, departure_count
        """
        logger.info("Calculating departures per stop...")

        departures = (
            self.stop_times.groupby("stop_id")
            .size()
            .reset_index(name="departure_count")
        )

        # Merge with stop names
        departures = departures.merge(
            self.stops[["stop_id", "stop_name"]], on="stop_id", how="left"
        )

        departures = departures.sort_values("departure_count", ascending=True)

        logger.info(f"✓ Analyzed {len(departures)} stops")
        logger.info(
            f"  - Min departures: {departures['departure_count'].min()} "
            f"(stop: {departures.iloc[0]['stop_name']})"
        )
        logger.info(f"  - Max departures: {departures['departure_count'].max()}")
        logger.info(f"  - Avg departures: {departures['departure_count'].mean():.1f}")

        return departures

    def find_service_gaps(self) -> pd.DataFrame:
        """
        Find the longest service gaps (time between consecutive departures) per stop.

        Returns:
            pd.DataFrame: DataFrame with stop_id, stop_name, max_gap (hours)
        """
        logger.info("Finding service gaps...")

        gaps_list = []

        for stop_id in self.stops["stop_id"].unique():
            stop_times = self.stop_times[self.stop_times["stop_id"] == stop_id].copy()

            if len(stop_times) < 2:
                continue

            # Convert time strings to timedelta for calculation
            try:
                stop_times["arrival_time"] = pd.to_timedelta(stop_times["arrival_time"])
                stop_times = stop_times.sort_values("arrival_time")

                times = stop_times["arrival_time"].values
                gaps = [times[i + 1] - times[i] for i in range(len(times) - 1)]

                if gaps:
                    max_gap = max(gaps)
                    max_gap_hours = max_gap.total_seconds() / 3600

                    stop_name = self.stops[self.stops["stop_id"] == stop_id][
                        "stop_name"
                    ].values[0]

                    gaps_list.append(
                        {
                            "stop_id": stop_id,
                            "stop_name": stop_name,
                            "max_gap_hours": max_gap_hours,
                            "num_departures": len(times),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error processing stop {stop_id}: {e}")
                continue

        gaps_df = pd.DataFrame(gaps_list).sort_values("max_gap_hours", ascending=False)

        logger.info(f"✓ Analyzed {len(gaps_df)} stops for service gaps")
        if len(gaps_df) > 0:
            logger.info(f"  - Max gap: {gaps_df['max_gap_hours'].max():.1f} hours")
            logger.info(f"  - Avg gap: {gaps_df['max_gap_hours'].mean():.1f} hours")

        return gaps_df

    def analyze_by_zone(self) -> pd.DataFrame:
        """
        Analyze departures by geographic zone (detected from stop names).

        Returns:
            pd.DataFrame: DataFrame with zone, stop_count, total_departures
        """
        logger.info("Analyzing service by zone...")

        # Define zones based on stop name patterns
        def extract_zone(stop_name: str) -> str:
            stop_name_lower = str(stop_name).lower()

            if any(
                keyword in stop_name_lower
                for keyword in ["centru", "station", "gara", "piata", "casa"]
            ):
                return "City Center"
            elif any(
                keyword in stop_name_lower
                for keyword in ["industrial", "zona industriala"]
            ):
                return "Industrial Zone"
            elif any(
                keyword in stop_name_lower
                for keyword in ["selimbar", "parc"]
            ):
                return "Suburban/Parks"
            elif any(
                keyword in stop_name_lower
                for keyword in ["school", "scoala", "gimnaziu"]
            ):
                return "School Routes"
            else:
                return "Other"

        self.stops["zone"] = self.stops["stop_name"].apply(extract_zone)

        # Count departures per zone
        zone_departures = self.stop_times.merge(
            self.stops[["stop_id", "zone"]], on="stop_id", how="left"
        )

        zone_analysis = (
            zone_departures.groupby("zone")
            .agg(
                {
                    "stop_id": "nunique",  # Number of unique stops
                    "trip_id": "count",  # Total departures
                }
            )
            .reset_index()
            .rename(
                columns={
                    "stop_id": "stop_count",
                    "trip_id": "total_departures",
                }
            )
            .sort_values("total_departures", ascending=False)
        )

        logger.info(f"✓ Analyzed {len(zone_analysis)} zones")
        logger.info(f"  - Total zones: {len(zone_analysis)}")
        for _, row in zone_analysis.iterrows():
            pct = (row["total_departures"] / zone_analysis["total_departures"].sum()) * 100
            logger.info(
                f"  - {row['zone']}: {row['stop_count']} stops, "
                f"{row['total_departures']:,} departures ({pct:.1f}%)"
            )

        return zone_analysis

    def analyze_peak_hours(self) -> pd.DataFrame:
        """
        Identify peak service hours based on departure frequency.

        Returns:
            pd.DataFrame: DataFrame with hour, departure_count
        """
        logger.info("Analyzing peak hours...")

        # Extract hour from arrival_time
        self.stop_times["hour"] = self.stop_times["arrival_time"].str.split(":").str[0]

        hourly_departures = (
            self.stop_times.groupby("hour")
            .size()
            .reset_index(name="departure_count")
        )

        hourly_departures = hourly_departures.sort_values("hour")

        logger.info(f"✓ Analyzed {len(hourly_departures)} hours")
        peak_hour = hourly_departures.loc[hourly_departures["departure_count"].idxmax()]
        logger.info(
            f"  - Peak hour: {peak_hour['hour']}:00 "
            f"({int(peak_hour['departure_count'])} departures)"
        )

        return hourly_departures

    def analyze_routes_efficiency(self) -> pd.DataFrame:
        """
        Analyze route efficiency based on stop coverage and frequency.

        Returns:
            pd.DataFrame: DataFrame with route_id, route_name, stops, departures
        """
        logger.info("Analyzing route efficiency...")

        route_stats = []

        for route_id in self.routes["route_id"].unique():
            route_trips = self.trips[self.trips["route_id"] == route_id]
            route_stop_times = self.stop_times[
                self.stop_times["trip_id"].isin(route_trips["trip_id"])
            ]

            route_name = self.routes[self.routes["route_id"] == route_id][
                "route_short_name"
            ].values[0]

            unique_stops = route_stop_times["stop_id"].nunique()
            total_departures = len(route_stop_times)

            route_stats.append(
                {
                    "route_id": route_id,
                    "route_name": route_name,
                    "stops": unique_stops,
                    "departures": total_departures,
                    "efficiency": total_departures / unique_stops if unique_stops > 0 else 0,
                }
            )

        routes_df = pd.DataFrame(route_stats).sort_values(
            "departures", ascending=False
        )

        logger.info(f"✓ Analyzed {len(routes_df)} routes")

        return routes_df

    def get_data_quality_report(self) -> Dict[str, any]:
        """
        Generate data quality report.

        Returns:
            dict: Data quality metrics
        """
        logger.info("Generating data quality report...")

        report = {
            "total_stops": len(self.stops),
            "total_stop_times": len(self.stop_times),
            "total_routes": len(self.routes),
            "total_trips": len(self.trips),
            "stops_with_null_names": self.stops["stop_name"].isnull().sum(),
            "stop_times_with_null": self.stop_times.isnull().sum().sum(),
            "unique_trips": self.stop_times["trip_id"].nunique(),
            "data_completeness": {
                "stops": (
                    (len(self.stops) - self.stops.isnull().sum().sum())
                    / (len(self.stops) * len(self.stops.columns))
                    * 100
                ),
                "stop_times": (
                    (len(self.stop_times) - self.stop_times.isnull().sum().sum())
                    / (len(self.stop_times) * len(self.stop_times.columns))
                    * 100
                ),
            },
        }

        logger.info(f"✓ Data quality report generated")
        logger.info(f"  - Stops: {report['total_stops']:,}")
        logger.info(f"  - Stop times: {report['total_stop_times']:,}")
        logger.info(f"  - Routes: {report['total_routes']}")
        logger.info(f"  - Trips: {report['total_trips']:,}")

        return report