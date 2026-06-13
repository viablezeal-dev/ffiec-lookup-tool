# FFIEC Lookup Tool

A Python desktop application that streamlines FFIEC census tract lookups and income classification workflows using publicly available Census and FFIEC data sources.

## Overview

The FFIEC Lookup Tool was developed to improve the speed and consistency of census tract identification and tract income classification. It combines Census geocoding services with locally maintained FFIEC datasets to provide a single workflow for address-based tract lookup and reporting.

The project was originally created after experiencing limitations and outages in the traditional lookup process and has since evolved into a standalone workflow tool for tract research and lending-support activities.

## Features

### Single Address Lookup

* Census tract identification by address
* Tract income level lookup
* Median Family Income (MFI) percentage lookup
* Distressed or underserved tract identification
* Confidence scoring
* Lookup method tracking
* Local audit-style logging

### Lookup Logic

The application attempts multiple lookup methods to maximize successful tract identification:

1. Census Geocoder API exact match
2. Address normalization and simplification
3. Nearby address matching
4. ZIP/city approximation
5. County-level fallback logic

Each result includes both a confidence score and the method used to obtain the tract information.

## Technologies Used

* Python
* Pandas
* Requests
* Tkinter
* Excel Processing
* U.S. Census Geocoder API
* FFIEC Public Data Files

## Data Sources

This project utilizes publicly available datasets and services, including:

* FFIEC Census Tract Lists
* FFIEC Census Flat Files
* FFIEC Distressed or Underserved Tract Lists
* U.S. Census Geocoder API

Large source datasets are not included in this repository.

Expected file names:

```text
CensusTractList2026.xlsx
CensusFlatFile2025.csv
2025DistressedorUnderservedTracts.xls
```

Place the required data files in the same directory as `ffiec_tool.py`.

## Current Status

### Working Features

* Single-address lookup
* Census tract identification
* FFIEC income classification lookup
* MFI percentage lookup
* Distressed/underserved tract identification
* Confidence scoring
* Lookup method reporting
* Local activity logging

### Known Issues

* Batch Excel processing is currently being refined and tested.
* Output workbook generation is not consistently created in all packaged executable builds.
* Additional error handling and user feedback mechanisms are planned for future releases.

### Planned Improvements

* Improved batch processing reliability
* Enhanced error reporting and diagnostics
* Automatic data validation
* Improved executable packaging
* Dataset update automation
* Additional reporting and export options

## Documentation Note

The included user guide reflects the intended functionality and workflow of the application at the time it was written. While most documented features are operational, some functionality remains under active development and testing. Known issues and development status are documented within this repository.

## Why I Built This

This project was built to solve a real operational problem: quickly identifying census tracts and associated FFIEC income classifications while maintaining workflow continuity during external service interruptions. It also served as an opportunity to further develop skills in Python, API integration, data processing, desktop application development, and workflow automation.

## Disclaimer

This application is intended as a supplemental workflow aid and educational portfolio project. It is not an official FFIEC product and should not be considered a system of record. Results should always be verified through official FFIEC and Census resources when used for lending, CRA, compliance, audit, or regulatory purposes.
