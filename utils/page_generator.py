import os
import pandas as pd
from .seo_content_generator import SEOContentGenerator
from jinja2 import Environment, FileSystemLoader
from flask import Flask

class PageGenerator:
    def __init__(self, template_dir, output_dir, base_url="https://tradeprofinder.toronto"):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.base_url = base_url
        self.seo_generator = SEOContentGenerator()
        
        # Create a Flask app for template rendering
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder='static')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Add url_for to template environment
        self.env.globals['url_for'] = self._mock_url_for
        
    def _mock_url_for(self, endpoint, **values):
        """Mock url_for function for static files."""
        if endpoint == 'static':
            return f"/static/{values['filename']}"
        return f"/{endpoint}"
        
    def generate_pages(self, services_file, locations_file):
        """Generate all service-location combination pages."""
        services_df = pd.read_csv(services_file)
        locations_df = pd.read_csv(locations_file)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get top 25 services
        top_services = services_df.head(25)['Category'].tolist()
        
        # Generate pages for each service-location combination
        for service in top_services:
            for location in locations_df['Location']:
                self._generate_single_page(service, location)
                
    def _generate_single_page(self, service, location):
        """Generate a single service-location page."""
        # Generate SEO content
        title = self.seo_generator.generate_title(service, location)
        meta_description = self.seo_generator.generate_meta_description(service, location)
        h1_heading = self.seo_generator.generate_h1_heading(service, location)
        intro_text = self.seo_generator.generate_intro_text(service, location)
        schema_data = self.seo_generator.generate_schema_data(service, location, [])
        faq_schema = self.seo_generator.generate_faq_schema(service, location)
        why_choose = self.seo_generator.generate_why_choose_points(service)
        
        # Prepare meta data
        meta = {
            'title': title,
            'description': meta_description,
            'keywords': f"{service}, {location}, best {service}, top {service}, professional {service}, {service} services",
            'url': f"{self.base_url}/{service.lower().replace(' ', '-')}-{location.lower().replace(' ', '-')}",
            'image': f"{self.base_url}/static/images/services/{service.lower().replace(' ', '-')}.jpg"
        }
        
        # Prepare content data
        content = {
            'main_heading': h1_heading,
            'intro_text': intro_text,
            'schema_data': schema_data,
            'faq_schema': faq_schema,
            'why_choose': why_choose,
            'service_areas': f"Serving all areas in {location} and surrounding neighborhoods"
        }
        
        # Load and render template
        template = self.env.get_template('service_location.html')
        rendered_html = template.render(
            meta=meta,
            content=content,
            service=service,
            location=location
        )
        
        # Create directory structure
        page_dir = os.path.join(self.output_dir, service.lower().replace(' ', '-'))
        os.makedirs(page_dir, exist_ok=True)
        
        # Write the file
        file_path = os.path.join(page_dir, f"{location.lower().replace(' ', '-')}.html")
        with open(file_path, 'w') as f:
            f.write(rendered_html)
        
        return file_path
