#!/usr/bin/env python3
import os
from utils.page_generator import PageGenerator
from utils.sitemap_generator import SitemapGenerator

def main():
    # Initialize generators
    page_generator = PageGenerator(
        template_dir='templates',
        output_dir='generated_pages',
        base_url='https://tradeprofinder.toronto'
    )
    sitemap_generator = SitemapGenerator()
    
    print("Starting SEO page generation...")
    
    # Generate all service-location pages
    page_generator.generate_pages(
        services_file='data/tradepro_finder_toronto_keywords.csv',
        locations_file='data/tradepro_finder_cities.csv'
    )
    
    print("Generating sitemap...")
    
    # Generate sitemap
    sitemap_content = sitemap_generator.generate_sitemap_xml(
        services_file='data/tradepro_finder_toronto_keywords.csv',
        locations_file='data/tradepro_finder_cities.csv'
    )
    
    # Write sitemap
    with open('static/sitemap.xml', 'w') as f:
        f.write(sitemap_content)
    
    print("Done! Generated pages can be found in the 'generated_pages' directory.")
    print("Sitemap has been updated at 'static/sitemap.xml'")

if __name__ == "__main__":
    main()
