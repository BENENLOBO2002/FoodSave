

// Chart references
let consumptionChart = null;
let savingsChart = null;


// HTML elements
const periodSelector = document.getElementById('periodSelector');

const wasteRateElement = document.getElementById('wasteRate');
const consumedCountElement = document.getElementById('consumedCount');
const wastedCountElement = document.getElementById('wastedCount');
const consumedProgressElement = document.getElementById('consumedProgress');




async function loadConsumptionAnalytics() {

    const period = periodSelector.value;

    try {

        const response = await fetch(
            `/api/analytics/consumption/?period=${period}`
        );

        if (!response.ok) {
            throw new Error('Unable to retrieve consumption analytics');
        }

        const data = await response.json();

        updateConsumptionChart(data);

        updateWasteOverview(data);

    } catch (error) {

        console.error('Consumption analytics error:', error);

    }

}


function updateConsumptionChart(data) {

    const canvas = document.getElementById('consumptionChart');

    if (consumptionChart) {
        consumptionChart.destroy();
    }

    consumptionChart = new Chart(canvas, {

        type: 'doughnut',

        data: {

            labels: ['Consumed activities', 'Wasted activities'],

            datasets: [{

                data: [
                    data.consumed,
                    data.wasted
                ],

                backgroundColor: [
                    '#48a76b',
                    '#e47a73'
                ],

                borderWidth: 0,

                hoverOffset: 8

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: '65%',

            plugins: {

                legend: {
                    position: 'bottom'
                },

                tooltip: {

                    callbacks: {

                        label: function(context) {

                            return `${context.label}: ${context.raw} records`;

                        }

                    }

                }

            }

        }

    });

}


// Update Waste Overview
function updateWasteOverview(data) {

    const total = data.consumed + data.wasted;

    const wasteRate = total > 0
        ? (data.wasted / total) * 100
        : 0;

    const consumedRate = total > 0
        ? (data.consumed / total) * 100
        : 0;

    wasteRateElement.textContent = `${wasteRate.toFixed(1)}%`;

    consumedCountElement.textContent = data.consumed;

    wastedCountElement.textContent = data.wasted;

    consumedProgressElement.style.width = `${consumedRate}%`;

}




async function loadSavingsAnalytics() {

    try {

        const response = await fetch(
            '/api/analytics/monthly-savings/'
        );

        if (!response.ok) {
            throw new Error('Unable to retrieve savings analytics');
        }

        const data = await response.json();

        updateSavingsChart(data.monthly_data);

    } catch (error) {

        console.error('Savings analytics error:', error);

    }

}


function updateSavingsChart(monthlyData) {

    const canvas = document.getElementById('savingsChart');

    if (savingsChart) {
        savingsChart.destroy();
    }

    savingsChart = new Chart(canvas, {

        type: 'bar',

        data: {

            labels: monthlyData.map(item => item.month),

            datasets: [{

                label: 'Estimated money saved (€)',

                data: monthlyData.map(item => item.saved),

                backgroundColor: '#48a76b',

                borderRadius: 7,

                maxBarThickness: 45

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    callbacks: {

                        label: function(context) {

                            return `€${context.raw.toFixed(2)}`;

                        }

                    }

                }

            },

            scales: {

                y: {

                    beginAtZero: true,

                    title: {
                        display: true,
                        text: 'Estimated value (€)'
                    }

                },

                x: {

                    title: {
                        display: true,
                        text: 'Month'
                    }

                }

            }

        }

    });

}




// Reload consumption chart when period changes
periodSelector.addEventListener(
    'change',
    loadConsumptionAnalytics
);



document.addEventListener('DOMContentLoaded', function() {

    loadConsumptionAnalytics();

    loadSavingsAnalytics();

});