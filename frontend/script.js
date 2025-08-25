// API Configuration
const API_BASE_URL = window.location.origin + '/api'; // Dynamically get the base URL

// State Management
let currentFile = null;
let analysisResults = null;
let chartInstance = null;

// Pagination state
let currentPage = 1;
let resultsPerPage = 10;
let filteredResults = [];

// DOM Elements
const elements = {
    // Tabs
    tabButtons: document.querySelectorAll('.tab-button'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Text Input
    textInput: document.getElementById('text-input'),
    analyzeTextBtn: document.getElementById('analyze-text-btn'),
    enhancedAnalyzeBtn: document.getElementById('enhanced-analyze-btn'),
    charCount: document.querySelector('.char-count'),
    detectedLanguage: document.querySelector('.detected-language'),
    
    // File Upload
    fileInput: document.getElementById('file-input'),
    uploadArea: document.getElementById('upload-area'),
    browseBtn: document.getElementById('browse-btn'),
    fileInfo: document.getElementById('file-info'),
    fileName: document.querySelector('.file-name'),
    fileSize: document.querySelector('.file-size'),
    removeFileBtn: document.getElementById('remove-file'),
    analyzeFileBtn: document.getElementById('analyze-file-btn'),
    
    // Loading
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingMessage: document.getElementById('loading-message'),
    progressFill: document.getElementById('progress-fill'),
    
    // Results
    resultsSection: document.getElementById('results-section'),
    positivePercent: document.getElementById('positive-percent'),
    positiveCount: document.getElementById('positive-count'),
    neutralPercent: document.getElementById('neutral-percent'),
    neutralCount: document.getElementById('neutral-count'),
    negativePercent: document.getElementById('negative-percent'),
    negativeCount: document.getElementById('negative-count'),
    resultsTable: document.getElementById('results-table'),
    
    // Chart
    sentimentChart: document.getElementById('sentiment-chart'),
    
    // Filters
    filterBtn: document.getElementById('filter-btn'),
    filterOptions: document.getElementById('filter-options'),
    exportBtn: document.getElementById('export-btn'),
    
    // AI Insights
    aiInsights: document.getElementById('ai-insights'),
    insightsContent: document.getElementById('insights-content'),
    exportInsightsBtn: document.getElementById('export-insights-btn'),
    
    // Navigation
    resultsNavigation: document.getElementById('results-navigation'),
    currentRange: document.getElementById('current-range'),
    totalResults: document.getElementById('total-results'),
    currentPageNum: document.getElementById('current-page-num'),
    totalPages: document.getElementById('total-pages'),
    prevPageBtn: document.getElementById('prev-page-btn'),
    nextPageBtn: document.getElementById('next-page-btn'),
    
    // Error
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text'),
    closeError: document.getElementById('close-error')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeTextInput();
    initializeFileUpload();
    initializeFilters();
    initializeNavigation();
    initializeExport();
    initializeInsightsExport();
    initializeErrorHandling();
    testAPIConnectivity(); // Test API on load
});

// Tab Functionality
function initializeTabs() {
    elements.tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    elements.tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update content
    elements.tabContents.forEach(content => {
        const isActive = content.id === `${tabName}-tab`;
        content.classList.toggle('active', isActive);
    });
}

// Text Input Functionality
function initializeTextInput() {
    // Character counter
    elements.textInput.addEventListener('input', () => {
        const length = elements.textInput.value.length;
        elements.charCount.textContent = `${length} / 5000 characters`;
        
        // Enable/disable analyze button
        elements.analyzeTextBtn.disabled = length === 0 || length > 5000;
        
        // Detect language (simulated - in production, this would call an API)
        if (length > 20) {
            detectLanguagePreview(elements.textInput.value);
        }
    });
    
    // Analyze button
    elements.analyzeTextBtn.addEventListener('click', () => {
        const text = elements.textInput.value.trim();
        if (text) {
            analyzeText(text);
        }
    });
    
    // Enhanced analyze button
    elements.enhancedAnalyzeBtn.addEventListener('click', () => {
        const text = elements.textInput.value.trim();
        if (text) {
            analyzeTextEnhanced(text);
        }
    });
}

// Language Detection Preview (real API call)
async function detectLanguagePreview(text) {
    if (text.length < 10) {
        elements.detectedLanguage.textContent = 'Language: Auto-detect';
        return;
    }
    
    try {
        // Call the actual language detection API
        const response = await fetch(`${API_BASE_URL}/detect-language`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text.substring(0, 200) }) // Only send first 200 chars for preview
        });
        
        if (response.ok) {
            const data = await response.json();
            const confidence = Math.round(data.confidence * 100);
            elements.detectedLanguage.textContent = `Language: ${data.language} (${confidence}% confidence)`;
        } else {
            // Fallback to basic detection
            const detectedLang = detectLanguageBasic(text);
            elements.detectedLanguage.textContent = `Language: ${detectedLang} (estimated)`;
        }
    } catch (error) {
        // Fallback to basic detection
        const detectedLang = detectLanguageBasic(text);
        elements.detectedLanguage.textContent = `Language: ${detectedLang} (estimated)`;
    }
}

function detectLanguageBasic(text) {
    // Basic heuristic detection as fallback
    const cleanText = text.toLowerCase();
    
    // Check for common English patterns
    const englishWords = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on', 'are'];
    const englishCount = englishWords.filter(word => cleanText.includes(` ${word} `) || cleanText.startsWith(`${word} `) || cleanText.endsWith(` ${word}`)).length;
    
    if (englishCount >= 2) {
        return 'English';
    }
    
    // Check for other language patterns
    if (/[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]/.test(cleanText)) {
        return 'French/Spanish';
    }
    if (/[äöüß]/.test(cleanText)) {
        return 'German';
    }
    if (/[а-я]/.test(cleanText)) {
        return 'Russian';
    }
    if (/[一-龯]/.test(cleanText)) {
        return 'Chinese';
    }
    if (/[あ-ん]/.test(cleanText)) {
        return 'Japanese';
    }
    if (/[ا-ي]/.test(cleanText)) {
        return 'Arabic';
    }
    if (/[अ-ह]/.test(cleanText)) {
        return 'Hindi';
    }
    
    return 'English'; // Default to English
}

// File Upload Functionality
function initializeFileUpload() {
    // Browse button
    elements.browseBtn.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    // File input change
    elements.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });
    
    // Drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('dragover');
    });
    
    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });
    
    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });
    
    // Remove file button
    elements.removeFileBtn.addEventListener('click', () => {
        removeFile();
    });
    
    // Analyze file button
    elements.analyzeFileBtn.addEventListener('click', () => {
        if (currentFile) {
            analyzeFile(currentFile);
        }
    });
}

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['application/json', 'text/csv'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const validExtensions = ['json', 'csv'];
    
    if (!validExtensions.includes(fileExtension)) {
        showError('Invalid file type. Please upload a JSON or CSV file.');
        return;
    }
    
    // Validate file size (2MB max)
    const maxSize = 2 * 1024 * 1024; // 2MB in bytes
    if (file.size > maxSize) {
        showError('File size exceeds 2MB. Please upload a smaller file.');
        return;
    }
    
    // Store file reference
    currentFile = file;
    
    // Display file info
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    elements.fileInfo.style.display = 'block';
    elements.uploadArea.style.display = 'none';
    elements.analyzeFileBtn.disabled = false;
}

function removeFile() {
    currentFile = null;
    elements.fileInput.value = '';
    elements.fileInfo.style.display = 'none';
    elements.uploadArea.style.display = 'block';
    elements.analyzeFileBtn.disabled = true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Analysis Functions
async function analyzeTextEnhanced(text) {
    showLoading('Performing enhanced analysis...');
    
    try {
        // Simulate progress updates
        updateProgress(20, 'Detecting language and style...');
        await sleep(500);
        
        updateProgress(40, 'Analyzing emotions and themes...');
        await sleep(500);
        
        updateProgress(60, 'Processing customer intent...');
        await sleep(500);
        
        updateProgress(80, 'Generating comprehensive insights...');
        await sleep(500);
        
        // Make API call to enhanced analysis endpoint
        const response = await fetch(`${API_BASE_URL}/analyze/enhanced`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error('Enhanced analysis failed');
        }
        
        const data = await response.json();
        updateProgress(100, 'Complete!');
        await sleep(300);
        
        displayEnhancedResults(data);
    } catch (error) {
        console.error('Enhanced analysis error:', error);
        
        // Fallback to regular analysis if enhanced fails
        showError('Enhanced analysis unavailable. Falling back to standard sentiment analysis.');
        await sleep(1000);
        analyzeText(text);
    } finally {
        hideLoading();
    }
}

async function analyzeText(text) {
    showLoading('Analyzing text...');
    
    try {
        // Simulate progress updates
        updateProgress(20, 'Detecting language...');
        await sleep(500);
        
        updateProgress(40, 'Translating text...');
        await sleep(500);
        
        updateProgress(60, 'Performing sentiment analysis...');
        await sleep(500);
        
        updateProgress(80, 'Generating insights...');
        await sleep(500);
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        updateProgress(100, 'Complete!');
        await sleep(300);
        
        displayResults(data);
    } catch (error) {
        console.error('Analysis error:', error);
        
        // Check if it's a network error or API error
        if (error.message.includes('failed to fetch') || error.message.includes('NetworkError')) {
            showError('Unable to connect to the server. Please check your connection and try again.');
        } else {
            showError(`Analysis failed: ${error.message}. Please try again or contact support.`);
        }
        
        // For development: still show mock data
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('Development mode: Using mock data');
            const mockData = generateMockResults(text);
            displayResults(mockData);
        }
    } finally {
        hideLoading();
    }
}

async function analyzeFile(file) {
    showLoading('Processing file...');
    
    try {
        // Read file content
        updateProgress(10, 'Reading file...');
        const content = await readFileContent(file);
        
        updateProgress(30, 'Parsing data...');
        await sleep(500);
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        
        updateProgress(50, 'Analyzing content...');
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/upload/file/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('File analysis failed');
        }
        
        const data = await response.json();
        updateProgress(100, 'Complete!');
        await sleep(300);
        
        displayResults(data);
    } catch (error) {
        console.error('File analysis error:', error);
        
        // Check if it's a network error or API error
        if (error.message.includes('failed to fetch') || error.message.includes('NetworkError')) {
            showError('Unable to connect to the server. Please check your connection and try again.');
        } else {
            showError(`File analysis failed: ${error.message}. Please try again or contact support.`);
        }
        
        // For development: still show mock data
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('Development mode: Using mock file data');
            const mockData = generateMockFileResults();
            displayResults(mockData);
        }
    } finally {
        hideLoading();
    }
}

function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
    });
}

// Enhanced Results Display
function displayEnhancedResults(data) {
    // Show results section
    elements.resultsSection.style.display = 'block';
    
    // Clear existing content
    elements.resultsTable.innerHTML = '';
    
    // Create enhanced analysis display
    const enhanced = data.enhanced_analysis || {};
    
    let html = `
        <div class="enhanced-analysis-container">
            <div class="enhanced-header">
                <h3><i class="fas fa-brain"></i> Enhanced Analysis Results</h3>
                <span class="model-badge">GPT OSS-120B</span>
            </div>
            
            <div class="enhanced-grid">
                <div class="analysis-card sentiment-card">
                    <div class="card-header">
                        <i class="fas fa-heart"></i>
                        <h4>Sentiment & Emotion</h4>
                    </div>
                    <div class="card-content">
                        <div class="metric">
                            <span class="label">Sentiment:</span>
                            <span class="value sentiment-${enhanced.sentiment || 'neutral'}">${(enhanced.sentiment || 'neutral').toUpperCase()}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Confidence:</span>
                            <span class="value">${Math.round((enhanced.confidence || 0.7) * 100)}%</span>
                        </div>
                        <div class="metric">
                            <span class="label">Emotion:</span>
                            <span class="value emotion-badge">${enhanced.emotion || 'unknown'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-card style-card">
                    <div class="card-header">
                        <i class="fas fa-pen-fancy"></i>
                        <h4>Language & Style</h4>
                    </div>
                    <div class="card-content">
                        <div class="metric">
                            <span class="label">Language:</span>
                            <span class="value">${data.language || 'Unknown'}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Style:</span>
                            <span class="value">${enhanced.language_style || 'unknown'}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Urgency:</span>
                            <span class="value urgency-${enhanced.urgency_level || 'medium'}">${enhanced.urgency_level || 'medium'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-card themes-card">
                    <div class="card-header">
                        <i class="fas fa-tags"></i>
                        <h4>Themes & Intent</h4>
                    </div>
                    <div class="card-content">
                        <div class="metric">
                            <span class="label">Key Themes:</span>
                            <div class="themes-list">
                                ${(enhanced.key_themes || ['general']).map(theme => 
                                    `<span class="theme-tag">${theme}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <div class="metric">
                            <span class="label">Customer Intent:</span>
                            <span class="value intent-badge">${enhanced.customer_intent || 'unknown'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-card text-card">
                    <div class="card-header">
                        <i class="fas fa-quote-left"></i>
                        <h4>Original Text</h4>
                    </div>
                    <div class="card-content">
                        <p class="analyzed-text">${escapeHtml(data.text)}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    elements.resultsTable.innerHTML = html;
    
    // Hide chart and summary cards for enhanced analysis
    document.querySelector('.summary-cards').style.display = 'none';
    document.querySelector('.chart-container').style.display = 'none';
    
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Results Display
function displayResults(data) {
    analysisResults = data;
    
    // Show results section
    elements.resultsSection.style.display = 'block';
    
    // Show chart and summary cards for regular analysis
    document.querySelector('.summary-cards').style.display = 'grid';
    document.querySelector('.chart-container').style.display = 'block';
    
    // Update summary cards
    updateSummaryCards(data.summary);
    
    // Create chart
    createSentimentChart(data.summary);
    
    // Display detailed results
    displayDetailedResults(data.results);
    
    // Display AI insights if available
    if (data.insights) {
        displayInsights(data.insights);
    }
    
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function updateSummaryCards(summary) {
    const total = summary.positive + summary.neutral + summary.negative;
    
    // Positive
    const posPercent = total > 0 ? Math.round((summary.positive / total) * 100) : 0;
    elements.positivePercent.textContent = `${posPercent}%`;
    elements.positiveCount.textContent = `${summary.positive} ${summary.positive === 1 ? 'review' : 'reviews'}`;
    
    // Neutral
    const neuPercent = total > 0 ? Math.round((summary.neutral / total) * 100) : 0;
    elements.neutralPercent.textContent = `${neuPercent}%`;
    elements.neutralCount.textContent = `${summary.neutral} ${summary.neutral === 1 ? 'review' : 'reviews'}`;
    
    // Negative
    const negPercent = total > 0 ? Math.round((summary.negative / total) * 100) : 0;
    elements.negativePercent.textContent = `${negPercent}%`;
    elements.negativeCount.textContent = `${summary.negative} ${summary.negative === 1 ? 'review' : 'reviews'}`;
}

function createSentimentChart(summary) {
    const ctx = elements.sentimentChart.getContext('2d');
    
    // Destroy existing chart if any
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    // Create new chart with interactive features
    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [summary.positive, summary.neutral, summary.negative],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2,
                hoverBackgroundColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14,
                            weight: '500'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        generateLabels: function(chart) {
                            const data = chart.data;
                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                            
                            return data.labels.map((label, index) => {
                                const value = data.datasets[0].data[index];
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                
                                return {
                                    text: `${label}: ${value} (${percentage}%)`,
                                    fillStyle: data.datasets[0].backgroundColor[index],
                                    strokeStyle: data.datasets[0].borderColor[index],
                                    lineWidth: 2,
                                    hidden: false,
                                    index: index
                                };
                            });
                        }
                    },
                    onClick: function(event, legendItem, legend) {
                        // Toggle dataset visibility and apply filter
                        const chart = legend.chart;
                        const index = legendItem.index;
                        const meta = chart.getDatasetMeta(0);
                        
                        // Toggle visibility
                        meta.data[index].hidden = !meta.data[index].hidden;
                        chart.update();
                        
                        // Apply filter to detailed results
                        const sentimentTypes = ['positive', 'neutral', 'negative'];
                        const sentimentType = sentimentTypes[index];
                        toggleSentimentFilter(sentimentType);
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} reviews (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            }
        }
    });
}

function displayDetailedResults(results) {
    // Initialize pagination state
    filteredResults = [...results]; // Copy all results initially
    currentPage = 1; // Reset to first page
    
    // Initialize pagination
    updateNavigationState();
    displayCurrentPage();
    
    // Update total count
    updateResultsCount(results.length);
}

function updateResultsCount(total) {
    const resultsCountElement = document.getElementById('results-count');
    if (resultsCountElement) {
        resultsCountElement.textContent = `${total} ${total === 1 ? 'review' : 'reviews'}`;
    }
}

function displayInsights(insights) {
    elements.aiInsights.style.display = 'block';
    
    let html = '<div class="insights-list">';
    insights.forEach(insight => {
        html += `<div class="insight-item">${renderMarkdown(insight)}</div>`;
    });
    html += '</div>';
    
    elements.insightsContent.innerHTML = html;
}

// Filter Functionality
function initializeFilters() {
    elements.filterBtn.addEventListener('click', () => {
        const isVisible = elements.filterOptions.style.display === 'flex';
        elements.filterOptions.style.display = isVisible ? 'none' : 'flex';
    });
    
    // Add event listeners to filter checkboxes
    const filterCheckboxes = elements.filterOptions.querySelectorAll('input[type="checkbox"]');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

function applyFilters() {
    const activeFilters = [];
    const filterCheckboxes = elements.filterOptions.querySelectorAll('input[type="checkbox"]:checked');
    
    filterCheckboxes.forEach(checkbox => {
        activeFilters.push(checkbox.value);
    });
    
    // Filter the original results based on active filters
    if (analysisResults && analysisResults.results) {
        filteredResults = analysisResults.results.filter(result => {
            const sentiment = result.sentiment.toLowerCase();
            return activeFilters.includes(sentiment);
        });
        
        // Reset to page 1 when filters change
        currentPage = 1;
        
        // Update pagination and display
        updateNavigationState();
        displayCurrentPage();
        
        // Update results count with filtered information
        const totalCount = analysisResults.results.length;
        const visibleCount = filteredResults.length;
        const resultsCountElement = document.getElementById('results-count');
        if (resultsCountElement) {
            if (visibleCount === totalCount) {
                resultsCountElement.textContent = `${totalCount} ${totalCount === 1 ? 'review' : 'reviews'}`;
            } else {
                resultsCountElement.textContent = `${visibleCount} of ${totalCount} ${totalCount === 1 ? 'review' : 'reviews'}`;
            }
        }
    }
}

function toggleSentimentFilter(sentimentType) {
    // Find the corresponding checkbox and toggle it
    const checkbox = elements.filterOptions.querySelector(`input[value="${sentimentType}"]`);
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        applyFilters();
        
        // Update filter button to show active state
        const activeCount = elements.filterOptions.querySelectorAll('input[type="checkbox"]:checked').length;
        const totalCount = elements.filterOptions.querySelectorAll('input[type="checkbox"]').length;
        
        if (activeCount < totalCount) {
            elements.filterBtn.classList.add('filter-active');
            elements.filterBtn.innerHTML = `<i class="fas fa-filter"></i> Filter (${activeCount}/${totalCount})`;
        } else {
            elements.filterBtn.classList.remove('filter-active');
            elements.filterBtn.innerHTML = `<i class="fas fa-filter"></i> Filter`;
        }
    }
}

// Navigation Functionality
function initializeNavigation() {
    if (elements.prevPageBtn) {
        elements.prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                displayCurrentPage();
            }
        });
    }
    
    if (elements.nextPageBtn) {
        elements.nextPageBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredResults.length / resultsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                displayCurrentPage();
            }
        });
    }
}

function updateNavigationState() {
    if (!elements.resultsNavigation || !filteredResults.length) {
        if (elements.resultsNavigation) {
            elements.resultsNavigation.style.display = 'none';
        }
        return;
    }
    
    const totalResults = filteredResults.length;
    const totalPages = Math.ceil(totalResults / resultsPerPage);
    
    // Show navigation only if there are more results than fit on one page
    if (totalResults > resultsPerPage) {
        elements.resultsNavigation.style.display = 'flex';
        
        // Update info
        const startRange = (currentPage - 1) * resultsPerPage + 1;
        const endRange = Math.min(currentPage * resultsPerPage, totalResults);
        
        elements.currentRange.textContent = `${startRange}-${endRange}`;
        elements.totalResults.textContent = totalResults;
        elements.currentPageNum.textContent = currentPage;
        elements.totalPages.textContent = totalPages;
        
        // Update button states
        elements.prevPageBtn.disabled = currentPage === 1;
        elements.nextPageBtn.disabled = currentPage === totalPages;
    } else {
        elements.resultsNavigation.style.display = 'none';
    }
}

function displayCurrentPage() {
    if (!filteredResults.length) return;
    
    const startIndex = (currentPage - 1) * resultsPerPage;
    const endIndex = Math.min(startIndex + resultsPerPage, filteredResults.length);
    const pageResults = filteredResults.slice(startIndex, endIndex);
    
    // Display only the current page results
    displayPageResults(pageResults, startIndex);
    updateNavigationState();
}

function displayPageResults(results, startIndex = 0) {
    let html = '';
    
    results.forEach((result, index) => {
        const actualIndex = startIndex + index;
        const sentimentClass = result.sentiment.toLowerCase();
        const translationInfo = result.translation_info || {};
        const wasTranslated = result.was_translated || translationInfo.was_translated;
        
        html += `
            <div class="result-item" data-sentiment="${sentimentClass}">
                <div class="result-header-row">
                    <span class="result-id">#${actualIndex + 1}</span>
                    <span class="sentiment-badge ${sentimentClass}">${result.sentiment}</span>
                    ${wasTranslated ? '<span class="translation-badge"><i class="fas fa-language"></i> Translated</span>' : ''}
                </div>
                
                ${wasTranslated ? `
                    <div class="translation-section">
                        <p class="result-text original">
                            <strong>Original (${result.language}):</strong><br>
                            ${escapeHtml(result.original_text || result.text)}
                        </p>
                        <p class="result-text translated">
                            <strong>English Translation:</strong><br>
                            ${escapeHtml(result.translated_text || result.text)}
                        </p>
                    </div>
                ` : `
                    <p class="result-text">${escapeHtml(result.text)}</p>
                `}
                
                <div class="result-meta">
                    <span><i class="fas fa-globe"></i> ${result.language || 'Unknown'}</span>
                    <span><i class="fas fa-chart-bar"></i> Confidence: ${Math.round(result.confidence * 100)}%</span>
                    ${wasTranslated ? `<span><i class="fas fa-exchange-alt"></i> ${translationInfo.source_language || result.language} → ${translationInfo.target_language || 'en'}</span>` : ''}
                </div>
            </div>
        `;
    });
    
    elements.resultsTable.innerHTML = html;
}

// Export Functionality
function initializeExport() {
    elements.exportBtn.addEventListener('click', exportResults);
}

function exportResults() {
    if (!analysisResults) {
        showError('No results to export');
        return;
    }
    
    // Create CSV content
    let csv = 'Index,Text,Sentiment,Language,Confidence\n';
    
    analysisResults.results.forEach((result, index) => {
        csv += `${index + 1},"${result.text.replace(/"/g, '""')}",${result.sentiment},${result.language || 'Unknown'},${Math.round(result.confidence * 100)}%\n`;
    });
    
    // Create download link
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentiment_analysis_${new Date().getTime()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// AI Insights Export Functionality
function initializeInsightsExport() {
    if (elements.exportInsightsBtn) {
        elements.exportInsightsBtn.addEventListener('click', exportInsights);
    }
}

function exportInsights() {
    if (!analysisResults || !analysisResults.insights) {
        showError('No AI insights to export');
        return;
    }
    
    // Create markdown content
    let markdown = `# AI-Generated Insights\n\n`;
    markdown += `**Analysis Date:** ${new Date().toLocaleString()}\n\n`;
    
    if (analysisResults.summary) {
        const summary = analysisResults.summary;
        const total = summary.positive + summary.neutral + summary.negative;
        
        markdown += `## Summary Statistics\n\n`;
        markdown += `- **Total Reviews Analyzed:** ${total}\n`;
        markdown += `- **Positive:** ${summary.positive} (${Math.round((summary.positive / total) * 100)}%)\n`;
        markdown += `- **Neutral:** ${summary.neutral} (${Math.round((summary.neutral / total) * 100)}%)\n`;
        markdown += `- **Negative:** ${summary.negative} (${Math.round((summary.negative / total) * 100)}%)\n\n`;
    }
    
    markdown += `## Key Insights\n\n`;
    
    // Convert HTML insights back to clean markdown
    analysisResults.insights.forEach((insight, index) => {
        // Remove HTML tags and convert to clean text
        const cleanInsight = insight
            .replace(/<br\s*\/?>/gi, '\n')
            .replace(/<strong>(.*?)<\/strong>/gi, '**$1**')
            .replace(/<em>(.*?)<\/em>/gi, '*$1*')
            .replace(/<div class="insight-bullet">(.*?)<\/div>/gi, '$1')
            .replace(/<[^>]*>/g, '') // Remove any remaining HTML tags
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .trim();
        
        if (cleanInsight) {
            markdown += `${index + 1}. ${cleanInsight}\n\n`;
        }
    });
    
    markdown += `---\n\n`;
    markdown += `*Generated by Multilingual Sentiment Analysis Pipeline*\n`;
    markdown += `*Powered by Ollama GPT OSS-120B*\n`;
    
    // Create download link
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_insights_${new Date().getTime()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Loading State
function showLoading(message) {
    elements.loadingMessage.textContent = message;
    elements.progressFill.style.width = '0%';
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function updateProgress(percent, message) {
    elements.progressFill.style.width = `${percent}%`;
    if (message) {
        elements.loadingMessage.textContent = message;
    }
}

// Error Handling
function initializeErrorHandling() {
    elements.closeError.addEventListener('click', () => {
        elements.errorMessage.style.display = 'none';
    });
}

function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        elements.errorMessage.style.display = 'none';
    }, 5000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    // Simple markdown renderer for insights
    if (!text) return '';
    
    // Escape HTML first but keep markdown syntax
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    
    // Convert markdown to HTML
    html = html
        // Bold text: **text** -> <strong>text</strong>
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // Italic text: *text* -> <em>text</em>
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        // Bullet points: • text -> proper bullet
        .replace(/^•\s*(.+)$/gm, '<div class="insight-bullet">• $1</div>')
        // Dash bullet points: - text -> proper bullet
        .replace(/^-\s*(.+)$/gm, '<div class="insight-bullet">• $1</div>')
        // Line breaks
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    
    return html;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Mock Data Generation (for demonstration)
function generateMockResults(text) {
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    const sentiments = ['Positive', 'Neutral', 'Negative'];
    const languages = ['English', 'Spanish', 'French', 'German'];
    
    const results = sentences.slice(0, 10).map((sentence, index) => ({
        text: sentence.trim(),
        sentiment: sentiments[Math.floor(Math.random() * sentiments.length)],
        confidence: 0.7 + Math.random() * 0.3,
        language: languages[Math.floor(Math.random() * languages.length)]
    }));
    
    const summary = {
        positive: results.filter(r => r.sentiment === 'Positive').length,
        neutral: results.filter(r => r.sentiment === 'Neutral').length,
        negative: results.filter(r => r.sentiment === 'Negative').length
    };
    
    const insights = [
        'The overall sentiment is predominantly positive with strong confidence scores.',
        'Multiple languages detected in the input, showing diverse perspectives.',
        'Consider focusing on addressing the negative feedback points for improvement.',
        'The neutral responses suggest areas where more clarity might be beneficial.'
    ];
    
    return { results, summary, insights };
}

function generateMockFileResults() {
    const count = 20 + Math.floor(Math.random() * 30);
    const sentiments = ['Positive', 'Neutral', 'Negative'];
    const languages = ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese'];
    const sampleTexts = [
        'This product exceeded my expectations!',
        'The service was okay, nothing special.',
        'Terrible experience, would not recommend.',
        'Great quality and fast shipping.',
        'Average product, decent price.',
        'Absolutely love it! Will buy again.',
        'Not worth the money.',
        'Good customer support.',
        'Could be better.',
        'Outstanding performance!'
    ];
    
    const results = Array.from({ length: count }, (_, index) => ({
        text: sampleTexts[Math.floor(Math.random() * sampleTexts.length)],
        sentiment: sentiments[Math.floor(Math.random() * sentiments.length)],
        confidence: 0.6 + Math.random() * 0.4,
        language: languages[Math.floor(Math.random() * languages.length)]
    }));
    
    const summary = {
        positive: results.filter(r => r.sentiment === 'Positive').length,
        neutral: results.filter(r => r.sentiment === 'Neutral').length,
        negative: results.filter(r => r.sentiment === 'Negative').length
    };
    
    const insights = [
        `Analyzed ${count} reviews across ${languages.length} different languages.`,
        `The sentiment distribution shows ${Math.round((summary.positive / count) * 100)}% positive feedback.`,
        'Customer satisfaction appears to be generally high with room for improvement.',
        'Consider implementing the suggested improvements from negative reviews.',
        'The multilingual analysis reveals consistent patterns across different markets.'
    ];
    
    return { results, summary, insights };
}

// API Connectivity Testing
async function testAPIConnectivity() {
    /**
     * Test API connectivity on page load and provide user feedback
     */
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            timeout: 5000  // 5 second timeout
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('API Health Check:', data);
            
            // Show subtle success indicator
            if (data.status === 'healthy') {
                addConnectionStatus('connected', 'API Connected');
            } else {
                addConnectionStatus('warning', 'API Partially Available');
            }
        } else {
            throw new Error(`API returned ${response.status}`);
        }
    } catch (error) {
        console.warn('API connectivity test failed:', error);
        addConnectionStatus('disconnected', 'API Unavailable - Using Demo Mode');
        
        // Show info message about demo mode
        setTimeout(() => {
            showInfo('API is not available. The application is running in demo mode with sample data.');
        }, 1000);
    }
}

function addConnectionStatus(status, message) {
    /**
     * Show a beautiful toast notification for API connection status
     */
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${status}`;
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">
                <i class="fas ${status === 'connected' ? 'fa-check-circle' : status === 'warning' ? 'fa-exclamation-triangle' : 'fa-times-circle'}"></i>
            </div>
            <div class="toast-message">
                <span class="toast-title">${getStatusTitle(status)}</span>
                <span class="toast-text">${message}</span>
            </div>
        </div>
        <div class="toast-progress"></div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('toast-show');
    }, 10);
    
    // Auto-hide toast after delay
    const hideDelay = status === 'connected' ? 3000 : status === 'warning' ? 5000 : 7000;
    
    setTimeout(() => {
        hideToast(toast);
    }, hideDelay);
    
    // Add click to dismiss
    toast.addEventListener('click', () => {
        hideToast(toast);
    });
}

function getStatusTitle(status) {
    const titles = {
        'connected': 'API Connected',
        'warning': 'API Warning',
        'disconnected': 'API Disconnected'
    };
    return titles[status] || 'Status Update';
}

function hideToast(toast) {
    toast.classList.add('toast-hide');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function showInfo(message) {
    /**
     * Show an informational message to the user
     */
    const infoDiv = document.createElement('div');
    infoDiv.className = 'info-message';
    infoDiv.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <p>${message}</p>
        <button class="close-info" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.querySelector('.main-content').prepend(infoDiv);
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        if (infoDiv.parentElement) {
            infoDiv.remove();
        }
    }, 8000);
}
