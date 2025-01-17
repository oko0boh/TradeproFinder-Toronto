import random
from datetime import datetime

class SEOContentGenerator:
    def __init__(self):
        self.current_year = datetime.now().year
        
    def generate_title(self, service, location):
        """Generate SEO-optimized title."""
        templates = [
            f"Top {service.title()} in {location} - Best Rated {self.current_year}",
            f"Best {service.title()} Services in {location} | Trusted Professionals",
            f"{location}'s Leading {service.title()} | Expert Services {self.current_year}",
            f"Professional {service.title()} in {location} | Top-Rated Experts",
            f"Top-Rated {service.title()} Services {location} | Licensed & Insured"
        ]
        return random.choice(templates)

    def generate_meta_description(self, service, location):
        """Generate SEO-optimized meta description."""
        templates = [
            f"Find the best {service.lower()} in {location}. ✓Licensed ✓Insured ✓Professional {service.lower()} services. Get free quotes & book online. Available 24/7.",
            f"Top-rated {service.lower()} in {location}. Expert {service.lower()} services with years of experience. Read reviews, compare prices, and book instantly.",
            f"Looking for reliable {service.lower()} in {location}? Our verified professionals offer top-quality services. Get instant quotes and same-day service.",
            f"Trusted {service.lower()} serving {location}. Emergency services available. ✓Experienced ✓Affordable ✓Professional. Book your service today!",
            f"Expert {service.lower()} services in {location}. Local, licensed, and insured professionals. Get free estimates and guaranteed satisfaction."
        ]
        return random.choice(templates)

    def generate_h1_heading(self, service, location):
        """Generate SEO-optimized H1 heading."""
        templates = [
            f"Top-Rated {service.title()} Services in {location}",
            f"Professional {service.title()} in {location}",
            f"Expert {service.title()} Services | {location}",
            f"Best {service.title()} in {location} for {self.current_year}",
            f"Licensed & Insured {service.title()} in {location}"
        ]
        return random.choice(templates)

    def generate_intro_text(self, service, location):
        """Generate SEO-optimized introduction text."""
        templates = [
            f"Looking for the best {service.lower()} in {location}? Our network of verified professionals provides top-quality services with guaranteed satisfaction. Get instant quotes and book your service today.",
            f"Need a reliable {service.lower()} in {location}? We connect you with experienced, licensed, and insured professionals who deliver exceptional service. Compare reviews and prices to find the perfect match.",
            f"Discover the top-rated {service.lower()} services in {location}. Our carefully vetted professionals are ready to help with any project, big or small. Get free estimates and same-day service availability.",
            f"Find expert {service.lower()} in {location} through our trusted network. All professionals are thoroughly vetted and come highly recommended. Book with confidence and get the quality service you deserve.",
            f"Connect with the best {service.lower()} in {location}. Our platform makes it easy to find reliable professionals with proven track records. Read verified reviews and make an informed choice."
        ]
        return random.choice(templates)

    def generate_schema_data(self, service, location, businesses):
        """Generate Schema.org structured data."""
        return {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": f"{service.title()} Services in {location}",
            "description": self.generate_meta_description(service, location),
            "areaServed": {
                "@type": "City",
                "name": location
            },
            "serviceType": service.title(),
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.8",
                "reviewCount": "100+"
            },
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"https://tradeprofinder.toronto/search?category={service}&location={location}"
                }
            }
        }

    def generate_why_choose_points(self, service):
        """Generate why choose us points."""
        return [
            "✓ Licensed & Insured Professionals",
            "✓ Free Quotes & Estimates",
            "✓ Emergency Services Available",
            f"✓ Experienced {service.title()} Experts",
            "✓ Satisfaction Guaranteed",
            "✓ Competitive Pricing",
            "✓ Background-Checked Professionals",
            "✓ 24/7 Customer Support"
        ]

    def generate_faq_schema(self, service, location):
        """Generate FAQ Schema.org data."""
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"How do I find a reliable {service.lower()} in {location}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"To find a reliable {service.lower()} in {location}, use our platform to compare verified professionals, read customer reviews, and get free quotes. All our listed professionals are licensed and insured."
                    }
                },
                {
                    "@type": "Question",
                    "name": f"What should I look for when hiring a {service.lower()}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"When hiring a {service.lower()}, look for proper licensing, insurance, experience, and positive customer reviews. Our platform helps you verify these credentials and compare professionals easily."
                    }
                },
                {
                    "@type": "Question",
                    "name": f"How much does a {service.lower()} cost in {location}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"The cost of {service.lower()} services in {location} varies depending on the project scope. Get free quotes from our verified professionals to compare prices and make an informed decision."
                    }
                }
            ]
        }
