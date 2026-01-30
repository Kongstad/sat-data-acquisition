"""
Demonstration of merge_bands parameter functionality.

This example shows the difference between:
- merge_bands=True: Saves all bands in a single multi-band file
- merge_bands=False: Saves each band as a separate single-band file
"""

from shapely.geometry import box

from sat_data_acquisition import ProcessingParams, SaveParams, SatDataClient

# Define a small area of interest (Copenhagen, Denmark)
bbox = box(12.5683, 55.6761, 12.5783, 55.6811)

# ===== Example 1: Merged Bands (Default) =====
print("Example 1: Saving as merged multi-band files")
print("=" * 60)

save_params_merged = SaveParams(
    output_path="./data/merged_example",
    save_to_local=True,
    save_as_geotiff=True,
    save_as_numpy=True,
    merge_bands=True,  # Default - saves single multi-band file
)

processing_params = ProcessingParams(
    satellite="S2MPC",
    search_method="geometry",
    start_date="2024-06-01",
    end_date="2024-06-05",
    max_cloud_cover=20,
    bands=["red", "green", "blue"],
)

client = SatDataClient()

print("Downloading and saving merged files...")
for item_data in client.get_data(
    geometry=bbox,
    processing_params=processing_params,
    save_params=save_params_merged,
    identifier="copenhagen",
):
    print(f"  Saved merged file for {item_data['datetime']}")

print("\nOutput structure (merged):")
print("  data/merged_example/S2MPC/2024/tiff/")
print("    └── S2MPC_2024-06-02_merged_copenhagen.tif  (3 bands in 1 file)")
print("  data/merged_example/S2MPC/2024/npy/")
print("    └── S2MPC_2024-06-02_merged_copenhagen.npy  (shape: 3, h, w)")
print()

# ===== Example 2: Separate Band Files =====
print("\nExample 2: Saving as separate band files")
print("=" * 60)

save_params_separate = SaveParams(
    output_path="./data/separate_example",
    save_to_local=True,
    save_as_geotiff=True,
    save_as_numpy=True,
    merge_bands=False,  # Saves separate file per band
)

print("Downloading and saving separate band files...")
for item_data in client.get_data(
    geometry=bbox,
    processing_params=processing_params,
    save_params=save_params_separate,
    identifier="copenhagen",
):
    print(f"  Saved separate band files for {item_data['datetime']}")

print("\nOutput structure (separate):")
print("  data/separate_example/S2MPC/2024/tiff/")
print("    ├── S2MPC_2024-06-02_red_copenhagen.tif    (1 band)")
print("    ├── S2MPC_2024-06-02_green_copenhagen.tif  (1 band)")
print("    └── S2MPC_2024-06-02_blue_copenhagen.tif   (1 band)")
print("  data/separate_example/S2MPC/2024/npy/")
print("    ├── S2MPC_2024-06-02_red_copenhagen.npy    (shape: h, w)")
print("    ├── S2MPC_2024-06-02_green_copenhagen.npy  (shape: h, w)")
print("    └── S2MPC_2024-06-02_blue_copenhagen.npy   (shape: h, w)")
print()

# ===== Recommendations =====
print("\nRecommendations:")
print("=" * 60)
print("• Use merge_bands=True (default) for:")
print("  - Standard remote sensing workflows")
print("  - Visualization and analysis in QGIS/ArcGIS")
print("  - Machine learning with multi-band inputs")
print("  - More efficient storage and faster loading")
print()
print("• Use merge_bands=False when:")
print("  - Processing bands individually")
print("  - Only using a subset of bands in downstream tasks")
print("  - Integrating with systems expecting single-band files")
print("  - Need flexibility to work with bands separately")
