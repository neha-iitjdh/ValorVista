/**
 * ValorVista - Valuation Page JavaScript
 * Handles property valuation form and results
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('valuationForm');
    const submitBtn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

    let currentPrediction = null;
    let currentPropertyData = null;

    /**
     * Handle form submission
     */
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate form
        if (!FormUtils.validateForm(form)) {
            Utils.showToast('Please fill in all required fields', 'danger');
            return;
        }

        // Get form data
        const propertyData = FormUtils.getFormData(form);
        currentPropertyData = propertyData;

        // Show loading
        loadingModal.show();

        try {
            // Make API request
            const result = await API.predict(propertyData);

            if (result.success) {
                currentPrediction = result;
                displayResults(result, propertyData);

                // Hide form section animation
                document.getElementById('valuation-form').scrollIntoView({
                    behavior: 'smooth'
                });

                setTimeout(() => {
                    resultsSection.classList.remove('d-none');
                    resultsSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }, 300);

            } else {
                throw new Error(result.error || 'Prediction failed');
            }

        } catch (error) {
            console.error('Prediction error:', error);
            Utils.showToast(`Error: ${error.message}`, 'danger');
        } finally {
            loadingModal.hide();
        }
    });

    /**
     * Display prediction results
     */
    function displayResults(result, propertyData) {
        // Main prediction value with animation
        const predictionEl = document.getElementById('predictionValue');
        const prediction = result.prediction;
        Utils.animateValue(predictionEl, 0, prediction, 1500);

        // Confidence interval
        const intervalEl = document.getElementById('confidenceInterval');
        if (result.confidence_interval && result.confidence_interval.formatted) {
            intervalEl.textContent = `95% Confidence: ${result.confidence_interval.formatted.lower} - ${result.confidence_interval.formatted.upper}`;
        }

        // Property summary
        displayPropertySummary(propertyData, result.input_summary);

        // Get and display key factors
        displayKeyFactors(propertyData);
    }

    /**
     * Display property summary
     */
    function displayPropertySummary(propertyData, summary) {
        const container = document.getElementById('propertySummary');

        const summaryItems = [
            { icon: 'bi-rulers', label: 'Living Area', value: `${Utils.formatNumber(propertyData.GrLivArea || 0)} sq ft` },
            { icon: 'bi-door-open', label: 'Bedrooms', value: propertyData.BedroomAbvGr || 3 },
            { icon: 'bi-droplet', label: 'Bathrooms', value: summary?.bathrooms || (propertyData.FullBath || 0) + 0.5 * (propertyData.HalfBath || 0) },
            { icon: 'bi-calendar', label: 'Year Built', value: propertyData.YearBuilt },
            { icon: 'bi-star', label: 'Quality', value: `${propertyData.OverallQual}/10` },
            { icon: 'bi-speedometer2', label: 'Condition', value: `${propertyData.OverallCond}/10` }
        ];

        container.innerHTML = summaryItems.map(item => `
            <div class="d-flex align-items-center mb-3">
                <div class="me-3">
                    <i class="${item.icon} text-primary fs-5"></i>
                </div>
                <div>
                    <small class="text-muted d-block">${item.label}</small>
                    <strong>${item.value}</strong>
                </div>
            </div>
        `).join('');
    }

    /**
     * Display key value factors
     */
    async function displayKeyFactors(propertyData) {
        const container = document.getElementById('keyFactors');

        try {
            const explanation = await API.explain(propertyData);

            if (explanation.success && explanation.key_factors) {
                const factors = explanation.key_factors.slice(0, 6);

                container.innerHTML = factors.map(factor => {
                    const percentage = (factor.importance * 100).toFixed(1);
                    return `
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="small">${formatFeatureName(factor.feature)}</span>
                                <span class="small text-muted">${percentage}%</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar bg-primary" style="width: ${percentage * 5}%"></div>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error('Error getting explanation:', error);
            container.innerHTML = '<p class="text-muted">Unable to load key factors</p>';
        }
    }

    /**
     * Format feature name for display
     */
    function formatFeatureName(name) {
        const mappings = {
            'GrLivArea': 'Living Area',
            'OverallQual': 'Overall Quality',
            'TotalBsmtSF': 'Basement Area',
            'GarageCars': 'Garage Capacity',
            'YearBuilt': 'Year Built',
            'FullBath': 'Full Bathrooms',
            'TotRmsAbvGrd': 'Total Rooms',
            'Fireplaces': 'Fireplaces',
            'GarageArea': 'Garage Area',
            'YearRemodAdd': 'Remodel Year',
            '1stFlrSF': 'First Floor',
            '2ndFlrSF': 'Second Floor',
            'LotArea': 'Lot Area',
            'BsmtFinSF1': 'Finished Basement',
            'WoodDeckSF': 'Wood Deck',
            'OpenPorchSF': 'Open Porch',
            'TotalSF': 'Total Sq Ft',
            'OverallScore': 'Overall Score',
            'HouseAge': 'House Age'
        };

        return mappings[name] || name.replace(/([A-Z])/g, ' $1').trim();
    }

    /**
     * Download report button handler
     */
    document.getElementById('downloadReportBtn')?.addEventListener('click', async () => {
        if (!currentPropertyData) {
            Utils.showToast('No property data available', 'warning');
            return;
        }

        const btn = document.getElementById('downloadReportBtn');
        Utils.setButtonLoading(btn, true);

        try {
            const result = await API.generateReport(currentPropertyData);

            if (result.success && result.download_url) {
                // Trigger download
                window.open(result.download_url, '_blank');
                Utils.showToast('Report generated successfully!', 'success');
            } else {
                throw new Error(result.error || 'Report generation failed');
            }
        } catch (error) {
            console.error('Report error:', error);
            Utils.showToast(`Error: ${error.message}`, 'danger');
        } finally {
            Utils.setButtonLoading(btn, false);
        }
    });

    /**
     * New valuation button handler
     */
    document.getElementById('newValuationBtn')?.addEventListener('click', () => {
        resultsSection.classList.add('d-none');
        form.reset();
        FormUtils.resetValidation(form);
        currentPrediction = null;
        currentPropertyData = null;

        document.getElementById('valuation-form').scrollIntoView({
            behavior: 'smooth'
        });
    });

    /**
     * Auto-calculate related fields
     */
    const livingAreaInput = document.getElementById('GrLivArea');
    const firstFloorInput = document.getElementById('1stFlrSF');

    livingAreaInput?.addEventListener('change', () => {
        if (!firstFloorInput.value && livingAreaInput.value) {
            firstFloorInput.value = livingAreaInput.value;
        }
    });

    /**
     * Set default values for year fields
     */
    const currentYear = new Date().getFullYear();
    document.querySelectorAll('input[type="number"]').forEach(input => {
        if (input.name === 'YearBuilt' && !input.value) {
            input.placeholder = `e.g., ${currentYear - 20}`;
        }
    });
});
