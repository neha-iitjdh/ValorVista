/**
 * ValorVista - Insights Page JavaScript
 * Handles feature importance chart and market analytics
 */

document.addEventListener('DOMContentLoaded', () => {
    loadFeatureImportance();
});

/**
 * Load and display feature importance
 */
async function loadFeatureImportance() {
    const container = document.getElementById('featureImportanceChart');

    try {
        const result = await API.getFeatureImportance(15);

        if (result.success && result.feature_importance) {
            displayFeatureChart(result.feature_importance);
        } else {
            throw new Error('Failed to load feature importance');
        }
    } catch (error) {
        console.error('Feature importance error:', error);
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-exclamation-circle text-warning display-4 mb-3"></i>
                <p class="text-muted">Unable to load feature importance data.<br>
                Please ensure the model is trained and loaded.</p>
            </div>
        `;
    }
}

/**
 * Display feature importance as bar chart
 */
function displayFeatureChart(features) {
    const container = document.getElementById('featureImportanceChart');

    // Create horizontal bar chart using pure HTML/CSS
    const maxImportance = Math.max(...features.map(f => f.importance));

    const chartHTML = features.map((feature, index) => {
        const percentage = (feature.importance / maxImportance) * 100;
        const formattedImportance = (feature.importance * 100).toFixed(2);
        const delay = index * 50;

        return `
            <div class="feature-bar mb-3" style="animation-delay: ${delay}ms">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="feature-name">${formatFeatureName(feature.feature)}</span>
                    <span class="feature-value text-muted">${formattedImportance}%</span>
                </div>
                <div class="progress" style="height: 24px;">
                    <div class="progress-bar bg-primary"
                         role="progressbar"
                         style="width: ${percentage}%; transition: width 0.8s ease ${delay}ms;"
                         aria-valuenow="${percentage}"
                         aria-valuemin="0"
                         aria-valuemax="100">
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <style>
            .feature-bar {
                opacity: 0;
                animation: fadeInUp 0.5s ease forwards;
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .feature-name {
                font-weight: 500;
                color: #333;
            }
            .feature-value {
                font-size: 0.85rem;
            }
        </style>
        ${chartHTML}
    `;

    // Trigger animations after a small delay
    setTimeout(() => {
        container.querySelectorAll('.progress-bar').forEach(bar => {
            bar.style.width = bar.getAttribute('aria-valuenow') + '%';
        });
    }, 100);
}

/**
 * Format feature name for display
 */
function formatFeatureName(name) {
    const mappings = {
        'GrLivArea': 'Above Ground Living Area',
        'OverallQual': 'Overall Quality Rating',
        'TotalBsmtSF': 'Total Basement Area',
        'GarageCars': 'Garage Car Capacity',
        'YearBuilt': 'Year Built',
        'FullBath': 'Full Bathrooms',
        'TotRmsAbvGrd': 'Total Rooms Above Ground',
        'Fireplaces': 'Number of Fireplaces',
        'GarageArea': 'Garage Area',
        'YearRemodAdd': 'Year Remodeled',
        '1stFlrSF': 'First Floor Area',
        '2ndFlrSF': 'Second Floor Area',
        'LotArea': 'Lot Area',
        'BsmtFinSF1': 'Finished Basement Type 1',
        'WoodDeckSF': 'Wood Deck Area',
        'OpenPorchSF': 'Open Porch Area',
        'TotalSF': 'Total Square Footage',
        'OverallScore': 'Overall Score (Quality x Condition)',
        'HouseAge': 'House Age',
        'TotalBaths': 'Total Bathrooms',
        'GarageYrBlt': 'Garage Year Built',
        'BsmtUnfSF': 'Unfinished Basement',
        'OverallCond': 'Overall Condition',
        'MasVnrArea': 'Masonry Veneer Area',
        'LotFrontage': 'Lot Frontage',
        'BedroomAbvGr': 'Bedrooms Above Ground',
        'KitchenAbvGr': 'Kitchens Above Ground',
        'PoolArea': 'Pool Area',
        'ScreenPorch': 'Screen Porch Area',
        'EnclosedPorch': 'Enclosed Porch Area',
        'ExterQual': 'Exterior Quality',
        'BsmtQual': 'Basement Quality',
        'KitchenQual': 'Kitchen Quality',
        'GarageFinish': 'Garage Finish',
        'Neighborhood': 'Neighborhood'
    };

    return mappings[name] || name.replace(/([A-Z])/g, ' $1').trim();
}
