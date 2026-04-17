import { Target, TrendingUp, Activity, Newspaper } from 'lucide-react';
import { useEffect, useState } from 'react';
import './index.css';
import Chart from './components/Chart';
import NewsPanel from './components/NewsPanel';

function App() {
  const [signal, setSignal] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/signal/CJ.TO')
      .then(res => res.json())
      .then(json => setSignal(json))
      .catch(err => console.error("Could not load signals", err));
      
    // Set up a polling interval every 2 minutes for day trading
    const interval = setInterval(() => {
      fetch('http://localhost:8000/api/signal/CJ.TO')
        .then(res => res.json())
        .then(json => setSignal(json));
    }, 120000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <header className="header-area">
        <div className="brand">
          <Target color="#3b82f6" size={28} />
          <h1>Nexus Trader</h1>
          <span className="ticker-badge">TSX:CJ</span>
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px'}}>
              <div style={{width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-green)', boxShadow: '0 0 8px var(--accent-green)'}}></div>
              Live Data Stream Active
            </div>
        </div>
      </header>

      <main className="main-chart-area">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-title"><TrendingUp size={16}/> Current Price</div>
            <div className={`stat-value ${signal?.math.change_pct >= 0 ? 'value-green' : 'value-red'}`}>
              ${signal?.math.current_price?.toFixed(2) || '0.00'}
            </div>
            <div style={{fontSize: '0.8rem', color: signal?.math.change_pct >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}}>
              {signal?.math.change_pct >= 0 ? '+' : ''}{signal?.math.change_pct?.toFixed(2)}% Today
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-title"><Activity size={16}/> Volatility</div>
            <div className="stat-value">{signal?.math.volatility || 'Scanning'}</div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>Math Score: {signal?.math.score}/100</div>
          </div>
          <div className="stat-card">
            <div className="stat-title"><Newspaper size={16}/> Sentiment</div>
            <div className={`stat-value ${signal?.news?.aggregate_score > 50 ? 'value-green' : (signal?.news?.aggregate_score < 50 ? 'value-red' : '')}`}>
              {signal?.news.aggregate_score || '50'} / 100
            </div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
              {signal?.news?.aggregate_score > 50 ? 'Bullish' : (signal?.news?.aggregate_score < 50 ? 'Bearish' : 'Neutral')} News
            </div>
          </div>
          <div className="stat-card conviction-score">
            <div className="stat-title">Conviction Signal</div>
            <div className="stat-value">{signal?.conviction?.signal || 'SCANNING...'}</div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>AI Score: {signal?.conviction?.score.toFixed(1) || '0'}/100</div>
          </div>
        </div>

        <div className="glass-panel chart-container" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: '16px', fontWeight: 600, display: 'flex', justifyContent: 'space-between' }}>
            <span>Cardinal Energy Ltd. (15m Interval)</span>
          </div>
          <Chart />
        </div>
      </main>

      <aside className="glass-panel news-area">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Newspaper size={20} color="var(--accent-blue)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Live Catalyst Feed</h2>
        </div>
        <NewsPanel news={signal?.news?.articles || []} />
      </aside>
    </div>
  );
}

export default App;
