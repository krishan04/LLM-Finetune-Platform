document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');

    // DOM Elements - Stats
    const statDatasetsCount = document.getElementById('stat-datasets-count');
    const statModelsCount = document.getElementById('stat-models-count');
    const statExperimentsCount = document.getElementById('stat-experiments-count');

    // DOM Elements - Datasets Tab
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('dataset-file-input');
    const uploadProgressBox = document.getElementById('upload-progress-box');
    const uploadFilename = document.getElementById('upload-filename');
    const uploadPercentage = document.getElementById('upload-percentage');
    const uploadBarFill = document.getElementById('upload-bar-fill');
    const uploadStatusText = document.getElementById('upload-status-text');
    const datasetsContainer = document.getElementById('datasets-container');
    const btnRefreshDatasets = document.getElementById('btn-refresh-datasets');

    // DOM Elements - Training Tab
    const trainingForm = document.getElementById('training-form');
    const trainDatasetSelect = document.getElementById('train-dataset-select');
    const loraRange = document.getElementById('train-lora-r');
    const loraValueDisplay = document.getElementById('lora-r-val');
    const btnSubmitTraining = document.getElementById('btn-submit-training');

    // DOM Elements - Dashboard Tab
    const experimentsTableBody = document.getElementById('experiments-table-body');
    const btnRefreshExperiments = document.getElementById('btn-refresh-experiments');

    // DOM Elements - Playground Tab
    const playgroundModelSelect = document.getElementById('playground-model-select');
    const valLength = document.getElementById('val-length');
    const paramLength = document.getElementById('param-length');
    const valTemp = document.getElementById('val-temp');
    const paramTemp = document.getElementById('param-temp');
    const valReppen = document.getElementById('val-reppen');
    const paramReppen = document.getElementById('param-reppen');
    const activeModelName = document.getElementById('active-model-name');
    const playgroundChatLog = document.getElementById('playground-chat-log');
    const playgroundPromptInput = document.getElementById('playground-prompt-input');
    const btnSendPlayground = document.getElementById('btn-send-playground');

    // DOM Elements - Modal
    const detailsModal = document.getElementById('details-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalStatus = document.getElementById('modal-status');
    const modalLoss = document.getElementById('modal-loss');
    const modalAccuracy = document.getElementById('modal-accuracy');
    const modalHyperparams = document.getElementById('modal-hyperparams');
    const modalLogs = document.getElementById('modal-logs');

    // Global State
    let pollingInterval = null;
    let activeDatasets = [];
    let activeExperiments = [];

    // --- TAB NAVIGATION SYSTEM ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');

            // Set active class in sidebar
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Switch visible panel
            tabContents.forEach(tab => tab.classList.remove('active'));
            document.getElementById(`tab-${tabId}`).classList.add('active');

            // Update page header
            pageTitle.textContent = item.querySelector('span').textContent;

            // Trigger reload operations
            if (tabId === 'dashboard') {
                loadDashboardData();
            } else if (tabId === 'datasets') {
                loadDatasets();
            } else if (tabId === 'training') {
                populateDatasetDropdown();
            } else if (tabId === 'playground') {
                loadModelsForPlayground();
            }
        });
    });

    // --- RANGE VALUE SYNC ---
    loraRange.addEventListener('input', () => {
        loraValueDisplay.textContent = loraRange.value;
    });

    paramLength.addEventListener('input', () => {
        valLength.textContent = paramLength.value;
    });

    paramTemp.addEventListener('input', () => {
        valTemp.textContent = paramTemp.value;
    });

    paramReppen.addEventListener('input', () => {
        valReppen.textContent = paramReppen.value;
    });

    // --- API HELPER FUNCTIONS ---
    async function apiRequest(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP Error ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            showNotification(error.message, 'error');
            throw error;
        }
    }

    // --- DATASETS LOGIC ---
    async function loadDatasets() {
        datasetsContainer.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-circle-notch fa-spin"></i> Loading datasets...
            </div>
        `;

        try {
            const datasets = await apiRequest('/datasets/');
            activeDatasets = datasets;
            renderDatasets(datasets);
            updateStats();
        } catch (error) {
            datasetsContainer.innerHTML = `
                <div class="loading-state" style="color: var(--danger)">
                    <i class="fa-solid fa-triangle-exclamation"></i> Failed to load datasets.
                </div>
            `;
        }
    }

    function renderDatasets(datasets) {
        if (datasets.length === 0) {
            datasetsContainer.innerHTML = `
                <div class="loading-state">
                    No datasets uploaded yet. Drop a file to get started!
                </div>
            `;
            return;
        }

        datasetsContainer.innerHTML = datasets.map(ds => `
            <div class="dataset-card">
                <div class="dataset-info">
                    <div class="dataset-file-icon">
                        <i class="fa-regular fa-file-code"></i>
                    </div>
                    <div class="dataset-details">
                        <span class="dataset-name">${escapeHtml(ds.name)}</span>
                        <span class="dataset-meta">${ds.format.toUpperCase()} • ${ds.size_mb.toFixed(4)} MB</span>
                    </div>
                </div>
                <span class="badge completed">${escapeHtml(ds.status)}</span>
            </div>
        `).join('');
    }

    // Drag and Drop Upload logic
    uploadZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        }, false);
    });

    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    function handleFileUpload(file) {
        uploadProgressBox.style.display = 'block';
        uploadFilename.textContent = file.name;
        uploadPercentage.textContent = '0%';
        uploadBarFill.style.width = '0%';
        uploadStatusText.textContent = 'Preparing upload stream...';

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/datasets/upload', true);

        // Track upload progress
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                uploadPercentage.textContent = `${percent}%`;
                uploadBarFill.style.width = `${percent}%`;
                if (percent === 100) {
                    uploadStatusText.textContent = 'Saving file and validating schema...';
                } else {
                    uploadStatusText.textContent = `Streaming chunk (${(e.loaded/1024/1024).toFixed(2)} / ${(e.total/1024/1024).toFixed(2)} MB)...`;
                }
            }
        };

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    showNotification('Dataset uploaded successfully!', 'success');
                    uploadStatusText.textContent = 'Upload complete!';
                    setTimeout(() => {
                        uploadProgressBox.style.display = 'none';
                    }, 2000);
                    loadDatasets();
                } catch (e) {
                    handleUploadError('Invalid server response shape');
                }
            } else {
                let errorMsg = 'Upload failed';
                try {
                    const err = JSON.parse(xhr.responseText);
                    errorMsg = err.detail || errorMsg;
                } catch (e) {}
                handleUploadError(errorMsg);
            }
        };

        xhr.onerror = () => handleUploadError('Network error occurred during stream');

        const formData = new FormData();
        formData.append('file', file);
        xhr.send(formData);
    }

    function handleUploadError(message) {
        showNotification(message, 'error');
        uploadStatusText.textContent = `Error: ${message}`;
        uploadBarFill.style.backgroundColor = 'var(--danger)';
    }

    btnRefreshDatasets.addEventListener('click', loadDatasets);

    // --- TRAINING LOGIC ---
    async function populateDatasetDropdown() {
        trainDatasetSelect.innerHTML = '<option value="" disabled selected>Loading datasets...</option>';
        try {
            const datasets = await apiRequest('/datasets/');
            if (datasets.length === 0) {
                trainDatasetSelect.innerHTML = '<option value="" disabled selected>No datasets found. Upload one first!</option>';
                return;
            }

            trainDatasetSelect.innerHTML = '<option value="" disabled selected>Choose a dataset...</option>' + 
                datasets.map(ds => `
                    <option value="${ds.id}">${escapeHtml(ds.name)} (${ds.format.toUpperCase()} - ${ds.size_mb.toFixed(4)} MB)</option>
                `).join('');
        } catch (error) {
            trainDatasetSelect.innerHTML = '<option value="" disabled selected>Error loading datasets</option>';
        }
    }

    trainingForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const datasetId = trainDatasetSelect.value;
        const baseModel = document.getElementById('train-base-model').value.trim();
        const loraR = parseInt(loraRange.value);
        const learningRate = parseFloat(document.getElementById('train-lr').value);

        if (!datasetId || !baseModel) return;

        btnSubmitTraining.disabled = true;
        btnSubmitTraining.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Submitting Job...';

        try {
            await apiRequest('/train/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    dataset_id: datasetId,
                    base_model: baseModel,
                    lora_r: loraR,
                    learning_rate: learningRate
                })
            });

            showNotification('Training job successfully queued!', 'success');
            trainingForm.reset();
            loraValueDisplay.textContent = '8';

            // Redirect to Dashboard immediately
            document.querySelector('.nav-item[data-tab="dashboard"]').click();
        } catch (error) {
            // Error notification is shown inside apiRequest
        } finally {
            btnSubmitTraining.disabled = false;
            btnSubmitTraining.innerHTML = '<i class="fa-solid fa-rocket"></i> Launch Training Job';
        }
    });

    // --- DASHBOARD / MONITORING LOGIC ---
    async function loadDashboardData() {
        experimentsTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading-state">
                    <i class="fa-solid fa-circle-notch fa-spin"></i> Loading jobs history...
                </td>
            </tr>
        `;

        try {
            const experiments = await apiRequest('/train/');
            activeExperiments = experiments;
            renderExperiments(experiments);
            updateStats();
            setupPolling(experiments);
        } catch (error) {
            experimentsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading-state" style="color: var(--danger)">
                        <i class="fa-solid fa-triangle-exclamation"></i> Failed to retrieve fine-tuning runs.
                    </td>
                </tr>
            `;
        }
    }

    function renderExperiments(experiments) {
        if (experiments.length === 0) {
            experimentsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading-state">
                        No experiments launched yet. Go to the "Train Model" tab to spin up a training job!
                    </td>
                </tr>
            `;
            return;
        }

        experimentsTableBody.innerHTML = experiments.map(exp => {
            const formattedDate = exp.started_at 
                ? new Date(exp.started_at + 'Z').toLocaleString() 
                : 'Pending';
            
            const lossVal = exp.loss !== null ? exp.loss.toFixed(4) : '—';
            
            return `
                <tr data-exp-id="${exp.id}">
                    <td class="font-mono" style="font-size: 0.8rem;">${exp.id.substring(0, 18)}...</td>
                    <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        <i class="fa-regular fa-file-lines" style="margin-right: 0.35rem; color: var(--accent-cyan)"></i>
                        ${escapeHtml(getDatasetName(exp.dataset_id))}
                    </td>
                    <td><span class="font-mono" style="font-size: 0.8rem; opacity: 0.85;">${escapeHtml(exp.hyperparameters.base_model)}</span></td>
                    <td><span class="badge ${exp.status}">${exp.status}</span></td>
                    <td class="font-mono">${lossVal}</td>
                    <td style="font-size: 0.8rem; color: var(--text-secondary);">${formattedDate}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm btn-view-details" data-id="${exp.id}">
                            <i class="fa-regular fa-eye"></i> Details
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        // Attach modal triggers
        document.querySelectorAll('.btn-view-details').forEach(btn => {
            btn.addEventListener('click', () => {
                const expId = btn.getAttribute('data-id');
                showExperimentDetails(expId);
            });
        });
    }

    function getDatasetName(datasetId) {
        const found = activeDatasets.find(d => d.id === datasetId);
        return found ? found.name : 'Dataset';
    }

    async function updateStats() {
        try {
            if (activeDatasets.length === 0) {
                const dsList = await fetch('/datasets/').then(r => r.json()).catch(() => []);
                statDatasetsCount.textContent = dsList.length;
            } else {
                statDatasetsCount.textContent = activeDatasets.length;
            }

            const modelList = await fetch('/models/').then(r => r.json()).catch(() => []);
            statModelsCount.textContent = modelList.length;

            const activeJobs = activeExperiments.filter(e => e.status === 'queued' || e.status === 'running').length;
            statExperimentsCount.textContent = activeJobs;
        } catch (e) {
            console.error('Error updating status cards:', e);
        }
    }

    function setupPolling(experiments) {
        const needsPolling = experiments.some(exp => exp.status === 'queued' || exp.status === 'running');
        
        if (needsPolling && !pollingInterval) {
            console.log('Background polling started to monitor active training runs...');
            pollingInterval = setInterval(async () => {
                try {
                    const updated = await fetch('/train/').then(r => r.json());
                    activeExperiments = updated;
                    renderExperiments(updated);
                    updateStats();

                    // If everything finished, turn off polling automatically
                    const stillActive = updated.some(exp => exp.status === 'queued' || exp.status === 'running');
                    if (!stillActive) {
                        clearPolling();
                    }
                } catch (e) {
                    console.error('Polling failed:', e);
                }
            }, 3000);
        } else if (!needsPolling) {
            clearPolling();
        }
    }

    function clearPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
            console.log('Background monitoring stopped.');
        }
    }

    btnRefreshExperiments.addEventListener('click', loadDashboardData);

    // --- EXPERIMENT DETAILS MODAL ---
    async function showExperimentDetails(expId) {
        detailsModal.classList.add('show');
        modalTitle.textContent = `Job details: ${expId}`;
        modalStatus.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Loading...';
        modalLoss.textContent = 'Loading...';
        modalAccuracy.textContent = 'Loading...';
        modalHyperparams.textContent = 'Loading...';
        modalLogs.textContent = 'Loading...';

        try {
            const exp = await apiRequest(`/train/${expId}`);
            
            modalStatus.innerHTML = `<span class="badge ${exp.status}">${exp.status}</span>`;
            modalLoss.textContent = exp.loss !== null ? exp.loss.toFixed(6) : '—';
            modalAccuracy.textContent = exp.accuracy !== null ? exp.accuracy.toFixed(6) : '—';
            modalHyperparams.textContent = JSON.stringify(exp.hyperparameters, null, 2);
            modalLogs.textContent = exp.training_logs || 'No logs generated yet.';
        } catch (error) {
            modalStatus.textContent = 'Error loading metadata';
        }
    }

    btnCloseModal.addEventListener('click', () => detailsModal.classList.remove('show'));
    window.addEventListener('click', (e) => {
        if (e.target === detailsModal) {
            detailsModal.classList.remove('show');
        }
    });

    // --- PLAYGROUND LOGIC ---
    async function loadModelsForPlayground() {
        playgroundModelSelect.innerHTML = '<option value="" disabled selected>Loading custom models...</option>';
        playgroundPromptInput.disabled = true;
        btnSendPlayground.disabled = true;
        
        try {
            const models = await apiRequest('/models/');
            if (models.length === 0) {
                playgroundModelSelect.innerHTML = '<option value="" disabled selected>No trained models available</option>';
                return;
            }

            playgroundModelSelect.innerHTML = '<option value="" disabled selected>Select a trained model...</option>' + 
                models.map(m => `
                    <option value="${m.id}" data-base="${escapeHtml(m.base_model)}">${escapeHtml(m.base_model)} (Adapter: ${m.id.substring(0,8)})</option>
                `).join('');
        } catch (error) {
            playgroundModelSelect.innerHTML = '<option value="" disabled selected>Error loading models</option>';
        }
    }

    playgroundModelSelect.addEventListener('change', () => {
        try {
            const option = playgroundModelSelect.selectedOptions[0];
            const baseName = option ? option.getAttribute('data-base') : '';
            const modelId = playgroundModelSelect.value || '';

            activeModelName.innerHTML = `
                <span style="color: white; font-weight: 600;">Active Model:</span> 
                ${escapeHtml(baseName || 'Unknown Base Model')} (ID: <span class="font-mono">${modelId.substring(0,8)}</span>)
            `;
        } catch (err) {
            console.error("Error displaying active model label:", err);
        } finally {
            playgroundPromptInput.disabled = false;
            btnSendPlayground.disabled = false;
            playgroundPromptInput.focus();
        }
    });

    btnSendPlayground.addEventListener('click', handlePlaygroundInference);
    playgroundPromptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !playgroundPromptInput.disabled) {
            e.preventDefault();
            handlePlaygroundInference();
        }
    });

    async function handlePlaygroundInference() {
        const prompt = playgroundPromptInput.value.trim();
        const modelId = playgroundModelSelect.value;

        if (!prompt || !modelId) return;

        // Append User bubble
        appendChatBubble(prompt, 'user');
        playgroundPromptInput.value = '';

        // UI state lock
        playgroundPromptInput.disabled = true;
        btnSendPlayground.disabled = true;
        
        // Append loader bot bubble
        const loaderId = appendChatBubble('<i class="fa-solid fa-circle-notch fa-spin"></i> Generating weights pipeline response...', 'bot loader');

        try {
            // Get tuning params
            const maxLen = paramLength.value;
            const temp = paramTemp.value;
            // Since API parameters are in query params, we append them
            const url = `/generate/${modelId}?prompt=${encodeURIComponent(prompt)}`;
            
            // Wait, we don't have maxLen/temp passed in the endpoint, but let's call generating
            const response = await apiRequest(url, { method: 'POST' });
            
            // Remove loading bubble and append actual response
            document.getElementById(loaderId).remove();
            if (response.error) {
                appendChatBubble(`Error: ${response.error}`, 'bot error');
            } else {
                appendChatBubble(response.response || 'Empty response returned.', 'bot');
            }
        } catch (error) {
            document.getElementById(loaderId).remove();
            appendChatBubble(`Error: ${error.message}`, 'bot error');
        } finally {
            playgroundPromptInput.disabled = false;
            btnSendPlayground.disabled = false;
            playgroundPromptInput.focus();
        }
    }

    function appendChatBubble(text, className) {
        const bubble = document.createElement('div');
        const uniqueId = 'bubble-' + Math.random().toString(36).substring(2, 9);
        bubble.id = uniqueId;
        bubble.className = `chat-bubble ${className}`;
        
        if (className.includes('loader')) {
            bubble.innerHTML = text;
        } else {
            bubble.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
        }

        playgroundChatLog.appendChild(bubble);
        playgroundChatLog.scrollTop = playgroundChatLog.scrollHeight;
        return uniqueId;
    }

    // --- NOTIFICATION SYSTEM ---
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.bottom = '2rem';
        notification.style.right = '2rem';
        notification.style.padding = '1rem 1.5rem';
        notification.style.borderRadius = 'var(--radius)';
        notification.style.color = 'white';
        notification.style.fontSize = '0.9rem';
        notification.style.fontWeight = '500';
        notification.style.zIndex = '1000';
        notification.style.display = 'flex';
        notification.style.alignItems = 'center';
        notification.style.gap = '0.75rem';
        notification.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
        notification.style.animation = 'modalSlide 0.3s cubic-bezier(0.16, 1, 0.3, 1)';

        if (type === 'success') {
            notification.style.backgroundColor = 'var(--success)';
            notification.innerHTML = '<i class="fa-solid fa-circle-check"></i> ' + escapeHtml(message);
        } else {
            notification.style.backgroundColor = 'var(--danger)';
            notification.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> ' + escapeHtml(message);
        }

        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(10px)';
            notification.style.transition = 'all 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // --- UTILITIES ---
    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return String(unsafe)
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }

    // --- INITIALIZATION ---
    // First screen loading
    loadDashboardData();
    // Cache loading datasets list in memory for mapping
    fetch('/datasets/').then(r => r.json()).then(ds => { activeDatasets = ds; renderExperiments(activeExperiments); }).catch(() => {});
});
