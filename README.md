🚌 **A Deep Dive into Sibiu's GTFS Data**
Welcome to the project that finally proves why you missed your bus to the Industrial Zone! This project explores and deconstructs the GTFS (General Transit Feed Specification) dataset for Sibiu's transport operator, Tursib. We’ve moved past "guessing" and started "processing" to find out where the buses are actually hiding.

📊 **Project Objectives**
Hunting for "Ghost" Zones: Finding those legendary stops with the fewest daily departures (yes, they actually exist).

The "Nap Time" Analysis: Pinpointing the exact hours when the bus density drops so low you'd be faster walking in a downpour.

Center vs. The World: A spatial showdown between the bustling city center and the quiet, forgotten outskirts.

Special Ops: A dedicated investigation into industrial zones and the school lines that carry the future of Sibiu (at 7:15 AM sharp).

🔍 **Key Findings (The Spicy Reality)**
The Loneliest Stop: Ocna Scoala is officially the most exclusive club in the network, with exactly one departure per day. Don't blink, or you'll miss your ride for the next 24 hours.

The 10-Hour Siesta: In Selimbar Parc Industrial, we found service gaps longer than a workday. If you miss that 6:14 AM bus, I hope you brought a very long book and a tent.

The Gravity of the Train Station: Like a black hole, the Train Station and Casa Armatei suck in 70% of the city’s transport flow. If you aren't there, are you even in Sibiu?


**How to Run This Project (The "Manual" for Human Beings)**

1. Clone the repository:
   ```bash
   git clone [the link of the repository]


2. Install required libraries:
    Run the following command to install all necessary dependencies:
    Bash
    pip install -r requirements.txt

3.  Data Configuration:
    Create a folder named data/ in the project root.
    Download the data: You can find the official Tursib GTFS data at Mobility Database - Tursib Sibiu.
    Extract the .zip file and place the raw .txt files (stops.txt, stop_times.txt, routes.txt, etc.) into the data/ folder.

7.  Run the analysis:
    Launch Jupyter Notebook: jupyter notebook
    Open and run the Jupiter_Analyse.ipynb file.
