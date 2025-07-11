// HealthAI - Analytics Dashboard JavaScript

class HealthAnalytics {
    constructor() {
        this.charts = {};
        this.chartConfigs = {};
        this.colorPalette = [
            '#007bff', '#28a745', '#ffc107', '#dc3545', 
            '#17a2b8', '#6f42c1', '#fd7e14', '#20c997'
        ];
        
        this.init();
    }
    
    init() {
        this.setupChartDefaults();
        this.initializeEventListeners();
    }
    
    setupChartDefaults() {
        // Set Chart.js global defaults
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
            Chart.defaults.font.size = 12;
            Chart.defaults.color = '#6c757d';
            Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';
            
            // Register custom plugins
            this.registerChartPlugins();
        }
    }
    
    registerChartPlugins() {
        // Custom plugin for better responsive behavior
        Chart.register({
            id: 'healthai-responsive',
            beforeDraw: function(chart) {
                if (chart.canvas.parentNode.offsetWidth < 400) {
                    chart.options.plugins.legend.display = false;
                }
            }
        });
    }
    
    initializeEventListeners() {
        // Chart refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-refresh-chart]')) {
                const chartId = e.target.dataset.refreshChart;
                this.refreshChart(chartId);
            }
        });
        
        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-export-chart]')) {
                const chartId = e.target.dataset.exportChart;
                this.exportChart(chartId);
            }
        });
        
        // Window resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }
    
    // Chart initialization methods
    createActivityChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const chartData = {
            labels: data.labels || [],
            datasets: [{
                label: 'Activities',
                data: data.values || [],
                backgroundColor: this.colorPalette.map(color => color + '80'),
                borderColor: this.colorPalette,
                borderWidth: 2,
                hoverOffset: 4
            }]
        };
        
        const config = {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    createEngagementChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const chartData = {
            labels: data.labels || [],
            datasets: [{
                label: 'Daily Engagement',
                data: data.values || [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        };
        
        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#007bff',
                        borderWidth: 1
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    createHealthScoreGauge(canvasId, score = 85) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const chartData = {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [
                    this.getScoreColor(score),
                    '#e9ecef'
                ],
                borderWidth: 0,
                cutout: '75%'
            }]
        };
        
        const config = {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                circumference: 180,
                rotation: 270,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 2000
                }
            },
            plugins: [{
                id: 'gaugeText',
                beforeDraw: function(chart) {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    ctx.font = "bold 24px Inter";
                    ctx.fillStyle = "#007bff";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    
                    const text = score.toString();
                    const textX = Math.round(width / 2);
                    const textY = Math.round(height / 2) + 10;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    createConsultationChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const chartData = {
            labels: data.labels || [],
            datasets: [{
                label: 'Consultations',
                data: data.values || [],
                backgroundColor: 'rgba(0, 123, 255, 0.8)',
                borderColor: '#007bff',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        };
        
        const config = {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutBounce'
                }
            }
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    createCategoryChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const chartData = {
            labels: data.labels || [],
            datasets: [{
                data: data.values || [],
                backgroundColor: this.colorPalette.slice(0, data.labels.length).map(color => color + '80'),
                borderColor: this.colorPalette.slice(0, data.labels.length),
                borderWidth: 2
            }]
        };
        
        const config = {
            type: 'polarArea',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        pointLabels: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    createTrendChart(canvasId, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const config = {
            type: 'line',
            data: {
                labels: datasets.labels || [],
                datasets: datasets.data.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.values,
                    borderColor: this.colorPalette[index % this.colorPalette.length],
                    backgroundColor: this.colorPalette[index % this.colorPalette.length] + '20',
                    tension: 0.4,
                    fill: false,
                    pointBackgroundColor: this.colorPalette[index % this.colorPalette.length],
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        };
        
        this.charts[canvasId] = new Chart(ctx, config);
        this.chartConfigs[canvasId] = config;
        return this.charts[canvasId];
    }
    
    // Utility methods
    getScoreColor(score) {
        if (score >= 80) return '#28a745'; // Green
        if (score >= 60) return '#ffc107'; // Yellow
        if (score >= 40) return '#fd7e14'; // Orange
        return '#dc3545'; // Red
    }
    
    refreshChart(chartId) {
        const chart = this.charts[chartId];
        if (!chart) return;
        
        // Show loading state
        this.showChartLoading(chartId);
        
        // Simulate data refresh (replace with actual API call)
        setTimeout(() => {
            // Update chart with new data
            this.updateChartData(chartId, this.generateMockData());
            this.hideChartLoading(chartId);
        }, 1000);
    }
    
    updateChartData(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart || !newData) return;
        
        // Update labels and data
        chart.data.labels = newData.labels || chart.data.labels;
        
        if (chart.data.datasets && chart.data.datasets[0]) {
            chart.data.datasets[0].data = newData.values || chart.data.datasets[0].data;
        }
        
        // Animate the update
        chart.update('active');
    }
    
    showChartLoading(chartId) {
        const container = document.getElementById(chartId)?.parentElement;
        if (!container) return;
        
        const loading = document.createElement('div');
        loading.className = 'chart-loading';
        loading.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Updating chart...</p>
            </div>
        `;
        loading.style.position = 'absolute';
        loading.style.top = '50%';
        loading.style.left = '50%';
        loading.style.transform = 'translate(-50%, -50%)';
        loading.style.background = 'rgba(255, 255, 255, 0.9)';
        loading.style.padding = '20px';
        loading.style.borderRadius = '8px';
        loading.style.zIndex = '1000';
        
        container.style.position = 'relative';
        container.appendChild(loading);
    }
    
    hideChartLoading(chartId) {
        const container = document.getElementById(chartId)?.parentElement;
        if (!container) return;
        
        const loading = container.querySelector('.chart-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    exportChart(chartId, format = 'png') {
        const chart = this.charts[chartId];
        if (!chart) return;
        
        const canvas = chart.canvas;
        const link = document.createElement('a');
        
        link.download = `health-analytics-${chartId}-${new Date().toISOString().split('T')[0]}.${format}`;
        link.href = canvas.toDataURL(`image/${format}`);
        link.click();
    }
    
    handleResize() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }
    
    generateMockData() {
        // Generate sample data for testing
        return {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            values: [
                Math.floor(Math.random() * 20) + 10,
                Math.floor(Math.random() * 20) + 10,
                Math.floor(Math.random() * 20) + 10,
                Math.floor(Math.random() * 20) + 10
            ]
        };
    }
    
    // Advanced analytics methods
    calculateTrends(data) {
        if (!data || data.length < 2) return { trend: 'stable', percentage: 0 };
        
        const recent = data.slice(-3); // Last 3 data points
        const older = data.slice(-6, -3); // Previous 3 data points
        
        const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
        const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
        
        const percentage = ((recentAvg - olderAvg) / olderAvg) * 100;
        
        let trend = 'stable';
        if (percentage > 5) trend = 'increasing';
        else if (percentage < -5) trend = 'decreasing';
        
        return { trend, percentage: Math.abs(percentage) };
    }
    
    generateInsights(chartData) {
        const insights = [];
        
        // Analyze activity patterns
        if (chartData.activity) {
            const total = chartData.activity.reduce((a, b) => a + b, 0);
            const max = Math.max(...chartData.activity);
            const maxIndex = chartData.activity.indexOf(max);
            
            insights.push({
                type: 'activity',
                message: `Your most active area is ${chartData.labels[maxIndex]} with ${((max / total) * 100).toFixed(1)}% of total activity.`,
                priority: 'medium'
            });
        }
        
        // Analyze engagement trends
        if (chartData.engagement) {
            const trend = this.calculateTrends(chartData.engagement);
            insights.push({
                type: 'engagement',
                message: `Your health engagement is ${trend.trend} ${trend.percentage > 0 ? `by ${trend.percentage.toFixed(1)}%` : ''}.`,
                priority: trend.trend === 'decreasing' ? 'high' : 'low'
            });
        }
        
        return insights;
    }
    
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
    }
    
    // Cleanup method
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = {};
        this.chartConfigs = {};
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.healthAnalytics = new HealthAnalytics();
});

// Export for global use
window.HealthAnalytics = HealthAnalytics;
