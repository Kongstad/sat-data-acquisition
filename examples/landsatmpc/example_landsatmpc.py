from sat_data_acquisition import SatDataClient, ProcessingParams, SaveParams
from sat_data_acquisition.processing import save_data
from shapely.geometry import Point, box
import os

def main():
    # Define area as bounding box (rectangular shape)
    copenhagen_center = Point(12.5683, 55.6761)  # lon, lat
    buffer = 0.024  # ~5 km

    geometry = box(
        copenhagen_center.x - buffer,
        copenhagen_center.y - buffer,
        copenhagen_center.x + buffer,
        copenhagen_center.y + buffer
    )

    # Configure search for Landsat MPC
    processing_params = ProcessingParams(
        satellite='LANDSATMPC',
        search_method='geometry',
        bands=['red', 'green', 'blue'],
        start_date='2024-06-01',
        end_date='2024-08-31',
        cloud_coverage=50,
        clip_method='geometry'
    )

    # Configure save parameters
    save_params = SaveParams(
        output_path='examples/landsatmpc/data',
        save_to_local=True,
        save_as_geotiff=True,
    )

    # Initialize client
    client = SatDataClient()

    print("Searching and downloading Landsat (MPC) imagery...")
    # Download
    dataset = client.search_and_create_image(
        geometry=geometry,
        processing_params=processing_params,
    )

    if dataset.time.size == 0:
        print("No images found for the given criteria.")
        return

    print(f"Downloaded {len(dataset.time)} images.")

    # Save the first image using the cleaner save_data interface
    time_val = dataset.time.values[0]
    date_str = str(time_val)[:10]
    
    print(f"Saving image from {date_str}...")
    save_data(
        image=dataset.isel(time=0),
        identifier='copenhagen_landsatmpc',
        datetime=date_str,
        satellite='LANDSATMPC',
        provider='MPC',
        save_params=save_params,
        band='TCI',
    )
    print("Done.")

if __name__ == "__main__":
    main()
