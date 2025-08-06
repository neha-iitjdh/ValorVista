/**
 * ValorVista - Main JavaScript
 * Common utilities and shared functionality
 */

// API Base URL
const API_BASE = '/api/v1';

/**
 * Utility Functions
 */
const Utils = {
    /**
     * Format number as currency
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    },

    /**
     * Format number with commas
     */
    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    },

    /**
     * Show loading state on button
     */
    setButtonLoading(button, loading = true) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Processing...
            `;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText;
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
        return container;
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Animate number counting
     */
    animateValue(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const isPrice = element.textContent.includes('$');

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease out cubic
            const current = start + (end - start) * easeProgress;

            if (isPrice) {
                element.textContent = this.formatCurrency(current);
            } else {
                element.textContent = this.formatNumber(Math.round(current));
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    }
};

/**
 * API Client
 */
const API = {
    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get prediction for property
     */
    async predict(propertyData) {
        return this.request('/predict', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    /**
     * Get batch predictions
     */
    async predictBatch(properties) {
        return this.request('/predict/batch', {
            method: 'POST',
            body: JSON.stringify({ properties })
        });
    },

    /**
     * Get prediction explanation
     */
    async explain(propertyData) {
        return this.request('/explain', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    /**
     * Get feature importance
     */
    async getFeatureImportance(topN = 20) {
        return this.request(`/feature-importance?top_n=${topN}`);
    },

    /**
     * Generate report
     */
    async generateReport(propertyData) {
        return this.request('/report', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    /**
     * Health check
     */
    async healthCheck() {
        return this.request('/health');
    }
};

/**
 * Form Utilities
 */
const FormUtils = {
    /**
     * Get form data as object
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (value !== '' && value !== null) {
                // Convert numeric fields
                const numValue = parseFloat(value);
                data[key] = isNaN(numValue) ? value : numValue;
            }
        }

        return data;
    },

    /**
     * Validate required fields
     */
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value || field.value.trim() === '') {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    },

    /**
     * Reset form validation states
     */
    resetValidation(form) {
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    }
};

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add animation to elements when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .card, .insight-card').forEach(el => {
        observer.observe(el);
    });
});

// Export for use in other scripts
window.Utils = Utils;
window.API = API;
window.FormUtils = FormUtils;
