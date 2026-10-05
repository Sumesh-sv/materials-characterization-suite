import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

lam = 532  # in nm
E = 2.33  # in eV

# Load data

data = np.loadtxt("GNP11.txt")
shift = data[:, 0]
intensity = data[:, 1]

# Baseline correction (polynomial)

baseline = np.polyfit(shift, intensity, 3)
baseline_curve = np.polyval(baseline, shift)
corrected_intensity = intensity - baseline_curve

# Peak detection

peaks, properties = find_peaks(corrected_intensity, height=100)

# Define Raman regions

D_region = (shift > 1300) & (shift < 1400)
G_region = (shift > 1550) & (shift < 1620)
TwoD_region = (shift > 2600) & (shift < 2800)

# Extract peak positions

D_peak = shift[D_region][np.argmax(corrected_intensity[D_region])]
G_peak = shift[G_region][np.argmax(corrected_intensity[G_region])]
TwoD_peak = shift[TwoD_region][np.argmax(corrected_intensity[TwoD_region])]

# Extract intensities

D_int = max(corrected_intensity[D_region])
G_int = max(corrected_intensity[G_region])
TwoD_int = max(corrected_intensity[TwoD_region])

# Ratios

ID_IG = D_int / G_int
I2D_IG = TwoD_int / G_int
L_sp2 = (560 / np.power(E, 4)) * ID_IG
L_D2 = (2.4 * 10 ** (-9)) * (np.power(lam, 4)) * ID_IG
L_D = np.sqrt(L_D2)
n_D = ((2.4 * 10 ** 22) / (lam ** 4)) * ID_IG

# Create Main Window


root = tk.Tk()
root.title("Raman Analysis")
root.geometry("1000x700")

# =========================
# Left Frame → Plot
# =========================

plot_frame = tk.Frame(root)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(7, 7))

# Raman spectrum
ax.plot(shift, corrected_intensity,
        label="Baseline Corrected Spectrum",
        color='red')

# All detected peaks
ax.plot(shift[peaks],
        corrected_intensity[peaks],
        "ro",
        label="Detected Peaks")

# Highlight D, G, 2D peaks
ax.plot(D_peak, D_int, "bo")
ax.plot(G_peak, G_int, "go")
ax.plot(TwoD_peak, TwoD_int, "mo")

# Labels
ax.text(D_peak, D_int, f"D\n{D_peak:.1f}",
        color='blue', ha='center')

ax.text(G_peak, G_int, f"G\n{G_peak:.1f}",
        color='green', ha='center')

ax.text(TwoD_peak, TwoD_int, f"2D\n{TwoD_peak:.1f}",
        color='magenta', ha='center')

# Axis labels
ax.set_xlabel("Raman Shift (cm⁻¹)")
ax.set_ylabel("Intensity (a.u.)")
ax.set_title("GNP31RS")

ax.legend()
fig.savefig("Raman_plot_GNP31.png", dpi=300)

# Embed plot into tkinter
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Right Frame → Results

result_frame = tk.Frame(root)
result_frame.pack(side=tk.LEFT, fill=tk.BOTH)

results = f"""
D peak: {D_peak:.2f} cm-1
G peak: {G_peak:.2f} cm-1
2D peak: {TwoD_peak:.2f} cm-1

D int: {D_int:.2f}
G int: {G_int:.2f}
2D int: {TwoD_int:.2f}

ID/IG = {ID_IG:.4f}
I2D/IG = {I2D_IG:.4f}

L_sp2 = {L_sp2:.2f} nm
L_D = {L_D:.2f} nm
n_D = {n_D:.4e}
"""

text_area = ScrolledText(result_frame,
                         font=("Arial", 12),
                         width=50)

text_area.pack(fill=tk.BOTH, expand=True)

text_area.insert(tk.END, results)
text_area.config(state='disabled')
with open("GNP31RR.txt", 'w') as file:
    file.write(results)


def on_closing():
    plt.close('all')
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
