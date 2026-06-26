import pandas as pd
import numpy as np

# Create 1000 fake GPS points starting at Hyderabad
# (Simulating a drive along a road)
lat_start = 17.440080
lon_start = 78.348915

# Generate points that move slightly to simulate driving
data = []
for i in range(1000):
    lat = lat_start + (i * 0.0001)  # Moving North
    lon = lon_start + (np.random.normal(0, 0.00002)) # Slight wobble
    data.append([lat, lon])

# Save to CSV
df = pd.DataFrame(data, columns=['lat', 'lon'])
df.to_csv('gps_log.csv', index=False)
print("✅ gps_log.csv created successfully!")