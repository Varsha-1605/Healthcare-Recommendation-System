// HealthAI - WebSocket Client Implementation

class HealthAIWebSocket {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.pingInterval = null;
        this.connectionStatusElement = null;
        
        this.init();
    }
    
    init() {
        this.connectionStatusElement = document.getElementById('connection-status');
        this.connect();
        this.setupEventListeners();
    }
    
    connect() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 20000,
                forceNew: true
            });
            
            this.setupSocketEvents();
            this.updateConnectionStatus('connecting', 'Connecting...');
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.updateConnectionStatus('disconnected', 'Connection Failed');
            this.scheduleReconnect();
        }
    }
    
    setupSocketEvents() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected', 'Connected');
            this.startPingInterval();
            
            // Request initial recommendations
            this.requestRecommendations();
            
            // Track connection event
            this.trackActivity('websocket_connect');
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket disconnected:', reason);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected', 'Disconnected');
            this.stopPingInterval();
            
            // Only attempt reconnection if it wasn't a manual disconnect
            if (reason !== 'io client disconnect') {
                this.scheduleReconnect();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.updateConnectionStatus('disconnected', 'Connection Error');
            this.scheduleReconnect();
        });
        
        // Custom events
        this.socket.on('status', (data) => {
            console.log('Server status:', data.msg);
        });
        
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data.message);
            if (window.HealthAI) {
                window.HealthAI.showNotification(data.message, 'error');
            }
        });
        
        // Recommendations events
        this.socket.on('recommendations_update', (data) => {
            this.handleRecommendationsUpdate(data);
        });
        
        this.socket.on('quick_recommendations', (data) => {
            this.handleQuickRecommendations(data);
        });
        
        // Search events
        this.socket.on('search_suggestions', (data) => {
            this.handleSearchSuggestions(data);
        });
        
        // Health check response
        this.socket.on('health_response', (data) => {
            console.log('Health check response:', data);
        });
    }
    
    setupEventListeners() {
        // Listen for page activity to track user engagement
        document.addEventListener('click', (e) => {
            this.handleUserInteraction(e);
        });
        
        // Track content views
        this.setupContentTracking();
        
        // Setup search tracking
        this.setupSearchTracking();
        
        // Track form submissions
        this.setupFormTracking();
    }
    
    handleUserInteraction(event) {
        if (!this.isConnected) return;
        
        const target = event.target;
        const contentId = target.dataset.contentId;
        const activityType = this.getActivityType(target);
        
        if (activityType) {
            this.trackActivity(activityType, {
                content_id: contentId,
                element: target.tagName.toLowerCase(),
                timestamp: new Date().toISOString()
            });
        }
    }
    
    getActivityType(element) {
        if (element.classList.contains('btn-primary') || element.closest('.btn-primary')) {
            return 'click';
        }
        if (element.closest('a[href*="/content/"]')) {
            return 'content_click';
        }
        if (element.classList.contains('bookmark-btn') || element.closest('.bookmark-btn')) {
            return 'bookmark';
        }
        if (element.classList.contains('share-btn') || element.closest('.share-btn')) {
            return 'share';
        }
        return null;
    }
    
    setupContentTracking() {
        // Track when user views content
        const contentElements = document.querySelectorAll('[data-content-id]');
        
        if (contentElements.length > 0 && 'IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const contentId = entry.target.dataset.contentId;
                        if (contentId) {
                            this.trackActivity('view', {
                                content_id: parseInt(contentId),
                                duration: 0,
                                timestamp: new Date().toISOString()
                            });
                        }
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px'
            });
            
            contentElements.forEach(el => observer.observe(el));
        }
    }
    
    setupSearchTracking() {
        const searchInputs = document.querySelectorAll('input[type="search"], #search-query');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                const query = input.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        this.requestSearchSuggestions(query);
                    }, 300);
                }
            });
        });
    }
    
    setupFormTracking() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const formId = form.id || form.className;
                this.trackActivity('form_submit', {
                    form_id: formId,
                    timestamp: new Date().toISOString()
                });
            });
        });
    }
    
    // WebSocket API methods
    trackActivity(activityType, metadata = {}) {
        if (!this.isConnected) return;
        
        this.socket.emit('track_activity', {
            type: activityType,
            ...metadata
        });
    }
    
    requestRecommendations() {
        if (!this.isConnected) return;
        
        this.socket.emit('request_recommendations', {
            timestamp: new Date().toISOString()
        });
    }
    
    requestSearchSuggestions(query) {
        if (!this.isConnected) return;
        
        this.socket.emit('search_suggestions', {
            query: query
        });
    }
    
    performHealthCheck() {
        if (!this.isConnected) return;
        
        this.socket.emit('health_check');
    }
    
    // Event handlers
    handleRecommendationsUpdate(data) {
        console.log('Recommendations updated:', data);
        
        // Update recommendations in the UI
        this.updateRecommendationsUI(data);
        
        // Show notification if appropriate
        if (data.ai_recommendations && data.ai_recommendations.length > 0) {
            if (window.HealthAI) {
                window.HealthAI.showNotification('New health recommendations available!', 'info');
            }
            
            // Show toast notification
            this.showRecommendationToast();
        }
    }
    
    handleQuickRecommendations(data) {
        console.log('Quick recommendations:', data);
        
        // Update quick recommendations sidebar or widget
        this.updateQuickRecommendationsUI(data);
    }
    
    handleSearchSuggestions(data) {
        console.log('Search suggestions:', data);
        
        // Update search suggestions in the UI
        this.updateSearchSuggestionsUI(data);
    }
    
    // UI update methods
    updateRecommendationsUI(data) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;
        
        const recommendations = data.content_recommendations || [];
        
        if (recommendations.length > 0) {
            const html = recommendations.map((content, index) => `
                <div class="col-lg-6" data-aos="fade-up" data-aos-delay="${(index + 1) * 100}">
                    <div class="recommendation-card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <span class="badge bg-primary me-2">${content.category.replace('_', ' ')}</span>
                                <span class="badge bg-secondary">${content.content_type}</span>
                            </div>
                            <div class="ai-badge">
                                <i class="fas fa-robot text-primary"></i>
                            </div>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${content.title}</h5>
                            <p class="card-text">${content.description.substring(0, 150)}...</p>
                        </div>
                        <div class="card-footer">
                            <a href="${content.url}" class="btn btn-primary">
                                <i class="fas fa-arrow-right me-1"></i>View Details
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
            
            // Reinitialize AOS if available
            if (typeof AOS !== 'undefined') {
                AOS.refresh();
            }
        }
    }
    
    updateQuickRecommendationsUI(data) {
        const quickRecsContainer = document.getElementById('quick-recommendations');
        if (!quickRecsContainer) return;
        
        const recommendations = data.recommendations || [];
        
        if (recommendations.length > 0) {
            const html = recommendations.map(rec => `
                <div class="quick-rec-item">
                    <span class="badge bg-primary">${rec.category}</span>
                    <span class="rec-title">${rec.title}</span>
                </div>
            `).join('');
            
            quickRecsContainer.innerHTML = html;
        }
    }
    
    updateSearchSuggestionsUI(data) {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (!suggestionsContainer) return;
        
        const suggestions = data.suggestions || [];
        
        if (suggestions.length > 0) {
            const html = suggestions.map(suggestion => `
                <div class="suggestion-item" onclick="selectSuggestion('${suggestion.text}')">
                    <div class="suggestion-text">${suggestion.text}</div>
                    <div class="suggestion-category">${suggestion.category || suggestion.type}</div>
                </div>
            `).join('');
            
            suggestionsContainer.innerHTML = html;
            suggestionsContainer.style.display = 'block';
        } else {
            suggestionsContainer.style.display = 'none';
        }
    }
    
    showRecommendationToast() {
        const toastElement = document.getElementById('live-update-toast');
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            toastElement.querySelector('.toast-body').textContent = 'New health recommendations available!';
            toast.show();
        }
    }
    
    // Connection management
    updateConnectionStatus(status, message) {
        if (!this.connectionStatusElement) return;
        
        const statusIcon = document.getElementById('status-icon');
        const statusText = document.getElementById('status-text');
        
        if (statusIcon && statusText) {
            statusIcon.className = `fas fa-circle ${status}`;
            statusText.textContent = message;
            
            // Update badge color based on status
            const badge = this.connectionStatusElement.querySelector('.badge');
            if (badge) {
                badge.className = `badge bg-${status === 'connected' ? 'success' : status === 'connecting' ? 'warning' : 'danger'}`;
            }
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnect attempts reached');
            this.updateConnectionStatus('disconnected', 'Connection Failed');
            return;
        }
        
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
        this.reconnectAttempts++;
        
        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        this.updateConnectionStatus('connecting', `Reconnecting in ${Math.ceil(delay / 1000)}s...`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    startPingInterval() {
        this.pingInterval = setInterval(() => {
            if (this.isConnected) {
                this.performHealthCheck();
            }
        }, 30000); // Ping every 30 seconds
    }
    
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        this.stopPingInterval();
        this.updateConnectionStatus('disconnected', 'Disconnected');
    }
    
    reconnect() {
        this.disconnect();
        this.reconnectAttempts = 0;
        setTimeout(() => {
            this.connect();
        }, 1000);
    }
}

// Initialize WebSocket connection when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is logged in
    if (document.body.dataset.userId || document.querySelector('[data-user-id]')) {
        window.healthAISocket = new HealthAIWebSocket();
        
        // Make socket available globally for other scripts
        window.socket = window.healthAISocket.socket;
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (window.healthAISocket) {
        if (document.hidden) {
            // Page is hidden, reduce activity
            console.log('Page hidden, reducing WebSocket activity');
        } else {
            // Page is visible again, resume normal activity
            console.log('Page visible, resuming WebSocket activity');
            if (!window.healthAISocket.isConnected) {
                window.healthAISocket.reconnect();
            } else {
                // Request fresh recommendations
                window.healthAISocket.requestRecommendations();
            }
        }
    }
});

// Handle online/offline events
window.addEventListener('online', function() {
    console.log('Network connection restored');
    if (window.healthAISocket && !window.healthAISocket.isConnected) {
        window.healthAISocket.reconnect();
    }
});

window.addEventListener('offline', function() {
    console.log('Network connection lost');
    if (window.healthAISocket) {
        window.healthAISocket.updateConnectionStatus('disconnected', 'Offline');
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.healthAISocket) {
        window.healthAISocket.disconnect();
    }
});
