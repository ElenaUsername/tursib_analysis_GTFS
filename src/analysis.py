"""Main analysis orchestration for Tursib GTFS data."""
import logging
from pathlib import Path
from typing import Dict, Any
import os
from data_loader import GTFSDataLoader
from data_processor import GTFSProcessor
from visualizer import GTFSVisualizer

logger = logging.getLogger(__name__)


class TursibAnalysis:
    """Orchestrate complete GTFS analysis workflow for Tursib network."""

    def __init__(self, data_path: str):
        """
        Initialize analysis pipeline.

        Args:
            data_path: Path to directory containing GTFS files
        """
        self.data_path = data_path
        self.loader = GTFSDataLoader(data_path)
        self.data = None
        self.processor = None
        self.results = {}

    def run(self) -> Dict[str, Any]:
        """
        Execute complete analysis pipeline.

        Returns:
            dict: Dictionary containing all analysis results
        """
        try:
            logger.info("\n" + "=" * 60)
            logger.info("TURSIB GTFS ANALYSIS PIPELINE")
            logger.info("=" * 60 + "\n")

            # Step 1: Load data
            self._load_data()

            # Step 2: Initialize processor
            self._initialize_processor()

            # Step 3: Run all analyses
            self._run_analyses()

            # Step 4: Generate summary
            self._generate_summary()

            logger.info("\n" + "=" * 60)
            logger.info("✓ ANALYSIS COMPLETE")
            logger.info("=" * 60 + "\n")

            return self.results

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise

    def _load_data(self) -> None:
        """Load GTFS data files."""
        logger.info("STEP 1: Loading GTFS Data")
        logger.info("-" * 60)

        self.data = self.loader.load_all()

        logger.info("\n✓ Data loaded successfully\n")

    def _initialize_processor(self) -> None:
        """Initialize data processor with loaded data."""
        logger.info("STEP 2: Initializing Processor")
        logger.info("-" * 60)

        self.processor = GTFSProcessor(
            stops_df=self.data["stops"],
            stop_times_df=self.data["stop_times"],
            routes_df=self.data["routes"],
            trips_df=self.data["trips"],
        )

        logger.info("✓ Processor initialized\n")

    def _run_analyses(self) -> None:
        """Run all analysis modules."""
        logger.info("STEP 3: Running Analyses")
        logger.info("-" * 60 + "\n")

        # Data quality check
        self.results["data_quality"] = self.processor.get_data_quality_report()
        logger.info()

        # Departure analysis
        self.results["departures_per_stop"] = (
            self.processor.calculate_departures_per_stop()
        )
        logger.info()

        # Service gap analysis
        self.results["service_gaps"] = self.processor.find_service_gaps()
        logger.info()

        # Zone analysis
        self.results["zone_analysis"] = self.processor.analyze_by_zone()
        logger.info()

        # Peak hours analysis
        self.results["peak_hours"] = self.processor.analyze_peak_hours()
        logger.info()

        # Route efficiency analysis
        self.results["route_efficiency"] = self.processor.analyze_routes_efficiency()
        logger.info()

    def _generate_summary(self) -> None:
        """Generate and log analysis summary."""
        logger.info("STEP 4: Analysis Summary")
        logger.info("-" * 60)

        # Departures summary
        deps = self.results["departures_per_stop"]
        logger.info(f"\nDepartures Summary:")
        logger.info(f"  - Total stops: {len(deps)}")
        logger.info(f"  - Least served stop: {deps.iloc[0]['stop_name']} "
                    f"({int(deps.iloc[0]['departure_count'])} departures)")
        logger.info(f"  - Most served stop: {deps.iloc[-1]['stop_name']} "
                    f"({int(deps.iloc[-1]['departure_count'])} departures)")

        # Service gaps summary
        gaps = self.results["service_gaps"]
        if len(gaps) > 0:
            logger.info(f"\nService Gaps Summary:")
            logger.info(f"  - Stop with longest gap: {gaps.iloc[0]['stop_name']} "
                        f"({gaps.iloc[0]['max_gap_hours']:.1f} hours)")

        # Zone summary
        zones = self.results["zone_analysis"]
        logger.info(f"\nZone Summary:")
        total_deps = zones["total_departures"].sum()
        for _, zone in zones.iterrows():
            pct = (zone["total_departures"] / total_deps) * 100
            logger.info(f"  - {zone['zone']}: {pct:.1f}% of departures")

        # Routes summary
        routes = self.results["route_efficiency"]
        logger.info(f"\nTop 3 Busiest Routes:")
        for idx, (_, route) in enumerate(routes.head(3).iterrows(), 1):
            logger.info(f"  {idx}. Route {route['route_name']}: "
                        f"{int(route['departures'])} departures, "
                        f"{int(route['stops'])} stops")

        logger.info()

    def save_results(self, output_path: str = "outputs") -> None:
        """
        Save analysis results to CSV files.

        Args:
            output_path: Path to directory for saving results
        """
        logger.info("Saving results to CSV files...")

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        # Save DataFrames
        dataframe_results = {
            k: v
            for k, v in self.results.items()
            if isinstance(v, object) and hasattr(v, "to_csv")
        }

        for name, df in dataframe_results.items():
            csv_path = output_dir / f"{name}.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"  ✓ Saved: {csv_path}")

        logger.info(f"\n✓ Results saved to {output_dir}\n")

class TursibAnalysis:
    def __init__(self, data_path: str, output_path: str = "outputs"):
        self.data_path = data_path
        self.output_path = output_path
        self.loader = GTFSDataLoader(data_path)
        self.visualizer = GTFSVisualizer(output_path)
        self.results = {}

    def run(self):
        # 1. Load & Process (As before)
        data = self.loader.load_all()
        processor = GTFSProcessor(**data)
        
        # 2. Run Analyses
        self.results["departures"] = processor.calculate_departures_per_stop()
        self.results["peak_hours"] = processor.analyze_peak_hours()
        self.results["zones"] = processor.analyze_by_zone()
        
        # 3. Generate Diagrams & Popups
        print(f"Generating diagrams in /{self.output_path}...")
        self.visualizer.plot_departures(self.results["departures"])
        self.visualizer.plot_peak_hours(self.results["peak_hours"])
        self.visualizer.plot_zone_distribution(self.results["zones"])
        
        # 4. Save CSVs (Existing functionality)
        self.save_results(self.output_path)

# CRITICAL: This line makes the "nothing" become "something"
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 1. Setup paths
    data_path = "data"     # Where your GTFS files are
    output_path = "outputs" # Where diagrams will be saved
    
    logger.info("Starting Tursib Analysis...")
    
    # 2. Load the data
    loader = GTFSDataLoader(data_path)
    gtfs_data = loader.load_all()
    
    # 3. Process the data
    processor = GTFSProcessor(
        gtfs_data["stops"], 
        gtfs_data["stop_times"], 
        gtfs_data["routes"], 
        gtfs_data["trips"]
    )
    
    # 4. Generate Visuals
    viz = GTFSVisualizer(output_path)
    
    logger.info("Calculating frequencies and generating diagrams...")
    viz.plot_departures(processor.calculate_departures_per_stop())
    viz.plot_peak_hours(processor.analyze_peak_hours())
    viz.plot_zones(processor.analyze_by_zone())
    
    logger.info(f"DONE! Please check the '{output_path}' folder on your computer.")
    
    # 5. List the files created
    print("\nCheck these files in your folder:")
    for file in os.listdir(output_path):
        print(f" -> {file}")

if __name__ == "__main__":
    main()