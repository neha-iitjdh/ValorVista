/**
 * ValorVista - Main JavaScript (Frontend Version)
 * Common utilities and shared functionality
 */

// Get API URL from config
const API_BASE = window.CONFIG?.API_BASE_URL || 'http://localhost:5000/api/v1';

/**
 * Utility Functions
 */
const Utils = {
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    },

    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    },

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

    animateValue(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const isPrice = element.textContent.includes('$');

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3);
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
 * API Client - Calls Render backend
 */
const API = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            },
            mode: 'cors'
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

    async predict(propertyData) {
        return this.request('/predict', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    async predictBatch(properties) {
        return this.request('/predict/batch', {
            method: 'POST',
            body: JSON.stringify({ properties })
        });
    },

    async explain(propertyData) {
        return this.request('/explain', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    async getFeatureImportance(topN = 20) {
        return this.request(`/feature-importance?top_n=${topN}`);
    },

    async generateReport(propertyData) {
        return this.request('/report', {
            method: 'POST',
            body: JSON.stringify(propertyData)
        });
    },

    async healthCheck() {
        return this.request('/health');
    }
};

/**
 * Form Utilities
 */
const FormUtils = {
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (value !== '' && value !== null) {
                const numValue = parseFloat(value);
                data[key] = isNaN(numValue) ? value : numValue;
            }
        }

        return data;
    },

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

    resetValidation(form) {
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    }
};

// Export for use in other scripts
window.Utils = Utils;
window.API = API;
window.FormUtils = FormUtils;
