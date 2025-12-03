/**
 * Portfolio Unit 2 - Index JavaScript
 * Manages checkpoints display and navigation
 */

// Checkpoints data
const checkpointsData = [
    {
    number: 3,
    title: "Network Graph Visualization",
    description: "Social Network Analysis of U.S. Congress Twitter interactions using D3.js. Implementation of force-directed graphs, community detection (Louvain algorithm), centrality metrics (PageRank, Betweenness, In-Degree), and temporal analysis. Interactive dashboard with 475 nodes and 13,289 edges across 4 detected communities.",
    status: "completed",
    completionDate: "2024-11-03",
    exercises: 9,
    duration: "2 weeks",
    topics: ["Force-Directed Graphs", "Community Detection", "Centrality Metrics", "D3.js Visualization", "Social Network Analysis"]
    }
];

// Route configuration
let routeConfig = {};

// DOM Elements
const checkpointsContainer = document.getElementById('checkpointsContainer');
const loadingContainer = document.querySelector('.loading-container');
const progressFill = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Portfolio Unit 2 - Initializing...');
    
    // Load route configuration
    loadRouteConfig();
    
    // Calculate and update progress
    updateProgress();
    
    // Generate checkpoints
    generateCheckpoints();
    
    // Initialize theme management (if available)
    initializeTheme();
    
    console.log('✅ Portfolio initialized successfully');
});

/**
 * Load route configuration from HTML
 */
function loadRouteConfig() {
    const routeConfigElement = document.getElementById('route-config');
    if (routeConfigElement) {
        routeConfig = {
            home: routeConfigElement.dataset.homeUrl,
            checkpoint1: routeConfigElement.dataset.checkpoint1Url,
            checkpoint2: routeConfigElement.dataset.checkpoint2Url,
            checkpoint3: routeConfigElement.dataset.checkpoint3Url
        };
        console.log('📍 Routes loaded:', routeConfig);
    } else {
        console.warn('⚠️ Route configuration not found');
        // Fallback routes
        routeConfig = {
            home: '/',
            checkpoint1: '/portafolio/unidad2/checkpoint1',
            checkpoint2: '/portafolio/unidad2/checkpoint2',
            checkpoint3: '/portafolio/unidad2/checkpoint3'
        };
    }
}

/**
 * Calculate and update progress indicator
 */
function updateProgress() {
    const completedCount = checkpointsData.filter(cp => cp.status === 'completed').length;
    const totalCount = checkpointsData.length;
    const percentage = (completedCount / totalCount) * 100;
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${completedCount} of ${totalCount} checkpoints completed`;
    }
    
    console.log(`📊 Progress: ${completedCount}/${totalCount} (${percentage.toFixed(0)}%)`);
}

/**
 * Generate checkpoint cards
 */
function generateCheckpoints() {
    if (!checkpointsContainer) {
        console.error('❌ Checkpoints container not found');
        return;
    }
    
    checkpointsContainer.innerHTML = '';
    
    checkpointsData.forEach((checkpoint, index) => {
        const card = createCheckpointCard(checkpoint, index);
        checkpointsContainer.appendChild(card);
    });
    
    console.log(`✅ ${checkpointsData.length} checkpoint cards generated`);
}

/**
 * Create individual checkpoint card
 * @param {Object} checkpoint - Checkpoint data
 * @param {number} index - Index for animation delay
 * @returns {HTMLElement} - Card element
 */
function createCheckpointCard(checkpoint, index) {
    const card = document.createElement('div');
    card.className = 'checkpoint-card';
    card.style.animationDelay = `${index * 0.15}s`;
    
    // Status icon
    const statusIcon = getStatusIcon(checkpoint.status);
    
    // Format completion date
    const completionInfo = checkpoint.completionDate 
        ? `Completed: ${formatDate(checkpoint.completionDate)}`
        : `Duration: ${checkpoint.duration}`;
    
    card.innerHTML = `
        <div class="checkpoint-header">
            <div class="checkpoint-number">${checkpoint.number}</div>
            <div class="checkpoint-status ${checkpoint.status}">
                <i class="ti ti-${statusIcon}"></i>
                <span>${formatStatus(checkpoint.status)}</span>
            </div>
        </div>
        
        <div class="checkpoint-content">
            <h3>${checkpoint.title}</h3>
            <p class="checkpoint-description">${checkpoint.description}</p>
            
            <div class="checkpoint-meta">
                <div class="meta-item">
                    <i class="ti ti-book"></i>
                    <span>${checkpoint.exercises} exercises</span>
                </div>
                <div class="meta-item">
                    <i class="ti ti-clock"></i>
                    <span>${checkpoint.duration}</span>
                </div>
            </div>
            
            <div class="checkpoint-topics">
                ${createTopicsList(checkpoint.topics)}
            </div>
        </div>
        
        <div class="checkpoint-footer">
            <button class="view-btn" onclick="navigateToCheckpoint(${checkpoint.number})">
                <i class="ti ti-arrow-right"></i>
                <span>${checkpoint.status === 'completed' ? 'Review' : checkpoint.status === 'in-progress' ? 'Continue' : 'Start'}</span>
            </button>
            <span class="checkpoint-completion">${completionInfo}</span>
        </div>
    `;
    
    // Add click event to entire card
    card.addEventListener('click', (e) => {
        // Only block navigation if clicking footer elements
        if (e.target.closest('.checkpoint-footer') || 
            e.target.closest('.checkpoint-meta')) {
            return; // Don't navigate
        }
        // Navigate when clicking anywhere else on the card
        navigateToCheckpoint(checkpoint.number);
    });
    
    return card;
}

/**
 * Create topics list HTML
 * @param {Array} topics - Array of topic names
 * @returns {string} - HTML string
 */
function createTopicsList(topics) {
    const topicsHTML = topics.slice(0, 3).map(topic => 
        `<span class="topic-tag">${topic}</span>`
    ).join('');
    
    const moreTopics = topics.length > 3 ? 
        `<span class="topic-tag">+${topics.length - 3} more</span>` : '';
    
    return `<div class="checkpoint-topics-list">${topicsHTML}${moreTopics}</div>`;
}

/**
 * Get status icon
 * @param {string} status - Status type
 * @returns {string} - Icon name
 */
function getStatusIcon(status) {
    const icons = {
        'completed': 'circle-check',
        'in-progress': 'clock',
        'pending': 'circle-dashed'
    };
    return icons[status] || 'circle';
}

/**
 * Format status text
 * @param {string} status - Status type
 * @returns {string} - Formatted status
 */
function formatStatus(status) {
    const statusMap = {
        'completed': 'Completed',
        'in-progress': 'In Progress',
        'pending': 'Pending'
    };
    return statusMap[status] || status;
}

/**
 * Format date
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Navigate to checkpoint
 * @param {number} checkpointNumber - Checkpoint number
 */
function navigateToCheckpoint(checkpointNumber) {
    const checkpoint = checkpointsData.find(cp => cp.number === checkpointNumber);
    
    if (!checkpoint) {
        console.error(`❌ Checkpoint ${checkpointNumber} not found`);
        return;
    }
    
    // Get URL from route config
    const url = routeConfig[`checkpoint${checkpointNumber}`];
    
    if (!url) {
        console.error(`❌ URL for checkpoint ${checkpointNumber} not configured`);
        showNotification('Navigation error: URL not found', 'error');
        return;
    }
    
    console.log(`🚀 Navigating to Checkpoint ${checkpointNumber}: ${url}`);
    
    // Show loading feedback
    showNavigationFeedback(`Loading Checkpoint ${checkpointNumber}...`);
    
    // Navigate after brief delay for smooth transition
    setTimeout(() => {
        window.location.href = url;
    }, 600);
}

/**
 * Show navigation feedback
 * @param {string} message - Message to display
 */
function showNavigationFeedback(message) {
    // Remove any existing overlays
    const existingOverlays = document.querySelectorAll('.navigation-overlay');
    existingOverlays.forEach(overlay => overlay.remove());
    
    // Create temporary overlay
    const overlay = document.createElement('div');
    overlay.className = 'navigation-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9998;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div style="width: 50px; height: 50px; border: 4px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <p style="color: #334155; font-weight: 600; font-size: 1.1rem;">${message}</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Animate entrance
    requestAnimationFrame(() => {
        overlay.style.opacity = '1';
    });
}

/**
 * Show notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    
    const icons = {
        success: 'ti-circle-check',
        error: 'ti-alert-circle',
        info: 'ti-info-circle',
        warning: 'ti-alert-triangle'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: white;
        border-left: 4px solid ${colors[type]};
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 350px;
        display: flex;
        align-items: center;
        gap: 12px;
    `;
    
    notification.innerHTML = `
        <i class="ti ${icons[type]}" style="color: ${colors[type]}; font-size: 1.5rem;"></i>
        <span style="color: #334155; font-weight: 500;">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Animate entrance
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    });
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

/**
 * Initialize theme management
 */
function initializeTheme() {
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (!themeToggle) return;
    
    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeButton(currentTheme);
    
    // Theme toggle click handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeButton(newTheme);
        
        console.log(`🎨 Theme changed to: ${newTheme}`);
    });
}

/**
 * Update theme button text and icon
 * @param {string} theme - Current theme
 */
function updateThemeButton(theme) {
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (!themeToggle) return;
    
    const themeText = themeToggle.querySelector('.theme-text');
    const themeIcon = themeToggle.querySelector('.theme-icon svg');
    
    if (theme === 'dark') {
        if (themeText) themeText.textContent = 'Dark Mode';
        if (themeIcon) {
            themeIcon.innerHTML = '<path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
        }
    } else {
        if (themeText) themeText.textContent = 'Light Mode';
        if (themeIcon) {
            themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" fill="currentColor"/>';
        }
    }
}

/**
 * Search/filter checkpoints (can be added later)
 */
function filterCheckpoints(searchTerm) {
    const filteredData = checkpointsData.filter(checkpoint => 
        checkpoint.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        checkpoint.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        checkpoint.topics.some(topic => topic.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    
    // Re-generate checkpoints with filtered data
    checkpointsContainer.innerHTML = '';
    filteredData.forEach((checkpoint, index) => {
        const card = createCheckpointCard(checkpoint, index);
        checkpointsContainer.appendChild(card);
    });
    
    if (filteredData.length === 0) {
        checkpointsContainer.innerHTML = '<p style="text-align: center; color: var(--gray-600); padding: 40px;">No checkpoints found matching your search.</p>';
    }
}

/**
 * Export progress data (can be useful for tracking)
 */
function exportProgress() {
    const progressData = {
        unit: 2,
        checkpoints: checkpointsData.map(cp => ({
            number: cp.number,
            title: cp.title,
            status: cp.status,
            completionDate: cp.completionDate,
            exercises: cp.exercises
        })),
        completedCount: checkpointsData.filter(cp => cp.status === 'completed').length,
        totalCount: checkpointsData.length,
        exportDate: new Date().toISOString()
    };
    
    console.log('📤 Progress data:', progressData);
    return progressData;
}

// Add CSS for topics
const style = document.createElement('style');
style.textContent = `
    .checkpoint-topics {
        margin-top: 16px;
    }
    
    .checkpoint-topics-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .topic-tag {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(139, 92, 246, 0.1);
        color: var(--portfolio-primary);
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid rgba(139, 92, 246, 0.2);
        transition: all 0.2s ease;
    }
    
    .topic-tag:hover {
        background: rgba(139, 92, 246, 0.15);
        border-color: rgba(139, 92, 246, 0.3);
    }
`;
document.head.appendChild(style);

// Global error handling
window.addEventListener('error', (e) => {
    console.error('⚠️ Global error:', e.error);
});

// Make functions globally available
window.navigateToCheckpoint = navigateToCheckpoint;
window.filterCheckpoints = filterCheckpoints;
window.exportProgress = exportProgress;

// Debug mode for development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.PortfolioDebug = {
        checkpointsData,
        routeConfig,
        navigateToCheckpoint,
        filterCheckpoints,
        exportProgress,
        version: '1.0.0'
    };
    
    console.log('🔧 Portfolio Debug Mode Active');
    console.log('Access debug tools: window.PortfolioDebug');
}