import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Load data
with open('../coordinates/spectrum_processed.csv') as f:
  reader = csv.reader(f)
  data = list(reader)

freq = np.array([float(row[0]) for row in data[1:]])
intensity = np.array([float(row[1]) for row in data[1:]])

# Smoothing
smooth_intensity = savgol_filter(intensity, 15, 3)

# Baseline correction  
baseline = np.polyfit(freq, smooth_intensity, 1)
base_corrected = smooth_intensity - np.polyval(baseline, freq)

# Find peaks 
peaks = []
for i in range(1, len(base_corrected)-1):
  if base_corrected[i] > base_corrected[i-1] and base_corrected[i] > base_corrected[i+1]:
    peaks.append(i)

# Integrate peaks
peak_freqs = freq[peaks]
integrals = []
for peak in peak_freqs:
  idx = np.argmin(np.abs(freq - peak))
  integral = np.trapz(base_corrected[idx-5:idx+5], freq[idx-5:idx+5])
  integrals.append(integral)
  
# Estimate protons
n_protons = np.array(integrals) / max(integrals)

# Plot
plt.plot(freq, intensity, label='Original')
plt.plot(freq, base_corrected, label='Corrected')
plt.xlabel('Frequency (ppm)')
plt.ylabel('Intensity')
plt.title('NMR Spectrum')
plt.legend()
plt.show()

print('Peak frequencies:', peak_freqs)
print('Peak integrals:', integrals)  
print('Estimated protons:', n_protons)
