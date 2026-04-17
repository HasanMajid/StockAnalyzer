import { Target, TrendingUp, Activity, Newspaper, Brain } from 'lucide-react';
import { useEffect, useState } from 'react';
import './index.css';
import Chart from './components/Chart';
import NewsPanel from './components/NewsPanel';

function App() {
  const [signal, setSignal] = useState<any>(null);
  const [ticker, setTicker] = useState('CJ.TO');
  const [inputValue, setInputValue] = useState('CJ.TO');

  useEffect(() => {
    // Clear old signal when switching tickers
    setSignal(null);
    fetch(`http://localhost:8000/api/signal/${ticker}`)
      .then(res => res.json())
      .then(json => setSignal(json))
      .catch(err => console.error("Could not load signals", err));
      
    const interval = setInterval(() => {
      fetch(`http://localhost:8000/api/signal/${ticker}`)
        .then(res => res.json())
        .then(json => setSignal(json));
    }, 120000);
    
    return () => clearInterval(interval);
  }, [ticker]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if(inputValue) setTicker(inputValue.toUpperCase());
  };

  return (
    <div className="app-container">
      <header className="header-area">
        <div className="brand">
          <Target color="#3b82f6" size={28} />
          <h1>Nexus Trader</h1>
          <form onSubmit={handleSearch} style={{ display: 'flex', marginLeft: '12px' }}>
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="ticker-badge"
              style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.3)', outline: 'none', width: '100px', textAlign: 'center', fontFamily: 'inherit', fontSize: '0.9rem' }}
            />
            <button type="submit" style={{ display: 'none' }}>Go</button>
          </form>
          
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', borderLeft: '1px solid var(--border-color)', paddingLeft: '20px' }}>
            <span style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-1px', lineHeight: 1 }}>
              ${signal?.math?.current_price?.toFixed(2) || '...'}
            </span>
            <span className={signal?.math?.change_pct >= 0 ? 'value-green' : 'value-red'} style={{ fontSize: '1.1rem', fontWeight: 600 }}>
              {signal?.math?.change_pct >= 0 ? '+' : ''}{signal?.math?.change_pct?.toFixed(2) || '0.00'}%
            </span>
          </div>
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
            <div className="stat-title"><TrendingUp size={16}/> Math Score</div>
            <div className="stat-value">{signal?.math.score || '...'}</div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
               {signal?.math.volatility || 'Scanning'} Volatility
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-title"><Newspaper size={16}/> VADER Sentiment</div>
            <div className={`stat-value ${signal?.news?.vader_score > 50 ? 'value-green' : (signal?.news?.vader_score < 50 ? 'value-red' : '')}`}>
              {signal?.news.vader_score || '50'}
            </div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>Rule-based Engine</div>
          </div>
          <div className="stat-card">
            <div className="stat-title"><Brain size={16}/> Gemini LLM Score</div>
            <div className={`stat-value ${typeof signal?.news?.ai_score === 'number' && signal?.news?.ai_score > 50 ? 'value-green' : (typeof signal?.news?.ai_score === 'number' && signal?.news?.ai_score < 50 ? 'value-red' : '')}`} style={typeof signal?.news?.ai_score === 'string' ? {fontSize: '1rem', color: '#f59e0b'} : {}}>
              {signal?.news?.ai_score || '...'}
            </div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
              AI Contextual Analysis
            </div>
          </div>
          <div className="stat-card conviction-score">
            <div className="stat-title">Conviction Signal</div>
            <div className="stat-value">{signal?.conviction?.signal || 'SCANNING...'}</div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>Score: {signal?.conviction?.score.toFixed(1) || '0'}/100</div>
          </div>
        </div>
        
        {signal?.news?.ai_reasoning && (
          <div style={{ width: '100%', padding: '16px', background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '12px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <Brain size={20} color="#3b82f6" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <span style={{ fontWeight: 600, color: '#60a5fa', marginRight: '8px' }}>Active AI Thesis:</span>
              <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '0.95rem' }}>{signal.news.ai_reasoning}</span>
            </div>
          </div>
        )}

        <div className="glass-panel chart-container" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: '16px', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{ticker} Interactive Chart (15m Interval)</span>
          </div>
          <Chart ticker={ticker} />
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
