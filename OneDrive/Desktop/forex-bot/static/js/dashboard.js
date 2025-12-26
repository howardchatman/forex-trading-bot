// Dashboard JavaScript for Real-time Updates

class TradingDashboard {
    constructor() {
        this.updateInterval = 3000; // Update every 3 seconds
        this.intervalId = null;
        this.init();
    }

    init() {
        // Initial load
        this.updateDashboard();

        // Setup event listeners
        this.setupEventListeners();

        // Start auto-refresh
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Trading toggle
        const tradingToggle = document.getElementById('trading-toggle');
        if (tradingToggle) {
            tradingToggle.addEventListener('change', (e) => {
                this.toggleTrading(e.target.checked);
            });
        }

        // Manual trade form
        const tradeForm = document.getElementById('manual-trade-form');
        if (tradeForm) {
            tradeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitManualTrade();
            });
        }

        // Action dropdown
        const actionSelect = document.getElementById('trade-action');
        if (actionSelect) {
            actionSelect.addEventListener('change', (e) => {
                this.toggleTradeParams(e.target.value);
            });
        }
    }

    toggleTradeParams(action) {
        const params = document.querySelectorAll('.trade-params');
        if (action === 'close') {
            params.forEach(p => p.style.display = 'none');
        } else {
            params.forEach(p => p.style.display = 'block');
        }
    }

    async updateDashboard() {
        try {
            const response = await fetch('/api/dashboard');
            const data = await response.json();

            if (data.error) {
                console.error('Dashboard error:', data.error);
                return;
            }

            this.updateAccount(data.account);
            this.updateRisk(data.risk);
            this.updatePositions(data.positions);
            this.updateSignals(data.recent_signals);
            this.updateTradeHistory(data.trade_history);
            this.updateLastUpdate();

        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    updateAccount(account) {
        // Update environment badge
        const envBadge = document.getElementById('environment-badge');
        if (envBadge) {
            envBadge.textContent = account.environment.toUpperCase();
            envBadge.className = 'environment-badge';
            if (account.environment === 'live') {
                envBadge.classList.add('live');
            }
        }

        // Update account values
        this.updateElement('account-balance', this.formatCurrency(account.balance));
        this.updateElement('account-nav', this.formatCurrency(account.nav));
        this.updateElement('margin-used', this.formatCurrency(account.margin_used));
        this.updateElement('margin-available', this.formatCurrency(account.margin_available));

        // Update unrealized P/L
        const plElement = document.getElementById('unrealized-pl');
        if (plElement) {
            plElement.textContent = this.formatCurrency(account.unrealized_pl);
            const card = plElement.closest('.stat-card');
            card.classList.remove('positive', 'negative');
            if (account.unrealized_pl > 0) {
                card.classList.add('positive');
            } else if (account.unrealized_pl < 0) {
                card.classList.add('negative');
            }
        }
    }

    updateRisk(risk) {
        // Trading status
        const statusText = document.getElementById('trading-status-text');
        const toggle = document.getElementById('trading-toggle');
        if (statusText && toggle) {
            statusText.textContent = risk.trading_enabled ? 'Trading Active' : 'Trading Disabled';
            toggle.checked = risk.trading_enabled;
        }

        // Daily P/L
        this.updateElement('daily-pnl', this.formatCurrency(risk.daily_pnl));
        this.updateElement('daily-percent', risk.daily_loss_percent.toFixed(2) + '%');
        this.updateElement('daily-limit', risk.daily_limit.toFixed(0) + '%');

        const dailyProgress = document.getElementById('daily-progress');
        if (dailyProgress) {
            const percent = Math.min((Math.abs(risk.daily_loss_percent) / risk.daily_limit) * 100, 100);
            dailyProgress.style.width = percent + '%';
            dailyProgress.className = 'progress-fill';
            if (percent > 75) dailyProgress.classList.add('warning');
        }

        // Weekly P/L
        this.updateElement('weekly-pnl', this.formatCurrency(risk.weekly_pnl));
        this.updateElement('weekly-percent', risk.weekly_loss_percent.toFixed(2) + '%');
        this.updateElement('weekly-limit', risk.weekly_limit.toFixed(0) + '%');

        const weeklyProgress = document.getElementById('weekly-progress');
        if (weeklyProgress) {
            const percent = Math.min((Math.abs(risk.weekly_loss_percent) / risk.weekly_limit) * 100, 100);
            weeklyProgress.style.width = percent + '%';
            weeklyProgress.className = 'progress-fill';
            if (percent > 75) weeklyProgress.classList.add('warning');
        }

        // Positions
        this.updateElement('positions-count', `${risk.current_positions}/${risk.max_positions}`);
        this.updateElement('risk-per-trade', risk.risk_per_trade.toFixed(1) + '%');

        const positionsProgress = document.getElementById('positions-progress');
        if (positionsProgress) {
            const percent = (risk.current_positions / risk.max_positions) * 100;
            positionsProgress.style.width = percent + '%';
        }
    }

    updatePositions(positions) {
        const tbody = document.getElementById('positions-body');
        if (!tbody) return;

        if (!positions || positions.length === 0) {
            tbody.innerHTML = '<tr class="no-data"><td colspan="6">No open positions</td></tr>';
            return;
        }

        tbody.innerHTML = positions.map(pos => `
            <tr>
                <td><strong>${pos.instrument}</strong></td>
                <td><span class="badge ${pos.side.toLowerCase()}">${pos.side}</span></td>
                <td>${this.formatNumber(pos.units)}</td>
                <td>${pos.avg_price.toFixed(5)}</td>
                <td class="${pos.pl >= 0 ? 'positive' : 'negative'}" style="font-weight: 600;">
                    ${this.formatCurrency(pos.pl)}
                </td>
                <td>
                    <button class="btn btn-danger" onclick="dashboard.closePosition('${pos.instrument}')">
                        <i class="fas fa-times"></i> Close
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateSignals(signals) {
        const container = document.getElementById('signals-list');
        if (!container) return;

        if (!signals || signals.length === 0) {
            container.innerHTML = '<div class="no-data">No recent signals</div>';
            return;
        }

        container.innerHTML = signals.map(signal => {
            const time = this.formatTime(signal.timestamp);
            const action = signal.action.toUpperCase();

            return `
                <div class="signal-item ${signal.action}">
                    <div class="signal-header">
                        <div class="signal-instrument">
                            <span class="badge ${signal.action}">${action}</span>
                            ${signal.instrument}
                        </div>
                        <div class="signal-time">${time}</div>
                    </div>
                    <div class="signal-details">
                        ${signal.stop_loss ? `SL: ${signal.stop_loss} | ` : ''}
                        ${signal.take_profit ? `TP: ${signal.take_profit}` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    updateTradeHistory(history) {
        const tbody = document.getElementById('history-body');
        if (!tbody) return;

        if (!history || history.length === 0) {
            tbody.innerHTML = '<tr class="no-data"><td colspan="8">No trade history</td></tr>';
            return;
        }

        tbody.innerHTML = history.map(trade => `
            <tr>
                <td>${this.formatTime(trade.timestamp)}</td>
                <td><span class="badge ${trade.action}">${trade.action.toUpperCase()}</span></td>
                <td><strong>${trade.instrument}</strong></td>
                <td>${trade.units ? this.formatNumber(trade.units) : '-'}</td>
                <td>${trade.entry_price ? trade.entry_price.toFixed(5) : '-'}</td>
                <td>${trade.stop_loss ? trade.stop_loss.toFixed(5) : '-'}</td>
                <td>${trade.take_profit ? trade.take_profit.toFixed(5) : '-'}</td>
                <td>${trade.status}</td>
            </tr>
        `).join('');
    }

    async toggleTrading(enabled) {
        try {
            const endpoint = enabled ? '/api/enable-trading' : '/api/disable-trading';
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                this.showNotification(
                    `Trading ${enabled ? 'enabled' : 'disabled'}`,
                    'success'
                );
            }
        } catch (error) {
            console.error('Error toggling trading:', error);
            this.showNotification('Error toggling trading', 'error');
        }
    }

    async closePosition(instrument) {
        if (!confirm(`Are you sure you want to close ${instrument}?`)) {
            return;
        }

        try {
            const response = await fetch('/api/close-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ instrument })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showNotification(`Position closed: ${instrument}`, 'success');
                this.updateDashboard();
            } else {
                this.showNotification(data.message || 'Error closing position', 'error');
            }
        } catch (error) {
            console.error('Error closing position:', error);
            this.showNotification('Error closing position', 'error');
        }
    }

    async submitManualTrade() {
        const action = document.getElementById('trade-action').value;
        const instrument = document.getElementById('trade-instrument').value;
        const sl = document.getElementById('trade-sl').value;
        const tp = document.getElementById('trade-tp').value;

        const signal = {
            action,
            instrument,
            sl_pips: sl ? parseInt(sl) : undefined,
            tp_pips: tp ? parseInt(tp) : undefined
        };

        try {
            const response = await fetch('/api/manual-trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signal)
            });

            const data = await response.json();
            const resultDiv = document.getElementById('trade-result');

            if (data.status === 'success') {
                resultDiv.className = 'trade-result success';
                resultDiv.textContent = `✓ Trade executed: ${action.toUpperCase()} ${instrument}`;
                this.updateDashboard();
            } else {
                resultDiv.className = 'trade-result error';
                resultDiv.textContent = `✗ ${data.message || 'Trade failed'}`;
            }

            // Hide result after 5 seconds
            setTimeout(() => {
                resultDiv.style.display = 'none';
            }, 5000);

        } catch (error) {
            console.error('Error submitting trade:', error);
            const resultDiv = document.getElementById('trade-result');
            resultDiv.className = 'trade-result error';
            resultDiv.textContent = '✗ Error submitting trade';
        }
    }

    showNotification(message, type) {
        // Simple notification - could be enhanced with a toast library
        alert(message);
    }

    updateLastUpdate() {
        const element = document.getElementById('last-update');
        if (element) {
            const now = new Date();
            element.textContent = now.toLocaleTimeString();
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }

    formatTime(timestamp) {
        if (!timestamp) return '--';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    startAutoRefresh() {
        this.intervalId = setInterval(() => {
            this.updateDashboard();
        }, this.updateInterval);
    }

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new TradingDashboard();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.stopAutoRefresh();
    }
});
