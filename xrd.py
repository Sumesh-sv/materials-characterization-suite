import numpy as np
import pandas as pd

K = 0.9
lam = 0.154056  # nm for Cu Kα

# Number of materials
n_materials = int(input("Enter the number of materials: "))

results = []

for i in range(n_materials):
    print(f"\nMaterial {i + 1}")

    material = input("Material name: ")

    theta_2 = float(input("Enter 2θ (degrees): "))
    theta = theta_2 / 2
    theta_rad = np.radians(theta)

    dbeta = float(input("Enter FWHM β (degrees): "))
    beta = np.radians(dbeta)

    # Calculations
    d = lam / (2 * np.sin(theta_rad))
    La = (K * lam) / (beta * np.cos(theta_rad))
    layers = La / d

    results.append({
        "Material": material,
        "2θ (°)": theta_2,
        "FWHM β (°)": dbeta,
        "d (nm)": round(d, 4),
        "Crystallite Size (nm)": round(La, 2),
        "Average Layers": round(layers, 1)
    })

# Create DataFrame
df = pd.DataFrame(results)

print("\nResults:\n")
print(df.to_string(index=False))
df.to_excel("XRD_Results.xlsx", index=False)