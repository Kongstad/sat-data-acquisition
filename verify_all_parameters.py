"""
Comprehensive verification script for all download and save parameters.
Tests various combinations to ensure everything works as expected.
Run this once, verify output, then delete.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

import numpy as np
import rasterio
from shapely.geometry import box

from sat_data_acquisition import SatDataClient, ProcessingParams, SaveParams
from sat_data_acquisition.processing.save import save_data

# Test output directory
TEST_OUTPUT = Path("./test_verification_output")


def cleanup():
    """Remove test output directory."""
    if TEST_OUTPUT.exists():
        shutil.rmtree(TEST_OUTPUT)
        print(f"✓ Cleaned up {TEST_OUTPUT}")


def setup():
    """Create test output directory."""
    cleanup()
    TEST_OUTPUT.mkdir(parents=True)
    print(f"✓ Created {TEST_OUTPUT}")


def get_test_geometry():
    """Small test area in Copenhagen (100x100m)."""
    # Copenhagen city center
    lon, lat = 12.5683, 55.6761
    buffer = 0.0005  # ~50m in each direction
    return box(lon - buffer, lat - buffer, lon + buffer, lat + buffer)


def verify_geotiff(filepath, expected_bands=None):
    """Verify GeoTIFF file structure and metadata."""
    print(f"  Verifying: {filepath.name}")
    
    if not filepath.exists():
        print(f"    ✗ File does not exist!")
        return False
    
    try:
        with rasterio.open(filepath) as src:
            # Check basic properties
            print(f"    - Bands: {src.count}")
            print(f"    - Size: {src.width}x{src.height}")
            print(f"    - CRS: {src.crs}")
            print(f"    - Compression: {src.profile.get('compress', 'none')}")
            
            if expected_bands and src.count != expected_bands:
                print(f"    ✗ Expected {expected_bands} bands, got {src.count}")
                return False
            
            # Check if data is valid
            data = src.read(1)
            if data.size == 0:
                print(f"    ✗ No data in file")
                return False
            
            print(f"    ✓ Valid GeoTIFF")
            return True
    except Exception as e:
        print(f"    ✗ Error reading file: {e}")
        return False


def verify_numpy(filepath):
    """Verify NumPy file."""
    print(f"  Verifying: {filepath.name}")
    
    if not filepath.exists():
        print(f"    ✗ File does not exist!")
        return False
    
    try:
        data = np.load(filepath)
        print(f"    - Shape: {data.shape}")
        print(f"    - Dtype: {data.dtype}")
        
        if data.size == 0:
            print(f"    ✗ No data in file")
            return False
        
        print(f"    ✓ Valid NumPy file")
        return True
    except Exception as e:
        print(f"    ✗ Error reading file: {e}")
        return False


def test_basic_download():
    """Test 1: Basic download with default parameters."""
    print("\n" + "="*70)
    print("TEST 1: Basic Download (Default Parameters)")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red', 'green', 'blue'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    
    if len(dataset.time) == 0:
        print("✗ No images found")
        return False
    
    print(f"✓ Downloaded {len(dataset.time)} images")
    
    # Save with default parameters
    save_params = SaveParams(
        output_path=str(TEST_OUTPUT / "test1_basic"),
        save_to_local=True,
        save_as_geotiff=True,
    )
    
    image = dataset.isel(time=0)
    save_data(
        image=image,
        identifier='copenhagen',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params,
    )
    
    # Verify
    expected_file = TEST_OUTPUT / "test1_basic" / "S2MPC" / "2024" / "tiff"
    files = list(expected_file.glob("*.tif"))
    
    if len(files) == 0:
        print("✗ No output files found")
        return False
    
    return verify_geotiff(files[0], expected_bands=3)


def test_compression():
    """Test 2: Compression enabled vs disabled."""
    print("\n" + "="*70)
    print("TEST 2: Compression Settings")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red', 'green', 'blue'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    # Test with compression
    save_params_compressed = SaveParams(
        output_path=str(TEST_OUTPUT / "test2_compressed"),
        save_to_local=True,
        save_as_geotiff=True,
        enable_compression=True,
    )
    
    save_data(
        image=image,
        identifier='compressed',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_compressed,
    )
    
    # Test without compression
    save_params_uncompressed = SaveParams(
        output_path=str(TEST_OUTPUT / "test2_uncompressed"),
        save_to_local=True,
        save_as_geotiff=True,
        enable_compression=False,
    )
    
    save_data(
        image=image,
        identifier='uncompressed',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_uncompressed,
    )
    
    # Verify both
    compressed_files = list((TEST_OUTPUT / "test2_compressed" / "S2MPC" / "2024" / "tiff").glob("*.tif"))
    uncompressed_files = list((TEST_OUTPUT / "test2_uncompressed" / "S2MPC" / "2024" / "tiff").glob("*.tif"))
    
    result1 = verify_geotiff(compressed_files[0])
    result2 = verify_geotiff(uncompressed_files[0])
    
    # Compare file sizes
    size_compressed = compressed_files[0].stat().st_size
    size_uncompressed = uncompressed_files[0].stat().st_size
    
    print(f"\n  Compressed size: {size_compressed:,} bytes")
    print(f"  Uncompressed size: {size_uncompressed:,} bytes")
    print(f"  Compression ratio: {size_uncompressed/size_compressed:.2f}x")
    
    return result1 and result2


def test_numpy_format():
    """Test 3: NumPy format saving."""
    print("\n" + "="*70)
    print("TEST 3: NumPy Format")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red', 'green'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    save_params = SaveParams(
        output_path=str(TEST_OUTPUT / "test3_numpy"),
        save_to_local=True,
        save_as_numpy=True,
    )
    
    save_data(
        image=image,
        identifier='copenhagen',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params,
    )
    
    # Verify
    npy_files = list((TEST_OUTPUT / "test3_numpy" / "S2MPC" / "2024" / "npy").glob("*.npy"))
    
    if len(npy_files) == 0:
        print("✗ No NumPy files found")
        return False
    
    return verify_numpy(npy_files[0])


def test_custom_naming():
    """Test 4: Custom naming convention."""
    print("\n" + "="*70)
    print("TEST 4: Custom Naming Convention")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    # Custom naming format
    custom_format = "{area_name}_{date}_custom_test.{file_type}"
    
    save_params = SaveParams(
        output_path=str(TEST_OUTPUT / "test4_custom"),
        save_to_local=True,
        save_as_geotiff=True,
        custom_naming=custom_format,
    )
    
    save_data(
        image=image,
        identifier='testarea',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params,
    )
    
    # Verify custom filename exists
    custom_files = list((TEST_OUTPUT / "test4_custom").glob("testarea_*_custom_test.tif"))
    
    if len(custom_files) == 0:
        print("✗ Custom named file not found")
        return False
    
    print(f"  ✓ Custom filename: {custom_files[0].name}")
    return verify_geotiff(custom_files[0])


def test_identifier_types():
    """Test 5: Different identifier types."""
    print("\n" + "="*70)
    print("TEST 5: Identifier Types (area_name, field_id)")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    # Test area_name identifier type
    save_params1 = SaveParams(
        output_path=str(TEST_OUTPUT / "test5_area_name"),
        save_to_local=True,
        save_as_geotiff=True,
        identifier_type='area_name',
    )
    
    save_data(
        image=image,
        identifier='copenhagen_center',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params1,
    )
    
    # Test field_id identifier type
    save_params2 = SaveParams(
        output_path=str(TEST_OUTPUT / "test5_field_id"),
        save_to_local=True,
        save_as_geotiff=True,
        identifier_type='field_id',
    )
    
    save_data(
        image=image,
        identifier='field_12345',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params2,
    )
    
    # Verify both
    area_files = list((TEST_OUTPUT / "test5_area_name" / "S2MPC" / "2024" / "tiff").glob("*copenhagen_center*"))
    field_files = list((TEST_OUTPUT / "test5_field_id" / "S2MPC" / "2024" / "tiff").glob("*field_12345*"))
    
    if len(area_files) == 0:
        print("✗ Area name file not found")
        return False
    
    if len(field_files) == 0:
        print("✗ Field ID file not found")
        return False
    
    print(f"  ✓ Area name: {area_files[0].name}")
    print(f"  ✓ Field ID: {field_files[0].name}")
    
    return verify_geotiff(area_files[0]) and verify_geotiff(field_files[0])


def test_multiple_satellites():
    """Test 6: Different satellite sources."""
    print("\n" + "="*70)
    print("TEST 6: Multiple Satellite Sources")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    # Test S2MPC
    print("\n  Testing S2MPC...")
    params_s2mpc = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red', 'green'],
        cloud_coverage=20,
    )
    
    dataset_s2mpc = client.search_and_create_image(geometry=geometry, processing_params=params_s2mpc)
    
    save_params = SaveParams(
        output_path=str(TEST_OUTPUT / "test6_satellites"),
        save_to_local=True,
        save_as_geotiff=True,
    )
    
    if len(dataset_s2mpc.time) > 0:
        image = dataset_s2mpc.isel(time=0)
        save_data(
            image=image,
            identifier='test',
            datetime=str(image.time.values),
            satellite='S2MPC',
            provider='MPC',
            save_params=save_params,
        )
        print("  ✓ S2MPC download successful")
    
    # Test Landsat
    print("\n  Testing LANDSATMPC...")
    params_landsat = ProcessingParams(
        satellite='LANDSATMPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-30',
        bands=['red', 'green'],
        cloud_coverage=30,
    )
    
    dataset_landsat = client.search_and_create_image(geometry=geometry, processing_params=params_landsat)
    
    if len(dataset_landsat.time) > 0:
        image = dataset_landsat.isel(time=0)
        save_data(
            image=image,
            identifier='test',
            datetime=str(image.time.values),
            satellite='LANDSATMPC',
            provider='MPC',
            save_params=save_params,
        )
        print("  ✓ LANDSATMPC download successful")
    
    # Verify directory structure
    s2_files = list((TEST_OUTPUT / "test6_satellites" / "S2MPC").glob("**/*.tif"))
    landsat_files = list((TEST_OUTPUT / "test6_satellites" / "LANDSATMPC").glob("**/*.tif"))
    
    print(f"\n  S2MPC files: {len(s2_files)}")
    print(f"  LANDSATMPC files: {len(landsat_files)}")
    
    return len(s2_files) > 0 and len(landsat_files) > 0


def test_merge_bands():
    """Test 7: Merge bands vs separate files for GeoTIFF and NumPy."""
    print("\n" + "="*70)
    print("TEST 7: Band Merging (GeoTIFF and NumPy)")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red', 'green', 'blue'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    # Test 1: Merged bands GeoTIFF
    print("\n  Testing merged bands (GeoTIFF)...")
    save_params_merged_tiff = SaveParams(
        output_path=str(TEST_OUTPUT / "test7_merged_tiff"),
        save_to_local=True,
        save_as_geotiff=True,
        merge_bands=True,
    )
    
    save_data(
        image=image,
        identifier='test',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_merged_tiff,
    )
    
    merged_tiff_files = list((TEST_OUTPUT / "test7_merged_tiff" / "S2MPC" / "2024" / "tiff").glob("*_merged_*"))
    
    if len(merged_tiff_files) == 0:
        print("  ✗ Merged GeoTIFF not found")
        return False
    
    print(f"  ✓ Merged GeoTIFF: {merged_tiff_files[0].name}")
    result1 = verify_geotiff(merged_tiff_files[0], expected_bands=3)
    
    # Test 2: Separate band files GeoTIFF
    print("\n  Testing separate band files (merge_bands=False, GeoTIFF)...")
    save_params_separate_tiff = SaveParams(
        output_path=str(TEST_OUTPUT / "test7_separate_tiff"),
        save_to_local=True,
        save_as_geotiff=True,
        merge_bands=False,
    )
    
    save_data(
        image=image,
        identifier='test',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_separate_tiff,
    )
    
    separate_tiff_files = list((TEST_OUTPUT / "test7_separate_tiff" / "S2MPC" / "2024" / "tiff").glob("*.tif"))
    print(f"  Found {len(separate_tiff_files)} GeoTIFF file(s)")
    
    if len(separate_tiff_files) == 0:
        print("  ✗ No separate GeoTIFF files found")
        return False
    
    for f in separate_tiff_files:
        print(f"    - {f.name}")
        verify_geotiff(f)
    
    result2 = len(separate_tiff_files) > 0
    
    # Test 3: Merged bands NumPy
    print("\n  Testing merged bands (NumPy)...")
    save_params_merged_npy = SaveParams(
        output_path=str(TEST_OUTPUT / "test7_merged_npy"),
        save_to_local=True,
        save_as_numpy=True,
        merge_bands=True,
    )
    
    save_data(
        image=image,
        identifier='test',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_merged_npy,
    )
    
    merged_npy_files = list((TEST_OUTPUT / "test7_merged_npy" / "S2MPC" / "2024" / "npy").glob("*_merged_*"))
    
    if len(merged_npy_files) == 0:
        print("  ✗ Merged NumPy not found")
        return False
    
    print(f"  ✓ Merged NumPy: {merged_npy_files[0].name}")
    result3 = verify_numpy(merged_npy_files[0])
    
    # Check that NumPy has all 3 bands in one array
    data = np.load(merged_npy_files[0])
    if data.shape[0] != 3:
        print(f"  ✗ Expected 3 bands, got {data.shape[0]}")
        return False
    
    print(f"  ✓ NumPy array contains {data.shape[0]} bands")
    
    # Test 4: Separate band files NumPy
    print("\n  Testing separate band files (merge_bands=False, NumPy)...")
    save_params_separate_npy = SaveParams(
        output_path=str(TEST_OUTPUT / "test7_separate_npy"),
        save_to_local=True,
        save_as_numpy=True,
        merge_bands=False,
    )
    
    save_data(
        image=image,
        identifier='test',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params_separate_npy,
    )
    
    separate_npy_files = list((TEST_OUTPUT / "test7_separate_npy" / "S2MPC" / "2024" / "npy").glob("*.npy"))
    print(f"  Found {len(separate_npy_files)} NumPy file(s)")
    
    if len(separate_npy_files) == 0:
        print("  ✗ No separate NumPy files found")
        return False
    
    for f in separate_npy_files:
        print(f"    - {f.name}")
        verify_numpy(f)
    
    result4 = len(separate_npy_files) > 0
    
    return result1 and result2 and result3 and result4


def test_both_formats():
    """Test 8: Save as both GeoTIFF and NumPy."""
    print("\n" + "="*70)
    print("TEST 8: Save Both Formats")
    print("="*70)
    
    client = SatDataClient()
    geometry = get_test_geometry()
    
    params = ProcessingParams(
        satellite='S2MPC',
        search_method='geometry',
        start_date='2024-06-01',
        end_date='2024-06-15',
        bands=['red'],
        cloud_coverage=20,
    )
    
    dataset = client.search_and_create_image(geometry=geometry, processing_params=params)
    image = dataset.isel(time=0)
    
    save_params = SaveParams(
        output_path=str(TEST_OUTPUT / "test8_both"),
        save_to_local=True,
        save_as_geotiff=True,
        save_as_numpy=True,
    )
    
    save_data(
        image=image,
        identifier='test',
        datetime=str(image.time.values),
        satellite='S2MPC',
        provider='MPC',
        save_params=save_params,
    )
    
    # Verify both formats exist
    tiff_files = list((TEST_OUTPUT / "test8_both" / "S2MPC" / "2024" / "tiff").glob("*.tif"))
    npy_files = list((TEST_OUTPUT / "test8_both" / "S2MPC" / "2024" / "npy").glob("*.npy"))
    
    if len(tiff_files) == 0:
        print("✗ GeoTIFF file not found")
        return False
    
    if len(npy_files) == 0:
        print("✗ NumPy file not found")
        return False
    
    print(f"  ✓ GeoTIFF: {tiff_files[0].name}")
    print(f"  ✓ NumPy: {npy_files[0].name}")
    
    return verify_geotiff(tiff_files[0]) and verify_numpy(npy_files[0])


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("COMPREHENSIVE PARAMETER VERIFICATION")
    print("="*70)
    print(f"Output directory: {TEST_OUTPUT}")
    print("Testing all download and save parameter combinations...")
    
    setup()
    
    tests = [
        ("Basic Download", test_basic_download),
        ("Compression", test_compression),
        ("NumPy Format", test_numpy_format),
        ("Custom Naming", test_custom_naming),
        ("Identifier Types", test_identifier_types),
        ("Multiple Satellites", test_multiple_satellites),
        ("Band Merging", test_merge_bands),
        ("Both Formats", test_both_formats),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")
    
    print(f"\nTest output saved to: {TEST_OUTPUT}")
    print("Review the files, then run cleanup() to remove test data.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    
    # Optional: Uncomment to auto-cleanup after successful tests
    # if success:
    #     cleanup()
