import pytest

import pandas as pd

from src.data_processor import GTFSProcessor



@pytest.fixture

def sample_data():

    """Provides a tiny, fake GTFS dataset for testing."""

    stops = pd.DataFrame({

        "stop_id": ["S1", "S2"],

        "stop_name": ["Centru", "Gara"]

    })

    # Create 3 fake departures

    stop_times = pd.DataFrame({

        "trip_id": ["T1", "T1", "T2"],

        "stop_id": ["S1", "S2", "S1"],

        "arrival_time": ["08:00:00", "08:15:00", "09:00:00"]

    })

    return stops, stop_times



def test_calculate_departures_per_stop(sample_data):

    stops_df, stop_times_df = sample_data

    # We pass empty dfs for routes/trips since this specific method doesn't need them yet

    processor = GTFSProcessor(stops_df, stop_times_df, pd.DataFrame(), pd.DataFrame())

   

    result = processor.calculate_departures_per_stop()

   

    # Check if Centru (S1) correctly shows 2 departures

    centru_deps = result[result["stop_id"] == "S1"]["departure_count"].iloc[0]

    assert centru_deps == 2

    assert len(result) == 2