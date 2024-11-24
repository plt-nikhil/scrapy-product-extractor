# Product Data Scrapy Spider

This Scrapy spider scrapes product details from an e-commerce website and exports the data to an Excel file.

## Features
- Scrapes product categories and individual product details.
- Extracts information such as:
  - Product name, description, price
  - Size, color, material
  - Main image and additional image URLs
  - Download links (if available)
- Exports data to an Excel file (`products_data.xlsx`).

## Requirements
- [Scrapy](https://scrapy.org/)
- [scrapy-xlsx](https://pypi.org/project/scrapy-xlsx/)

To install dependencies, run:
```bash
pip install scrapy scrapy-xlsx
