import { ExternalLink, Loader2 } from 'lucide-react';

interface NewsItem {
  id: string;
  source: string;
  title: string;
  time: string;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  link: string;
}

export default function NewsPanel({ news }: { news: NewsItem[] }) {
  if (!news || news.length === 0) {
    return (
      <div className="news-list" style={{ justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
        <Loader2 className="animate-spin text-gray-500" />
        <span style={{color: 'var(--text-secondary)', marginTop: '8px', fontSize: '14px'}}>Scanning catalyst feeds...</span>
      </div>
    );
  }

  return (
    <div className="news-list">
      {news.map(item => (
        <a key={item.id} href={item.link} target="_blank" rel="noreferrer" style={{textDecoration: 'none', color: 'inherit'}}>
          <div className="news-item">
            <div className="news-header">
              <span className="news-source">{item.source}</span>
              <span className={`sentiment-badge sentiment-${item.sentiment.toLowerCase()}`}>
                {item.sentiment.toUpperCase()}
              </span>
            </div>
            <div className="news-title">{item.title}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{item.time}</span>
              <ExternalLink size={14} color="var(--text-secondary)" />
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}
