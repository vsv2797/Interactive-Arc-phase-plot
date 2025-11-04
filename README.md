# Interactive-Arc-phase-plot

This repository provides an interactive plotting tool for arc-phase time series, developed especially for InSAR / arc-phase analysis workflows.

## 🧭 About  
The tool allows users to load arc-phase data and interactively explore the phase time-series (per arc, per scatterer) with visualizations and filtering capabilities. It is intended to complement detailed processing workflows in multitemporal InSAR change-detection / phase-noise modelling.

## 📂 Contents  
- `Main_IAP.py` — The main driver script for launching the interactive plot interface.  
- `Interactive_plot.py` — Module that implements the interactive plotting logic (e.g., selecting arcs, toggling filters).  
- `func.py` — Utility functions used by the interactive plot (e.g., loading data, pre-processing).  
- `README.md` — This documentation file.  
- [optional] Your data input files and sample data (not included in this repo) — you’ll need to provide your own arc phase time-series.

## 🚀 Getting Started  
### Requirements  
- Python 3.x  
- Plotting / interactive libraries (e.g., `matplotlib`, `ipywidgets`, `pandas`, depending on your implementation)  
- Any other dependencies listed in your project (please add a `requirements.txt` if not yet present)  

### Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/vsv2797/Interactive-Arc-phase-plot.git
   cd Interactive-Arc-phase-plot
   ```  
2. (Optional) Create and activate a virtual environment:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Linux/macOS  
   venv\Scripts\activate      # On Windows  
   ```  
3. Install requirements:  
   ```bash
   pip install -r requirements.txt
   ```  

### Usage  
1. Prepare your arc phase dataset — ensure you have time-series formatted for each arc/scatterer (date, phase, possibly coherence, arc ID).  
2. Run the main script:  
   ```bash
   python Main_IAP.py --input your_arc_phase_file.csv
   ```  
   (Adapt the CLI options as implemented.)  
3. In the interactive window you will be able to:  
   - Select individual arcs or scatterers.  
   - Toggle filters (e.g., temporal smoothing, outlier removal).  
   - Visualize phase vs time, residuals, statistics.  
   - Export plots or summary tables for further analysis.  

## 🎯 Intended Use & Scope  
This tool is designed for researchers and practitioners working with multitemporal InSAR arc-phase time-series (for example, those implementing coherent change detection or phase-noise modelling). It helps in the exploratory and diagnostic phase (e.g., inspecting arc behaviour, detecting anomalous scatterers, verifying filtering stages).  
**Limitations**: It does *not* implement the full change-detection algorithm by itself; rather it supports the visual/interactive inspection step.

## 🧩 Integration with Your Workflow  
Since you are working on coherent change detection for InSAR time series, you might integrate this tool as follows:  
1. After pre-processing your arcs (e.g., phase unwrapping, temporal filtering), export each arc’s time-series into the required format.  
2. Use this interactive tool to inspect and clean arcs (e.g., remove arcs with low coherence, irregular phase behaviour).  
3. Once cleaned, feed the filtered arcs into your change detection algorithm (e.g., global change-point estimation across arcs).  
4. Use the interface to verify selected arcs visually and confirm behaviour prior to automated detection.

## 🧪 Example Workflow  
1. Load dataset: `arc_phase_data.csv` with columns: `arc_id`, `time`, `phase`, `coherence`.  
2. Launch tool:  
   ```bash
   python Main_IAP.py --input arc_phase_data.csv
   ```  
3. In the interactive UI:  
   - Select `arc_id = 123` → View phase vs time.  
   - Apply smoothing filter (e.g., Savitzky–Golay).  
   - Toggle residual plot to visualize phase noise.  
   - Export cleaned time series for downstream modelling.  
4. Proceed to your automated coherent change detection step.

## 📖 Documentation & Code Structure  
- `Main_IAP.py` orchestrates loading data, configuring the UI, and handling user interactions.  
- `Interactive_plot.py` contains the plotting classes and UI callbacks.  
- `func.py` provides data-loading, filtering, smoothing, and basic statistics.  
- Future enhancements: include documentation strings (doc-comments), unit tests, example datasets, and export functions (e.g., to CSV or figure formats).

## 🤝 Contributing  
Contributions, bug reports, and feature suggestions are very welcome! If you have improvements (e.g., support for more file formats, more filtering options, export capabilities), please open an issue or submit a pull request.

## 📄 License  
Specify your license here (e.g., MIT License).  
*(If not yet chosen, you might consider MIT, Apache 2.0, or GPL 3.0 depending on your preference.)*

## 📬 Contact  
For questions or collaboration, feel free to contact me.  
> Email: vsv2745@gmail.com

---

Happy plotting! 🎉