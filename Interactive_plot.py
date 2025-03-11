import numpy as np
import matplotlib.pyplot as plt

class InteractiveArcPlot:
    """
    Interactive tool to manually draw arcs between two points on the amplitude image
    and visualize the corresponding arc phase time series.
    """
    def __init__(self, mean_amplitude, arc_phases, first_order_mask, tcs_mask):
        self.mean_amplitude = mean_amplitude
        self.arc_phases = arc_phases  # Shape: (num_ifgs, height, width)
        self.first_order_mask = first_order_mask
        self.tcs_mask = tcs_mask  # Ensure TCS points are included

        self.fig, self.ax = plt.subplots(1, 2, figsize=(16, 8))
        self.selected_points = []  # Stores clicked points (row, col)

        self.plot_amplitude_image()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def plot_amplitude_image(self):
        """Plots the amplitude image and overlays first-order and TCS points."""
        self.ax[0].imshow(self.mean_amplitude, cmap="cmc.grayC_r", interpolation="nearest")
        self.ax[0].set_title(" Arc phase plot b/w first order and second order points")
        self.ax[0].set_xlabel("Range")
        self.ax[0].set_ylabel("Azimuth")

        # Highlight first-order points
        first_order_coords = np.array(np.where(self.first_order_mask)).T
        self.ax[0].scatter(first_order_coords[:, 1], first_order_coords[:, 0], 
                            color='red', marker='D', s=2, label="First Order Points")

        # Highlight TCS points (Fixed: Ensure they appear)
        tcs_coords = np.array(np.where(self.tcs_mask)).T
        self.ax[0].scatter(tcs_coords[:, 1], tcs_coords[:, 0], 
                            color='blue', marker='.', s=2, label="TCS Points")

        self.ax[0].legend()

    def on_click(self, event):
        """Handles click events to select two points, restricted to first-order and second-order points."""
        if event.inaxes != self.ax[0]:  # Ensure clicks are within the amplitude image
            return

        row, col = int(event.ydata), int(event.xdata)

        # Check if the selected point is in the first-order or second-order mask
        if not (self.first_order_mask[row, col] or self.tcs_mask[row, col]):
            print(f"⚠️ Invalid selection at ({row}, {col}). Only select first-order or second-order points.")
            return  # Ignore the selection if it's not in first-order or second-order points

        if len(self.selected_points) == 2:  # Reset points if a new selection starts
            self.selected_points = []
            self.ax[0].clear()  # Clear previous selections
            self.plot_amplitude_image()  # Redraw the amplitude image with first-order and TCS points

        self.selected_points.append((row, col))

        # Mark selected point
        self.ax[0].scatter(col, row, color='cyan', marker='.', s=40)
        self.fig.canvas.draw()

        # If two points are selected, draw the arc and plot phase
        if len(self.selected_points) == 2:
            self.plot_arc()
            self.plot_arc_phase()

    def plot_arc(self):
        """Draws a line (arc) between the two selected points."""
        (row1, col1), (row2, col2) = self.selected_points
        self.ax[0].plot([col1, col2], [row1, row2], color='gray', linewidth=2, label="Arc")
        self.fig.canvas.draw()

    def plot_arc_phase(self):
        """Extracts and plots the arc phase time series between the two selected points."""
        (row1, col1), (row2, col2) = self.selected_points

        # Extract arc phase time series between the selected points
        arc_phase_series = self.arc_phases[:, row1, col1] - self.arc_phases[:, row2, col2]

        self.ax[1].clear()
        self.ax[1].scatter(np.arange(len(arc_phase_series)), arc_phase_series, 
                        color='blue', marker='o', s=10)  # Use scatter plot (points only)
        self.ax[1].set_title(f"Arc Phase Between ({row1},{col1}) and ({row2},{col2})")
        self.ax[1].set_xlabel("Time (Interferograms)")
        self.ax[1].set_ylabel("Phase (radians)")
        self.ax[1].grid(True)

        self.fig.canvas.draw()

