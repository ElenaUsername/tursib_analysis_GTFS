"""Module for loading and validating GTFS data."""
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GTFSDataLoader:
    """Load and validate GTFS files from Tursib feed."""

    def __init__(self, data_path: str):
        """
        Initialize GTFS data loader.

        Args:
            data_path: Path to directory containing GTFS CSV files
        """
        self.data_path = Path(data_path)
        self.required_files = [
            "stops.txt",
            "stop_times.txt",
            "routes.txt",
            "trips.txt",
        ]
        self.optional_files = ["calendar.txt", "calendar_dates.txt"]

    def validate_files(self) -> bool:
        """
        Check if all required GTFS files exist.

        Returns:
            bool: True if all required files present, False otherwise
        """
        missing_files = []
        for file in self.required_files:
            if not (self.data_path / file).exists():
                missing_files.append(file)
                logger.warning(f"Missing file: {file}")

        if missing_files:
            logger.error(f"Missing required GTFS files: {missing_files}")
            return False

        logger.info("✓ All required GTFS files found")
        return True

    def load_stops(self) -> pd.DataFrame:
        """
        Load stops.txt with data validation.

        Returns:
            pd.DataFrame: DataFrame containing stop information

        Raises:
            FileNotFoundError: If stops.txt not found
            pd.errors.EmptyDataError: If file is empty
        """
        try:
            df = pd.read_csv(self.data_path / "stops.txt")
            logger.info(f"✓ Loaded {len(df)} stops")

            # Data quality checks
            if df.isnull().any().any():
                logger.warning(f"Found {df.isnull().sum().sum()} null values in stops")

            return df
        except FileNotFoundError as e:
            logger.error(f"File not found: stops.txt - {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading stops: {e}")
            raise

    def load_stop_times(self) -> pd.DataFrame:
        """
        Load stop_times.txt with data validation.

        Returns:
            pd.DataFrame: DataFrame containing stop time information

        Raises:
            FileNotFoundError: If stop_times.txt not found
        """
        try:
            df = pd.read_csv(self.data_path / "stop_times.txt")
            logger.info(f"✓ Loaded {len(df):,} stop_time records")

            if df.isnull().any().any():
                logger.warning(f"Found {df.isnull().sum().sum()} null values in stop_times")

            return df
        except FileNotFoundError as e:
            logger.error(f"File not found: stop_times.txt - {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading stop_times: {e}")
            raise

    def load_routes(self) -> pd.DataFrame:
        """
        Load routes.txt with data validation.

        Returns:
            pd.DataFrame: DataFrame containing route information

        Raises:
            FileNotFoundError: If routes.txt not found
        """
        try:
            df = pd.read_csv(self.data_path / "routes.txt")
            logger.info(f"✓ Loaded {len(df)} routes")

            if df.isnull().any().any():
                logger.warning(f"Found {df.isnull().sum().sum()} null values in routes")

            return df
        except FileNotFoundError as e:
            logger.error(f"File not found: routes.txt - {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading routes: {e}")
            raise

    def load_trips(self) -> pd.DataFrame:
        """
        Load trips.txt with data validation.

        Returns:
            pd.DataFrame: DataFrame containing trip information

        Raises:
            FileNotFoundError: If trips.txt not found
        """
        try:
            df = pd.read_csv(self.data_path / "trips.txt")
            logger.info(f"✓ Loaded {len(df):,} trips")

            if df.isnull().any().any():
                logger.warning(f"Found {df.isnull().sum().sum()} null values in trips")

            return df
        except FileNotFoundError as e:
            logger.error(f"File not found: trips.txt - {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading trips: {e}")
            raise

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required GTFS files into a dictionary.

        Returns:
            dict: Dictionary with keys: 'stops', 'stop_times', 'routes', 'trips'

        Raises:
            FileNotFoundError: If required files are missing
        """
        logger.info("=" * 50)
        logger.info("Loading GTFS Data")
        logger.info("=" * 50)

        if not self.validate_files():
            raise FileNotFoundError("Missing required GTFS files")

        return {
            "stops": self.load_stops(),
            "stop_times": self.load_stop_times(),
            "routes": self.load_routes(),
            "trips": self.load_trips(),
        }

    def get_data_summary(self) -> Dict[str, any]:
        """
        Get summary statistics of loaded data.

        Returns:
            dict: Summary statistics
        """
        data = self.load_all()
        return {
            "total_stops": len(data["stops"]),
            "total_stop_times": len(data["stop_times"]),
            "total_routes": len(data["routes"]),
            "total_trips": len(data["trips"]),
        }