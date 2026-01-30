import rasterio
import numpy as np
import os
import glob

def inspect_geotiff(file_path):
    print(f"\nInspecting: {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist!")
        return

    with rasterio.open(file_path) as src:
        print(f"  Dimensions: {src.width}x{src.height}")
        print(f"  Bands: {src.count}")
        print(f"  CRS: {src.crs}")
        print(f"  Transform: {src.transform}")
        
        for i in range(1, src.count + 1):
            data = src.read(i)
            print(f"  Band {i}: min={np.min(data)}, max={np.max(data)}, mean={np.mean(data):.2f}, dtype={data.dtype}")

def main():
    # Find all .tif files in examples directory
    tif_files = glob.glob("examples/**/*.tif", recursive=True)
    
    if not tif_files:
        print("No .tif files found to inspect.")
        return
        
    for tif_file in tif_files:
        inspect_geotiff(tif_file)

if __name__ == "__main__":
    main()
