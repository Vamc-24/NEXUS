const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    const dashboardContent = document.getElementById('dashboard-content');
    const refreshBtn = document.getElementById('refresh-btn');

    async function fetchInsights() {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Refreshing...';

        try {
            const response = await fetch(`${API_URL}/results`);
            const data = await response.json();

            if (data.clusters && data.clusters.length > 0) {
                // Sort clusters by count (descending)
                data.clusters.sort((a, b) => b.count - a.count);
                renderClusters(data.clusters);
            } else {
                dashboardContent.innerHTML = '<p>No feedback clusters found. Try submitting some feedback and processing it.</p>';
            }
        } catch (error) {
            console.error('Error fetching insights:', error);
            dashboardContent.innerHTML = '<p>Error loading data. Is the backend running?</p>';
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Insights';
        }
    }

    async function triggerProcessing() {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Processing...';
        try {
            await fetch(`${API_URL}/process`, { method: 'POST' });
            // Wait a bit for processing to complete (simulated)
            setTimeout(fetchInsights, 1000);
        } catch (error) {
            console.error('Error triggering processing:', error);
            alert('Failed to trigger processing.');
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Insights';
        }
    }

    function renderClusters(clusters) {
        dashboardContent.innerHTML = '';
        clusters.forEach(cluster => {
            const card = document.createElement('div');
            card.className = 'cluster-card';

            // Format solutions list
            const solutionsHtml = cluster.solutions.map(sol => {
                if (typeof sol === 'object') {
                    return `
                    <li class="solution-item">
                        <div class="solution-text"><strong>Action:</strong> ${sol.solution}</div>
                        <div class="solution-details" style="font-size: 0.9em; color: #555; margin-top: 4px;">
                            <span class="cost">💰 <strong>Est. Cost:</strong> ${sol.estimated_cost}</span>
                            <span class="tools" style="margin-left: 10px;">🛠️ <strong>Tools:</strong> ${sol.required_tools}</span>
                        </div>
                    </li>`;
                }
                return `<li>${sol}</li>`;
            }).join('');

            card.innerHTML = `
                <h3>Theme: ${cluster.theme || 'Untitled Cluster'}</h3>
                <p><strong>Count:</strong> ${cluster.count} comments</p>
                <div class="problem-statement">
                    <strong>Problem Statement:</strong><br>
                    ${cluster.problem_statement}
                </div>
                <div class="solution-section">
                    <h4>Recommendation:</h4>
                    <ul class="solution-list">
                        ${solutionsHtml}
                    </ul>
                </div>
            `;
            dashboardContent.appendChild(card);
        });
    }

    refreshBtn.addEventListener('click', triggerProcessing); // Main action is to trigger refresh/process logic

    // Initial load
    fetchInsights();
});
