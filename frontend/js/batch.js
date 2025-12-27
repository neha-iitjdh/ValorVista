/**
 * ValorVista - Batch Processing JavaScript
 * Handles CSV upload and batch predictions
 */

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('csvFile');
    const browseBtn = document.getElementById('browseBtn');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const processBtn = document.getElementById('processBtn');
    const resultsSection = document.getElementById('batchResults');
    const loadingModal = new bootstrap.Modal(document.getElementById('batchLoadingModal'));

    let uploadedData = null;

    /**
     * Handle file browse click
     */
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    /**
     * Handle file selection
     */
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    /**
     * Drag and drop handlers
     */
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    /**
     * Handle file upload
     */
    function handleFile(file) {
        if (!file.name.endsWith('.csv')) {
            Utils.showToast('Please upload a CSV file', 'danger');
            return;
        }

        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const data = parseCSV(e.target.result);

                if (data.length === 0) {
                    throw new Error('No data found in CSV');
                }

                if (data.length > 100) {
                    throw new Error('Maximum 100 properties allowed per batch');
                }

                // Validate required columns
                const requiredColumns = ['GrLivArea', 'OverallQual', 'OverallCond', 'YearBuilt'];
                const missingColumns = requiredColumns.filter(col => !(col in data[0]));

                if (missingColumns.length > 0) {
                    throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
                }

                uploadedData = data;
                fileName.textContent = `${file.name} (${data.length} properties)`;
                fileInfo.classList.remove('d-none');
                processBtn.disabled = false;

                Utils.showToast(`Loaded ${data.length} properties`, 'success');

            } catch (error) {
                console.error('CSV parse error:', error);
                Utils.showToast(`Error: ${error.message}`, 'danger');
                resetUpload();
            }
        };

        reader.readAsText(file);
    }

    /**
     * Parse CSV content
     */
    function parseCSV(content) {
        const lines = content.trim().split('\n');
        if (lines.length < 2) return [];

        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            const values = parseCSVLine(lines[i]);
            if (values.length === headers.length) {
                const row = {};
                headers.forEach((header, index) => {
                    const value = values[index].trim().replace(/"/g, '');
                    const numValue = parseFloat(value);
                    row[header] = isNaN(numValue) ? value : numValue;
                });
                data.push(row);
            }
        }

        return data;
    }

    /**
     * Parse a single CSV line (handling quoted values)
     */
    function parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current);
                current = '';
            } else {
                current += char;
            }
        }

        result.push(current);
        return result;
    }

    /**
     * Remove file handler
     */
    removeFileBtn.addEventListener('click', () => {
        resetUpload();
    });

    /**
     * Reset upload state
     */
    function resetUpload() {
        fileInput.value = '';
        uploadedData = null;
        fileInfo.classList.add('d-none');
        processBtn.disabled = true;
    }

    /**
     * Process batch
     */
    processBtn.addEventListener('click', async () => {
        if (!uploadedData || uploadedData.length === 0) {
            Utils.showToast('No data to process', 'warning');
            return;
        }

        loadingModal.show();
        document.getElementById('processingStatus').textContent =
            `Analyzing ${uploadedData.length} properties...`;

        try {
            const result = await API.predictBatch(uploadedData);

            if (result.success) {
                displayBatchResults(result);
                resultsSection.classList.remove('d-none');

                setTimeout(() => {
                    resultsSection.scrollIntoView({
                        behavior: 'smooth'
                    });
                }, 300);

                Utils.showToast('Batch processing complete!', 'success');
            } else {
                throw new Error(result.error || 'Batch processing failed');
            }

        } catch (error) {
            console.error('Batch error:', error);
            Utils.showToast(`Error: ${error.message}`, 'danger');
        } finally {
            loadingModal.hide();
        }
    });

    /**
     * Display batch results
     */
    function displayBatchResults(result) {
        const { predictions, summary_statistics } = result;

        // Update summary cards with animation
        const totalEl = document.getElementById('totalCount');
        const avgEl = document.getElementById('avgPrice');
        const medianEl = document.getElementById('medianPrice');
        const totalValueEl = document.getElementById('totalValue');

        Utils.animateValue(totalEl, 0, predictions.length, 500);

        setTimeout(() => {
            avgEl.textContent = summary_statistics.formatted.mean;
        }, 200);

        setTimeout(() => {
            medianEl.textContent = summary_statistics.formatted.median;
        }, 400);

        // Calculate total portfolio value
        const totalValue = predictions.reduce((sum, p) => sum + p.prediction, 0);
        setTimeout(() => {
            totalValueEl.textContent = Utils.formatCurrency(totalValue);
        }, 600);

        // Populate results table
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = predictions.map((item, index) => {
            const input = item.input;
            const interval = item.interval || {};

            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>${Utils.formatNumber(input.GrLivArea || 0)} sq ft</td>
                    <td>${input.BedroomAbvGr || '-'}</td>
                    <td>${input.YearBuilt || '-'}</td>
                    <td>${input.OverallQual || '-'}/10</td>
                    <td class="fw-bold text-primary">${item.formatted_prediction}</td>
                    <td class="text-muted small">
                        ${interval.formatted ? `${interval.formatted.lower} - ${interval.formatted.upper}` : '-'}
                    </td>
                </tr>
            `;
        }).join('');

        // Store results for export
        window.batchResults = result;
    }

    /**
     * Export results to CSV
     */
    document.getElementById('exportResults')?.addEventListener('click', () => {
        if (!window.batchResults) {
            Utils.showToast('No results to export', 'warning');
            return;
        }

        const { predictions } = window.batchResults;

        // Create CSV content
        const headers = [
            'Index', 'Living_Area', 'Bedrooms', 'Year_Built', 'Quality',
            'Predicted_Value', 'Lower_Bound', 'Upper_Bound'
        ];

        const rows = predictions.map((item, index) => {
            const input = item.input;
            const interval = item.interval || {};
            return [
                index + 1,
                input.GrLivArea || '',
                input.BedroomAbvGr || '',
                input.YearBuilt || '',
                input.OverallQual || '',
                item.prediction.toFixed(0),
                interval.lower ? interval.lower.toFixed(0) : '',
                interval.upper ? interval.upper.toFixed(0) : ''
            ];
        });

        const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `valorvista_batch_results_${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        Utils.showToast('Results exported successfully!', 'success');
    });

    /**
     * New batch button handler
     */
    document.getElementById('newBatchBtn')?.addEventListener('click', () => {
        resultsSection.classList.add('d-none');
        resetUpload();
        window.batchResults = null;

        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    /**
     * Download template
     */
    document.getElementById('downloadTemplate')?.addEventListener('click', (e) => {
        e.preventDefault();

        const template = `GrLivArea,OverallQual,OverallCond,YearBuilt,BedroomAbvGr,FullBath,HalfBath,TotalBsmtSF,GarageCars,Neighborhood
1500,7,5,2005,3,2,1,1000,2,NAmes
2200,8,6,2010,4,2,1,1200,2,CollgCr
1800,6,5,1995,3,2,0,900,2,OldTown`;

        const blob = new Blob([template], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'valorvista_template.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        Utils.showToast('Template downloaded!', 'success');
    });
});
