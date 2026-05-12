import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd

class GTFSVisualizer:
    """Handles the generation of high-quality diagrams for Tursib GTFS analysis."""
    
    def __init__(self, output_path: str = "outputs"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        # Setting a professional theme
        sns.set_theme(style="whitegrid", context="talk")
        self.palette = "viridis"

    def plot_departures(self, df: pd.DataFrame):
        """Creates a horizontal bar chart of the busiest stops."""
        plt.figure(figsize=(12, 8))
        top_df = df.sort_values("departure_count", ascending=False).head(15)
        
        ax = sns.barplot(
            data=top_df, 
            x="departure_count", 
            y="stop_name", 
            palette=self.palette,
            hue="stop_name",
            legend=False
        )
        
        plt.title("Top 15 Busiest Stops in Sibiu (Daily Departures)", pad=20, fontweight='bold')
        plt.xlabel("Total Departures", labelpad=15)
        plt.ylabel("Stop Name", labelpad=15)
        
        # Add value labels to the end of each bar
        for i in ax.containers:
            ax.bar_label(i, padding=5)
            
        plt.tight_layout()
        plt.savefig(self.output_path / "departures_per_stop.png", dpi=300)
        plt.show()

    def plot_peak_hours(self, df: pd.DataFrame):
        """Automatically detects and highlights the highest traffic hours."""
        plt.figure(figsize=(12, 6))
        
        # 1. Prepare data
        df["hour"] = df["hour"].astype(int)
        df = df.sort_values("hour")
        
        # 2. Dynamic Peak Detection: Find the top 2 highest hours
        # We find the indices of the max values to shade them
        top_hours = df.nlargest(2, 'departure_count')['hour'].tolist()
        
        # 3. Plot the main line
        sns.lineplot(data=df, x="hour", y="departure_count", 
                     marker="o", linewidth=3, color="#2c3e50", label='Bus Frequency')
        
        # 4. Add dynamic shading for detected peaks
        for peak in top_hours:
            plt.axvspan(peak - 0.5, peak + 0.5, color='green', alpha=0.15, 
                        label=f'Detected Peak ({peak}:00)')
        
        # 5. Styling
        plt.title("Tursib Network Load (Dynamic Peak Detection)", fontweight='bold')
        plt.xticks(range(0, 24))
        plt.xlabel("Hour of Day")
        plt.ylabel("Total Departures")
        
        # Handle legend to avoid duplicates
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        plt.tight_layout()
        plt.savefig(self.output_path / "peak_hours_dynamic.png", dpi=300)
        plt.show()

    def plot_zones(self, df: pd.DataFrame):
        """Creates a clean, modern donut chart for geographic distribution."""
        plt.figure(figsize=(12, 9))
        
        # 1. Sort data so the biggest slices are together
        df = df.sort_values("total_departures", ascending=False)
        
        # 2. Design - Donut Chart style
        # Create the pie first
        wedges, texts, autotexts = plt.pie(
            df["total_departures"], 
            labels=None, # We use a legend instead for a cleaner look
            autopct='%1.1f%%', 
            startangle=140, 
            colors=sns.color_palette("viridis", len(df)),
            pctdistance=0.85, # Move percentages towards the edge
            explode=[0.03] * len(df)
        )
        
        # 3. Draw a white circle in the middle (the "donut hole")
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # 4. Add a "Total" label in the center
        total_val = df["total_departures"].sum()
        plt.text(0, 0, f'Total\\n{total_val:,}\\nDeps', 
                ha='center', va='center', fontsize=14, fontweight='bold')

        # 5. Styling the percentages
        plt.setp(autotexts, size=10, weight="bold", color="white")

        # 6. Add a clean Legend to the side
        plt.legend(
            wedges, df["zone"],
            title="City Zones",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=12
        )
        
        plt.title("Tursib Service Coverage by Geographic Zone", fontweight='bold', fontsize=16, pad=20)
        
        # Adjust layout to make room for the legend
        plt.tight_layout()
        plt.savefig(self.output_path / "zones_refined.png", dpi=300, bbox_inches='tight')
        plt.show()