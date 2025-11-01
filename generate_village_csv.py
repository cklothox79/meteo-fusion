import pandas as pd

sample = [
    {"name": "Simogirang", "lat": -7.563, "lon": 112.123},
    {"name": "Surabaya", "lat": -7.249, "lon": 112.750},
    {"name": "Malang", "lat": -7.979, "lon": 112.630},
]

df = pd.DataFrame(sample)
df.to_csv("data/Village_LongLat_Approx.csv", index=False)
print("Contoh CSV dibuat di data/Village_LongLat_Approx.csv")
