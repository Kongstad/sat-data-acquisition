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

    # Configure search for HLS Sentinel (MPC)
    processing_params = ProcessingParams(
        satellite='HLS_SENTINEL',
        search_method='geometry',
        bands=['B04', 'B03', 'B02'],
        start_date='2024-06-01',
        end_date='2024-06-30',
        clip_method='geometry'
    )

    # Configure save parameters
    save_params = SaveParams(
        output_path='examples/hlsmpc/data',
        save_to_local=True,
        save_as_geotiff=True,
    )

    # Initialize client
    client = SatDataClient()

    print("Searching and downloading HLS Sentinel (MPC) imagery...")
    dataset_s = client.search_and_create_image(
        geometry=geometry,
        processing_params=processing_params,
    )

    print("Searching and downloading HLS Landsat (MPC) imagery...")
    processing_params.satellite = 'HLS_LANDSAT'
    dataset_l = client.search_and_create_image(
        geometry=geometry,
        processing_params=processing_params,
    )

    if dataset_s.time.size > 0:
        print(f"Downloaded {len(dataset_s.time)} HLS Sentinel images.")
        date_str = str(dataset_s.time.values[0])[:10]
        save_data(
            image=dataset_s.isel(time=0),
            identifier='copenhagen_hls_sentinel',
            datetime=date_str,
            satellite='HLS_SENTINEL',
            provider='MPC',
            save_params=save_params,
            band='TCI',
        )
    else:
        print("No HLS Sentinel images found.")

    if dataset_l.time.size > 0:
        print(f"Downloaded {len(dataset_l.time)} HLS Landsat images.")
        date_str = str(dataset_l.time.values[0])[:10]
        save_data(
            image=dataset_l.isel(time=0),
            identifier='copenhagen_hls_landsat',
            datetime=date_str,
            satellite='HLS_LANDSAT',
            provider='MPC',
            save_params=save_params,
            band='TCI',
        )
    else:
        print("No HLS Landsat images found.")
    
    print("Done.")

if __name__ == "__main__":
    main()
