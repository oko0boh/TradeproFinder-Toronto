import pandas as pd
from datetime import datetime
from urllib.parse import quote

class SitemapGenerator:
    def __init__(self, base_url="https://tradeprofinder.toronto"):
        self.base_url = base_url.rstrip('/')
        
    def generate_url_slug(self, service, location):
        """Generate SEO-friendly URL slug."""
        service_slug = quote(service.lower().replace(' ', '-'))
        location_slug = quote(location.lower().replace(' ', '-'))
        return f"{service_slug}-{location_slug}"
    
    def generate_sitemap_xml(self, services_file, locations_file):
        """Generate sitemap.xml content."""
        services_df = pd.read_csv(services_file)
        locations_df = pd.read_csv(locations_file)
        
        # Start sitemap XML
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        # Add homepage
        sitemap += self._create_url_entry(self.base_url)
        
        # Add service-location combination pages
        for service in services_df['Category']:
            for location in locations_df['Location']:
                url_slug = self.generate_url_slug(service, location)
                full_url = f"{self.base_url}/{url_slug}"
                sitemap += self._create_url_entry(full_url)
        
        sitemap += '</urlset>'
        return sitemap
    
    def _create_url_entry(self, url, changefreq='weekly', priority='0.8'):
        """Create a single URL entry for sitemap."""
        entry = '  <url>\n'
        entry += f'    <loc>{url}</loc>\n'
        entry += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        entry += f'    <changefreq>{changefreq}</changefreq>\n'
        entry += f'    <priority>{priority}</priority>\n'
        entry += '  </url>\n'
        return entry
