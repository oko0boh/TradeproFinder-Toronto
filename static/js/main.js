// Debug flag
const DEBUG = true;

function debug(message) {
    if (DEBUG) {
        console.log('Debug:', message);
    }
}

let nextPageToken = '';
const RESULTS_PER_PAGE = 10;

// Function to format rating stars
function formatRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star text-warning"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt text-warning"></i>';
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star text-warning"></i>';
    }
    return stars;
}

// Function to display search results
function displayResults(data) {
    console.log('\n=== DISPLAYING RESULTS ===');
    console.log('Results data:', data);
    
    const resultsContainer = document.getElementById('search-results');
    const totalResults = document.getElementById('total-results');
    const loadMoreBtn = document.getElementById('load-more-btn');
    
    if (!resultsContainer || !totalResults || !loadMoreBtn) {
        console.error('Required elements not found');
        return;
    }
    
    // Update total results count
    if (data.total_results !== undefined) {
        totalResults.textContent = `Found ${data.total_results} results (showing ${data.current_count})`;
        console.log(`Total results: ${data.total_results}, Current count: ${data.current_count}`);
    }
    
    // Clear results if this is the first page
    if (!data.from_cache && !currentPageToken) {
        resultsContainer.innerHTML = '';
        console.log('Clearing previous results');
    }
    
    // Display places
    if (data.places && data.places.length > 0) {
        data.places.forEach(place => {
            const card = createBusinessCard(place);
            resultsContainer.appendChild(card);
        });
        console.log(`Added ${data.places.length} places to the display`);
        
        // Show load more button if there are more results
        if (data.has_more && data.next_page) {
            loadMoreBtn.style.display = 'block';
            currentPageToken = data.next_page;
            console.log('Show load more button with token:', currentPageToken);
        } else {
            loadMoreBtn.style.display = 'none';
            currentPageToken = null;
            console.log('Hide load more button - no more results');
        }
    } else {
        if (!currentPageToken) {  // Only show no results message on first page
            resultsContainer.innerHTML = '<div class="col-12"><p class="text-center">No results found</p></div>';
            console.log('No results found');
        }
        loadMoreBtn.style.display = 'none';
        currentPageToken = null;
        console.log('Hide load more button - no results');
    }
}

// Function to create business card
function createBusinessCard(business) {
    // Generate rating stars
    const rating = business.rating || 0;
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    const starsHTML = Array(fullStars).fill('<i class="fas fa-star"></i>').join('') +
                     (hasHalfStar ? '<i class="fas fa-star-half-alt"></i>' : '') +
                     Array(emptyStars).fill('<i class="far fa-star"></i>').join('');
    
    const card = document.createElement('div');
    card.className = 'col-md-6 mb-4';
    card.innerHTML = `
        <div class="business-card">
            <div class="card-body">
                <h5 class="card-title mb-3">${business.name}</h5>
                
                <div class="business-info">
                    ${business.address ? `
                        <p class="mb-2">
                            <i class="fas fa-map-marker-alt"></i>
                            ${business.address}
                        </p>
                    ` : ''}
                    
                    ${business.phone ? `
                        <p class="mb-2">
                            <i class="fas fa-phone"></i>
                            ${business.phone}
                        </p>
                    ` : ''}
                    
                    ${business.rating ? `
                        <p class="mb-2">
                            <span class="rating-stars">${starsHTML}</span>
                            ${business.rating}
                            ${business.reviews ? `(${business.reviews} reviews)` : ''}
                        </p>
                    ` : ''}
                    
                    ${business.opening_hours ? `
                        <p class="mb-2">
                            <i class="fas fa-clock"></i>
                            <span class="${business.opening_hours.open_now ? 'open-badge' : 'closed-badge'}">
                                ${business.opening_hours.open_now ? 'Open Now' : 'Closed'}
                            </span>
                        </p>
                    ` : ''}
                    
                    ${business.business_type ? `
                        <p class="mb-2">
                            <i class="fas fa-tag"></i>
                            ${business.business_type}
                        </p>
                    ` : ''}
                </div>
                
                <div class="mt-3 d-flex flex-wrap gap-2">
                    ${business.phone ? `
                        <a href="tel:${business.phone}" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-phone"></i> Call
                        </a>
                    ` : ''}
                    
                    ${business.website ? `
                        <a href="${business.website}" target="_blank" class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-globe"></i> Website
                        </a>
                    ` : ''}
                    
                    <button class="btn btn-success btn-sm" onclick='openQuoteModal(${JSON.stringify(business)})'>
                        <i class="fas fa-file-invoice-dollar"></i> Get Quote
                    </button>
                </div>
            </div>
        </div>
    `;
    return card;
}

// Global variables
let currentPageToken = null;
let currentResultCount = 0;

// Function to show error messages
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.container').firstChild);
}

// Function to populate categories dropdown
async function loadCategories() {
    console.log('Loading categories...');
    const categorySelect = document.getElementById('category-select');
    
    if (!categorySelect) {
        console.error('Category select element not found');
        return;
    }
    
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const categories = await response.json();
        console.log('Categories loaded:', categories);
        
        // Clear existing options
        categorySelect.innerHTML = '<option value="">Select a Service</option>';
        
        // Add new options
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
        
        console.log('Categories populated successfully');
    } catch (error) {
        console.error('Error loading categories:', error);
        showError('Error loading categories. Please refresh the page.');
    }
}

// Function to populate locations dropdown
async function loadLocations() {
    console.log('Loading locations...');
    const locationSelect = document.getElementById('location-select');
    
    if (!locationSelect) {
        console.error('Location select element not found');
        return;
    }
    
    try {
        const response = await fetch('/api/locations');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const locations = await response.json();
        console.log('Locations loaded:', locations);
        
        // Clear existing options
        locationSelect.innerHTML = '<option value="">Select a Location</option>';
        
        // Add new options
        locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        });
        
        console.log('Locations populated successfully');
    } catch (error) {
        console.error('Error loading locations:', error);
        showError('Error loading locations. Please refresh the page.');
    }
}

// Function to search businesses
async function searchBusinesses(pageToken = null) {
    console.log('\n=== SEARCH BUSINESSES ===');
    
    const category = document.getElementById('category-select').value;
    const location = document.getElementById('location-select').value;
    
    console.log('Category:', category);
    console.log('Location:', location);
    console.log('Page Token:', pageToken);
    console.log('Current Result Count:', currentResultCount);
    
    if (!category || !location) {
        showError('Please select both a category and location');
        return;
    }
    
    // Show loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
    
    // Show results section
    const resultsSection = document.getElementById('search-results-section');
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
    
    try {
        // Build search URL
        let searchUrl = `/api/search?category=${encodeURIComponent(category)}&location=${encodeURIComponent(location)}&current_count=${currentResultCount}`;
        if (pageToken) {
            searchUrl += `&page_token=${encodeURIComponent(pageToken)}`;
        }
        
        console.log('Search URL:', searchUrl);
        
        // Make API request
        const response = await fetch(searchUrl);
        const data = await response.json();
        
        console.log('Search Response:', data);
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update current count
        currentResultCount = data.current_count;
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Search Error:', error);
        showError('Error searching businesses. Please try again.');
        
        // Hide results section on error
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    } finally {
        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
    }
}

// Function to load more results
async function loadMore() {
    console.log('\n=== LOAD MORE ===');
    if (!currentPageToken) {
        console.log('No page token available');
        return;
    }
    
    console.log('Loading more results with token:', currentPageToken);
    await searchBusinesses(currentPageToken);
}

// Function to handle quote request
async function submitQuoteRequest(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submitQuoteBtn');
    const form = document.getElementById('quoteForm');
    
    // Disable submit button and show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Submitting...
    `;
    
    try {
        // Get form data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Add location
        data.location = document.getElementById('location-select').value;
        
        // Make API request
        const response = await fetch('/api/submit-quote-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Hide quote modal and show success modal
        const quoteModal = bootstrap.Modal.getInstance(document.getElementById('quoteModal'));
        const successModal = new bootstrap.Modal(document.getElementById('successModal'));
        
        quoteModal.hide();
        successModal.show();
        
        // Reset form
        form.reset();
        
    } catch (error) {
        alert('Error submitting quote request: ' + error.message);
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Submit Quote Request';
    }
}

// Function to open quote modal
function openQuoteModal(business) {
    const modal = document.getElementById('quoteModal');
    if (!modal) return;
    
    // Set hidden fields
    document.getElementById('quoteBusiness').value = business.name;
    document.getElementById('quoteBusinessAddress').value = business.address;
    document.getElementById('quoteCategory').value = business.business_type || document.getElementById('category-select').value;
    
    // Set minimum date to today
    const dateInput = document.getElementById('quoteDate');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// Function to show quote form
function showQuoteForm() {
    // Populate service dropdown with categories
    const quoteService = document.getElementById('quote-service');
    const categorySelect = document.getElementById('category-select');
    if (quoteService && categorySelect) {
        quoteService.innerHTML = categorySelect.innerHTML;
    }
    
    // Populate location dropdown
    const quoteLocation = document.getElementById('quote-location');
    const locationSelect = document.getElementById('location-select');
    if (quoteLocation && locationSelect) {
        quoteLocation.innerHTML = locationSelect.innerHTML;
    }
    
    // Show the modal
    const quoteModal = new bootstrap.Modal(document.getElementById('quoteModal'));
    quoteModal.show();
}

// Function to show professional registration form
function showProRegistrationForm() {
    // Populate services dropdown with categories
    const proServices = document.getElementById('pro-services');
    const categorySelect = document.getElementById('category-select');
    if (proServices && categorySelect) {
        proServices.innerHTML = Array.from(categorySelect.options)
            .filter(option => option.value) // Remove empty option
            .map(option => option.outerHTML)
            .join('');
    }
    
    // Populate locations dropdown
    const proLocations = document.getElementById('pro-locations');
    const locationSelect = document.getElementById('location-select');
    if (proLocations && locationSelect) {
        proLocations.innerHTML = Array.from(locationSelect.options)
            .filter(option => option.value) // Remove empty option
            .map(option => option.outerHTML)
            .join('');
    }
    
    // Show the modal
    const proModal = new bootstrap.Modal(document.getElementById('proRegistrationModal'));
    proModal.show();
}

// Event listeners for form submissions
document.addEventListener('DOMContentLoaded', function() {
    // Quote form submission
    const quoteForm = document.getElementById('quote-form');
    if (quoteForm) {
        quoteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('quote-name').value,
                email: document.getElementById('quote-email').value,
                phone: document.getElementById('quote-phone').value,
                service: document.getElementById('quote-service').value,
                location: document.getElementById('quote-location').value,
                description: document.getElementById('quote-description').value
            };
            
            try {
                const response = await fetch('/api/submit-quote', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to submit quote');
                }
                
                alert('Quote request submitted successfully! We will contact you soon.');
                bootstrap.Modal.getInstance(document.getElementById('quoteModal')).hide();
                this.reset();
            } catch (error) {
                console.error('Error submitting quote:', error);
                alert('Failed to submit quote. Please try again.');
            }
        });
    }
    
    // Professional registration form submission
    const proForm = document.getElementById('pro-registration-form');
    if (proForm) {
        proForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                businessName: document.getElementById('pro-business-name').value,
                contactName: document.getElementById('pro-contact-name').value,
                email: document.getElementById('pro-email').value,
                phone: document.getElementById('pro-phone').value,
                services: Array.from(document.getElementById('pro-services').selectedOptions).map(opt => opt.value),
                locations: Array.from(document.getElementById('pro-locations').selectedOptions).map(opt => opt.value),
                license: document.getElementById('pro-license').value,
                insurance: document.getElementById('pro-insurance').value,
                description: document.getElementById('pro-description').value
            };
            
            try {
                const response = await fetch('/api/register-professional', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to submit registration');
                }
                
                alert('Registration submitted successfully! We will review your application and contact you soon.');
                bootstrap.Modal.getInstance(document.getElementById('proRegistrationModal')).hide();
                this.reset();
            } catch (error) {
                console.error('Error submitting registration:', error);
                alert('Failed to submit registration. Please try again.');
            }
        });
    }
    
    // Load dropdowns
    loadCategories();
    loadLocations();
    
    // Set up search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Search form submitted');
            currentResultCount = 0;  // Reset count
            currentPageToken = null; // Reset page token
            searchBusinesses();
        });
    } else {
        console.error('Search form not found');
    }
    
    // Set up load more button
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMore);
    } else {
        console.error('Load more button not found');
    }
});
