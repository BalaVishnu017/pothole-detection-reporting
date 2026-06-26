"""
InfraVision AI — Improved GPS Log Generator
=============================================
Generates a realistic GPS route log simulating a vehicle
driving along Hyderabad roads with controlled noise.

Usage:
    python scripts/generate_gps.py
    python scripts/generate_gps.py --points 500 --output data/gps_log.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_gps_route(
    lat_start: float = 17.440080,
    lon_start: float = 78.348915,
    num_points: int = 1000,
    speed_kmh: float = 30.0,
    sampling_hz: float = 1.0,
    noise_std: float = 0.00002,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a simulated GPS route log.

    The route moves North-East along a straight path, with small random
    perturbations on both axes to simulate real sensor noise.

    Args:
        lat_start:   Starting latitude (decimal degrees).
        lon_start:   Starting longitude (decimal degrees).
        num_points:  Number of GPS samples to generate.
        speed_kmh:   Simulated vehicle speed in km/h.
        sampling_hz: GPS sampling frequency (samples per second).
        noise_std:   Standard deviation of position noise (degrees).
        seed:        Random seed for reproducibility.

    Returns:
        DataFrame with columns: lat, lon, altitude_m, speed_kmh, timestamp
    """
    rng = np.random.default_rng(seed)

    # Convert speed to degrees-per-sample
    # 1 degree latitude ≈ 111 km → delta_lat per sample
    delta_lat_per_s = (speed_kmh / 3600) / 111.0
    delta_lat = delta_lat_per_s / sampling_hz

    # Slight eastward drift (lon advances slower than lat)
    delta_lon_per_s = (speed_kmh / 3600) / 103.0  # ~103 km/deg at 17°N
    delta_lon = delta_lon_per_s / sampling_hz * 0.4  # partial east

    lats = lat_start + np.arange(num_points) * delta_lat + rng.normal(0, noise_std, num_points)
    lons = lon_start + np.arange(num_points) * delta_lon + rng.normal(0, noise_std, num_points)

    # Simulate gentle altitude variation (Hyderabad is ~500–540 m above sea level)
    altitude = 520 + rng.normal(0, 3, num_points)

    # Simulated speed with small fluctuations
    speed = speed_kmh + rng.normal(0, 2, num_points)
    speed = np.clip(speed, 0, speed_kmh * 1.5)

    # Timestamps starting from midnight today
    timestamps = pd.date_range(
        start="2024-01-15 08:00:00",
        periods=num_points,
        freq=f"{int(1000 / sampling_hz)}ms",
    )

    df = pd.DataFrame(
        {
            "lat": np.round(lats, 7),
            "lon": np.round(lons, 7),
            "altitude_m": np.round(altitude, 1),
            "speed_kmh": np.round(speed, 1),
            "timestamp": timestamps.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
    )

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a simulated GPS route log for InfraVision AI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--lat", type=float, default=17.440080, help="Starting latitude")
    parser.add_argument("--lon", type=float, default=78.348915, help="Starting longitude")
    parser.add_argument("--points", type=int, default=1000, help="Number of GPS samples")
    parser.add_argument("--speed", type=float, default=30.0, help="Simulated speed in km/h")
    parser.add_argument("--output", type=str, default="data/gps_log.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"⚙️  Generating {args.points} GPS points at {args.speed} km/h…")
    df = generate_gps_route(
        lat_start=args.lat,
        lon_start=args.lon,
        num_points=args.points,
        speed_kmh=args.speed,
        seed=args.seed,
    )

    df.to_csv(output_path, index=False)
    print(f"✅ GPS log saved to '{output_path}' ({len(df)} records).")
    print(f"   Start : {df['lat'].iloc[0]:.6f}, {df['lon'].iloc[0]:.6f}")
    print(f"   End   : {df['lat'].iloc[-1]:.6f}, {df['lon'].iloc[-1]:.6f}")


if __name__ == "__main__":
    main()
