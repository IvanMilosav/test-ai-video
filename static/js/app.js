// Video Analyzer Web App
// Uses API key from .env file on server

// State
let selectedFile = null;
let analysisResult = null;

// API Base URL - supports both Railway and Netlify deployments
// For Netlify: Create a config.js file or use environment variable injection
const API_BASE_URL = window.API_BASE_URL || window.location.origin;

// Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const clearBtn = document.getElementById('clearBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');

const apiKeySection = document.getElementById('apiKeySection');
const analyzeSection = document.getElementById('analyzeSection');
const analyzeBtn = document.getElementById('analyzeBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

const resultsSection = document.getElementById('resultsSection');
const resultPreview = document.getElementById('resultPreview');
const downloadBtn = document.getElementById('downloadBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

const dataModal = document.getElementById('dataModal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const closeModalBtn = document.getElementById('closeModalBtn');

const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize
function init() {
    setupEventListeners();
    updateUI();
}

function setupEventListeners() {
    // File selection
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent event bubbling
        fileInput.click();
    });
    fileInput.addEventListener('change', handleFileSelect);
    clearBtn.addEventListener('click', clearFile);

    // Drag and drop
    dropZone.addEventListener('click', (e) => {
        // Only open file input if clicking the drop zone itself, not the button
        if (e.target === dropZone || e.target.closest('.drop-zone-icon, .drop-zone-text, .drop-zone-or')) {
            fileInput.click();
        }
    });
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Analysis
    analyzeBtn.addEventListener('click', analyzeVideo);

    // Results
    downloadBtn.addEventListener('click', downloadResults);
    newAnalysisBtn.addEventListener('click', resetApp);

    // Data viewers
    document.getElementById('viewOntologyBtn').addEventListener('click', () => viewData('ontology'));
    document.getElementById('viewBrainBtn').addEventListener('click', () => viewData('brain'));
    document.getElementById('viewHistoryBtn').addEventListener('click', () => viewData('history'));

    // Modal
    closeModalBtn.addEventListener('click', closeModal);
    dataModal.addEventListener('click', (e) => {
        if (e.target === dataModal) closeModal();
    });
}

// File handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        setFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
        setFile(file);
    } else {
        showAlert('Please drop a valid video file', 'error');
    }
}

function setFile(file) {
    // Check if it's a video file
    if (!file.type.startsWith('video/')) {
        showAlert('Please select a valid video file (MP4, MOV, AVI, MKV)', 'error');
        return;
    }

    // Check file size (512MB limit - will auto-compress if over 20MB)
    const maxSize = 512 * 1024 * 1024; // 512MB
    if (file.size > maxSize) {
        showAlert('Video file is too large. Maximum size is 512MB.', 'error');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
    dropZone.style.display = 'none';

    updateUI();
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    dropZone.style.display = 'block';
    resultsSection.style.display = 'none';

    updateUI();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// UI updates
function updateUI() {
    // Hide API key section (using .env file)
    apiKeySection.style.display = 'none';

    // Show analyze section if file is selected
    if (selectedFile) {
        analyzeSection.style.display = 'block';
    } else {
        analyzeSection.style.display = 'none';
    }
}

// Video analysis with real-time streaming
async function analyzeVideo() {
    if (!selectedFile) {
        showAlert('Please select a video file', 'error');
        return;
    }

    // Disable button
    analyzeBtn.disabled = true;
    document.getElementById('analyzeBtnText').textContent = 'Analyzing...';
    progressSection.style.display = 'block';
    updateProgress(5, 'Preparing...');

    try {
        const formData = new FormData();
        formData.append('video', selectedFile);

        // Use streaming endpoint
        const response = await fetch(`${API_BASE_URL}/api/analyze-video-stream`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Failed to start analysis');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let progress = 10;
        let buffer = ''; // Buffer for incomplete messages

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            // Decode and add to buffer
            buffer += decoder.decode(value, { stream: true });

            // Process complete messages (ending with \n\n)
            const messages = buffer.split('\n\n');

            // Keep last incomplete message in buffer
            buffer = messages.pop() || '';

            for (const message of messages) {
                const lines = message.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));

                            if (data.error) {
                                throw new Error(data.error);
                            }

                            if (data.status) {
                                // Update progress bar with real message
                                progress = Math.min(progress + 2, 95);
                                updateProgress(progress, data.status);
                            }

                            if (data.success) {
                                updateProgress(100, 'Complete!');
                                analysisResult = { output: data.output };
                                displayResults(analysisResult);
                            }
                        } catch (e) {
                            console.error('JSON parse error:', e, 'Line:', line.substring(0, 100));
                            // Continue processing other messages
                        }
                    }
                }
            }
        }

    } catch (error) {
        console.error('Analysis error:', error);

        // Check if it's an API key error
        if (error.message.includes('API key not configured')) {
            showAlert('⚠️ API Key Missing! Please create a .env file with GOOGLE_API_KEY=your_key_here', 'error');
        } else {
            showAlert(`Analysis failed: ${error.message}`, 'error');
        }

        // Reset UI
        analyzeBtn.disabled = false;
        document.getElementById('analyzeBtnText').textContent = 'Analyze Video';
        progressSection.style.display = 'none';
    }
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

function displayResults(result) {
    // Format result for display
    const output = result.output || 'No analysis data available';
    resultPreview.textContent = output;

    // Show results section
    resultsSection.style.display = 'block';
    analyzeSection.style.display = 'none';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Results handling
function downloadResults() {
    if (!analysisResult) return;

    const output = analysisResult.output || 'No data';
    const blob = new Blob([output], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `video_analysis_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showAlert('Results downloaded!', 'success');
}

function resetApp() {
    clearFile();
    analysisResult = null;
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
    analyzeBtn.disabled = false;
    document.getElementById('analyzeBtnText').textContent = 'Analyze Video';
    updateUI();
}

// Data viewing
async function viewData(type) {
    showLoading();

    try {
        let endpoint, title;

        switch (type) {
            case 'ontology':
                endpoint = '/api/data/master-ontology';
                title = '📊 Master Ontology - Statistics Brain';
                break;
            case 'brain':
                endpoint = '/api/data/script-clip-brain';
                title = '🧠 Script-Clip Brain - Recipe Book';
                break;
            case 'history':
                endpoint = '/api/data/history';
                title = '🎬 Analysis History';
                break;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error('Failed to load data');
        }

        const data = await response.json();

        modalTitle.textContent = title;

        if (type === 'history') {
            displayHistory(data.files || []);
        } else {
            modalBody.innerHTML = `<pre>${data.content || 'No data available yet. Analyze some videos first!'}</pre>`;
        }

        showModal();

    } catch (error) {
        console.error('Data loading error:', error);
        showAlert('Failed to load data. Data files may not exist yet.', 'info');
    } finally {
        hideLoading();
    }
}

function displayHistory(files) {
    if (files.length === 0) {
        modalBody.innerHTML = '<p style="color: var(--text-secondary);">No analysis history yet. Analyze some videos to see them here!</p>';
        return;
    }

    let html = '<div class="history-list">';
    files.forEach(file => {
        html += `
            <div class="history-item" onclick="viewHistoryFile('${file.path}')">
                <div class="history-name">${file.name}</div>
                <div class="history-meta">${file.size} | ${file.date}</div>
            </div>
        `;
    });
    html += '</div>';

    modalBody.innerHTML = html;
}

async function viewHistoryFile(path) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/data/file?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        modalBody.innerHTML = `<pre>${data.content}</pre>`;
    } catch (error) {
        showAlert('Failed to load file', 'error');
    }
}

// Modal handling
function showModal() {
    dataModal.style.display = 'flex';
}

function closeModal() {
    dataModal.style.display = 'none';
}

// Loading overlay
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Alerts
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    // Insert at top of main
    const main = document.querySelector('main');
    main.insertBefore(alert, main.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
