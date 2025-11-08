// Advanced Dashboard JavaScript with Animations and Real-time Updates

class SolarDashboard {
    constructor() {
        this.chart = null;
        this.isLiveView = true;
        this.initializeApp();
    }

    initializeApp() {
        this.setCurrentDateTime();
        this.initializeSliders();
        this.initializeChart();
        this.setupEventListeners();
        this.loadInitialData();
    }

    setCurrentDateTime() {
        const now = new Date();
        
        // Set hour slider
        document.getElementById('hour').value = now.getHours();
        this.updateHourDisplay(now.getHours());
        
        // Set day select
        this.populateDaySelect();
        document.getElementById('day').value = now.getDate();
        
        // Set month select (already set in HTML)
    }

    populateDaySelect() {
        const daySelect = document.getElementById('day');
        daySelect.innerHTML = '';
        
        for (let day = 1; day <= 31; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day;
            daySelect.appendChild(option);
        }
    }

    initializeSliders() {
        // Irradiation slider
        const irradiationSlider = document.getElementById('irradiation');
        irradiationSlider.addEventListener('input', (e) => {
            document.getElementById('irradiationValue').textContent = `${e.target.value} kW/m²`;
        });

        // Ambient temperature slider
        const ambientTempSlider = document.getElementById('ambient_temperature');
        ambientTempSlider.addEventListener('input', (e) => {
            document.getElementById('ambientTempValue').textContent = `${e.target.value}°C`;
        });

        // Module temperature slider
        const moduleTempSlider = document.getElementById('module_temperature');
        moduleTempSlider.addEventListener('input', (e) => {
            document.getElementById('moduleTempValue').textContent = `${e.target.value}°C`;
        });

        // Hour slider
        const hourSlider = document.getElementById('hour');
        hourSlider.addEventListener('input', (e) => {
            this.updateHourDisplay(e.target.value);
        });
    }

    updateHourDisplay(hour) {
        const formattedHour = hour.toString().padStart(2, '0');
        document.getElementById('hourValue').textContent = `${formattedHour}:00`;
    }

    initializeChart() {
        const ctx = document.getElementById('powerChart').getContext('2d');
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Actual AC Power',
                        data: [],
                        borderColor: 'rgb(34, 197, 94)',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: 'rgb(34, 197, 94)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Predicted AC Power',
                        data: [],
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: 'rgb(59, 130, 246)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#e2e8f0',
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 12,
                        displayColors: true,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} kW`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxTicksLimit: 10
                        },
                        title: {
                            display: true,
                            text: 'Time',
                            color: '#94a3b8',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value + ' kW';
                            }
                        },
                        title: {
                            display: true,
                            text: 'AC Power (kW)',
                            color: '#94a3b8',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    setupEventListeners() {
        // Prediction form
        document.getElementById('predictionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.makePrediction();
        });

        // Chart toggle
        document.getElementById('chartToggle').addEventListener('click', () => {
            this.toggleChartView();
        });

        // Auto-update chart every 30 seconds
        setInterval(() => {
            this.loadChartData();
        }, 30000);
    }

    async loadInitialData() {
        await this.loadChartData();
        await this.loadModelMetrics();
    }

    async loadChartData() {
        try {
            const response = await fetch('/series');
            const data = await response.json();
            
            this.updateChart(data);
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showFallbackData();
        }
    }

    async loadModelMetrics() {
        // Simulate loading model metrics
        document.getElementById('maeValue').textContent = '16.37';
        document.getElementById('rmseValue').textContent = '45.67';
        document.getElementById('r2Value').textContent = '0.9865';
    }

    updateChart(data) {
        if (!this.chart) return;

        this.chart.data.labels = data.timestamps.map((ts, index) => {
            if (index % 20 === 0) {
                return new Date(ts).toLocaleTimeString();
            }
            return '';
        });
        
        this.chart.data.datasets[0].data = data.actual;
        this.chart.data.datasets[1].data = data.predicted;
        
        this.chart.update('none');
    }

    showFallbackData() {
        const timestamps = [];
        const actual = [];
        const predicted = [];
        
        const now = new Date();
        for (let i = 0; i < 200; i++) {
            const time = new Date(now.getTime() - (199 - i) * 60000);
            timestamps.push(time.toISOString());
            
            const base = 200 + Math.sin(i * 0.1) * 50;
            actual.push(base + Math.random() * 20);
            predicted.push(base + Math.random() * 15 - 7.5);
        }
        
        this.updateChart({ timestamps, actual, predicted });
    }

    toggleChartView() {
        this.isLiveView = !this.isLiveView;
        const button = document.getElementById('chartToggle');
        
        if (this.isLiveView) {
            button.innerHTML = '<i class="fas fa-chart-line mr-1"></i>Live View';
            this.loadChartData();
        } else {
            button.innerHTML = '<i class="fas fa-chart-bar mr-1"></i>Historical View';
            this.showHistoricalView();
        }
    }

    showHistoricalView() {
        // Simulate historical data
        const timestamps = [];
        const actual = [];
        const predicted = [];
        
        for (let i = 0; i < 200; i++) {
            const date = new Date();
            date.setDate(date.getDate() - 199 + i);
            timestamps.push(date.toLocaleDateString());
            
            const seasonal = Math.sin((i / 200) * 2 * Math.PI) * 30;
            const base = 150 + seasonal;
            actual.push(base + Math.random() * 25);
            predicted.push(base + Math.random() * 20 - 10);
        }
        
        this.updateChart({ timestamps, actual, predicted });
    }

    async makePrediction() {
        const form = document.getElementById('predictionForm');
        const formData = new FormData(form);
        const resultDiv = document.getElementById('result');
        
        // Show loading state
        resultDiv.classList.add('hidden');
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.showPredictionResult(data);
            
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    showPredictionResult(data) {
        const resultDiv = document.getElementById('result');
        const predictionValue = document.getElementById('predictionValue');
        const modelInfo = document.getElementById('modelInfo');
        const activeModel = document.getElementById('activeModel');
        
        predictionValue.textContent = `${data.prediction} kW`;
        modelInfo.textContent = `Using ${data.model_used} AI Model`;
        activeModel.textContent = data.model_used;
        
        // Add animation
        resultDiv.classList.remove('hidden');
        resultDiv.classList.add('animate__animated', 'animate__fadeInUp');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            resultDiv.classList.remove('animate__animated', 'animate__fadeInUp');
        }, 1000);
        
        // Add to chart
        this.addPredictionToChart(data.prediction);
    }

    addPredictionToChart(prediction) {
        if (!this.chart) return;
        
        // Add the prediction as a new point in the chart
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        this.chart.data.labels.push(timestamp);
        this.chart.data.datasets[1].data.push(prediction);
        
        // Keep only last 50 points for performance
        if (this.chart.data.labels.length > 50) {
            this.chart.data.labels.shift();
            this.chart.data.datasets[1].data.shift();
        }
        
        this.chart.update();
    }

    showError(message) {
        const resultDiv = document.getElementById('result');
        const predictionValue = document.getElementById('predictionValue');
        const modelInfo = document.getElementById('modelInfo');
        
        predictionValue.textContent = 'Error';
        modelInfo.textContent = message;
        
        resultDiv.classList.remove('hidden');
        resultDiv.querySelector('div').classList.remove('bg-gradient-to-r', 'from-green-500/20', 'to-emerald-500/20', 'border-green-400/30');
        resultDiv.querySelector('div').classList.add('bg-gradient-to-r', 'from-red-500/20', 'to-pink-500/20', 'border-red-400/30');
        
        resultDiv.classList.add('animate__animated', 'animate__shakeX');
        
        setTimeout(() => {
            resultDiv.classList.remove('animate__animated', 'animate__shakeX');
        }, 1000);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    new SolarDashboard();
});
document.addEventListener('mousemove', (e) => {
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});