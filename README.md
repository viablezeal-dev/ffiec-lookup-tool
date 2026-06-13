# FFIEC Lookup Tool

A Python desktop tool that helps look up FFIEC census tract and income information for lending-support workflows.

## What it does

- Looks up census tract information by address
- Uses the U.S. Census Geocoder API when available
- Uses local FFIEC/Census data files for income, MFI, and distressed/underserved tract information
- Supports single-address lookup
- Supports batch Excel lookup
- Provides lookup method and confidence score
- Creates a local lookup log

## Why I built it

I built this after the official FFIEC/Census lookup process was unavailable or unreliable. The goal was to provide a backup workflow tool that could continue helping with tract and income classification lookups, especially for batch processing.

## Important note

This tool is a supplemental workflow aid, not the official system of record. Results should be verified against official FFIEC/Census resources before being used for compliance, CRA, lending, audit, or other sensitive decisions.

## Data files

Large FFIEC/Census data files are not included in this repository.

To run the tool, download the needed public datasets from FFIEC/Census sources and place them in the same folder as `ffiec_tool.py`.

Expected file names:

```text
CensusTractList2026.xlsx
CensusFlatFile2025.csv
2025DistressedorUnderservedTracts.xls
