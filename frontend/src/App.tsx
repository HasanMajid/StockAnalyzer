import { Target, TrendingUp, Newspaper, Brain } from 'lucide-react';
import { useEffect, useState } from 'react';
import './index.css';
import Chart from './components/Chart';
import NewsPanel from './components/NewsPanel';

function App() {
  const urlParams = new URLSearchParams(window.location.search);
  const initialTicker = urlParams.get('ticker')?.toUpperCase() || 'CJ.TO';
  const initialMode = (urlParams.get('mode') as 'swing' | 'day') || 'day';
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [signal, setSignal] = useState<any>(null);
  const [ticker, setTicker] = useState(initialTicker);
  const [inputValue, setInputValue] = useState(initialTicker);
  const [macroInput, setMacroInput] = useState('');
  const [activeMacro, setActiveMacro] = useState('');
  const [tradingMode, setTradingMode] = useState<'swing' | 'day'>(initialMode);

  // Sync URL with State
  useEffect(() => {
    const currentParams = new URLSearchParams(window.location.search);
    currentParams.set('ticker', ticker);
    currentParams.set('mode', tradingMode);
    window.history.replaceState({}, '', `${window.location.pathname}?${currentParams.toString()}`);
  }, [ticker, tradingMode]);

  // Fetch Macro Drivers when Ticker changes
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/macro-drivers/${ticker}`)
      .then(res => res.json())
      .then(json => {
         if(json.drivers) {
             setMacroInput(json.drivers);
             setActiveMacro(json.drivers);
         }
      })
      .catch(err => console.error("Could not fetch macro drivers", err));
  }, [ticker]);

  useEffect(() => {
    // Clear old signal when switching tickers, macros, or modes
    setSignal(null);
    const queryParams = new URLSearchParams({ trading_mode: tradingMode });
    if (activeMacro) queryParams.append('macro', activeMacro);
    
    fetch(`${API_BASE_URL}/api/signal/${ticker}?${queryParams.toString()}`)
      .then(res => res.json())
      .then(json => setSignal(json))
      .catch(err => console.error("Could not load signals", err));
      
    const interval = setInterval(() => {
      fetch(`${API_BASE_URL}/api/signal/${ticker}?${queryParams.toString()}`)
        .then(res => res.json())
        .then(json => setSignal(json));
    }, 60000);
    
    return () => clearInterval(interval);
  }, [ticker, activeMacro, tradingMode]);

  // Dynamic Browser Tab Title
  useEffect(() => {
    if (signal?.math?.current_price && signal?.conviction?.signal) {
      document.title = `[${signal.conviction.signal}] $${signal.math.current_price.toFixed(2)} - ${ticker}`;
    } else {
      document.title = `Scanning ${ticker}... | Nexus Trader`;
    }
  }, [signal, ticker]);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue) {
       // Only execute if it's actually a new ticker
       if (inputValue.toUpperCase() !== ticker) {
           setActiveMacro(''); // Blank it out so we don't fetch with old macros
           setTicker(inputValue.toUpperCase());
       } else {
           // If they are just manually updating the macro field for the same ticker
           setActiveMacro(macroInput);
       }
    }
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
          
          <form onSubmit={handleSearch} style={{ display: 'flex', marginLeft: '12px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginRight: '8px', fontWeight: 600 }}>MACRO RADAR:</span>
            <input 
              type="text" 
              value={macroInput}
              onChange={(e) => setMacroInput(e.target.value)}
              className="ticker-badge"
              placeholder="Auto-generating..."
              style={{ background: 'transparent', color: '#94a3b8', border: '1px dashed rgba(148, 163, 184, 0.4)', outline: 'none', width: '220px', padding: '4px 8px', fontSize: '0.8rem', fontWeight: 500 }}
            />
            <button type="submit" style={{ display: 'none' }}>Update</button>
          </form>

          <div style={{ display: 'flex', marginLeft: 'auto', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>MODE:</span>
            <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '6px', padding: '2px', border: '1px solid rgba(148, 163, 184, 0.2)' }}>
              <button 
                onClick={() => setTradingMode('swing')}
                style={{ background: tradingMode === 'swing' ? 'rgba(59, 130, 246, 0.2)' : 'transparent', color: tradingMode === 'swing' ? '#3b82f6' : '#94a3b8', border: 'none', padding: '4px 12px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
              >
                SWING
              </button>
              <button 
                onClick={() => setTradingMode('day')}
                style={{ background: tradingMode === 'day' ? 'rgba(245, 158, 11, 0.2)' : 'transparent', color: tradingMode === 'day' ? '#f59e0b' : '#94a3b8', border: 'none', padding: '4px 12px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
              >
                DAY
              </button>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', borderLeft: '1px solid var(--border-color)', paddingLeft: '20px', marginLeft: '20px' }}>
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
          <div className="stat-card" style={signal?.math?.pattern && signal?.math?.pattern !== "None" ? { border: '1px solid rgba(245, 158, 11, 0.4)', background: 'rgba(245, 158, 11, 0.05)' } : {}}>
            <div className="stat-title"><TrendingUp size={16}/> Math Score</div>
            <div className="stat-value">{signal?.math?.score || '...'}</div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
               {signal?.math?.volatility || 'Scanning'} Volatility
            </div>
            {signal?.math?.pattern && signal?.math?.pattern !== "None" && (
              <div style={{ marginTop: '8px', padding: '4px 8px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '4px', fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600, textAlign: 'center', border: '1px dashed rgba(245, 158, 11, 0.3)' }}>
                🚨 {signal.math.pattern} Detected
              </div>
            )}
          </div>
          <div className="stat-card">
            <div className="stat-title"><Newspaper size={16}/> VADER Sentiment</div>
            <div className={`stat-value ${signal?.news?.vader_score > 50 ? 'value-green' : (signal?.news?.vader_score < 50 ? 'value-red' : '')}`}>
              {signal?.news.vader_score || '50'}
            </div>
            <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>Rule-based Engine</div>
          </div>
          <div className="stat-card">
            <div className="stat-title"><Brain size={16}/> LLM Score</div>
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
        <NewsPanel news={signal?.news?.articles || []} isScanning={!signal} />
      </aside>
    </div>
  );
}

export default App;
