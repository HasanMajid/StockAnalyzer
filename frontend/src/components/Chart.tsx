import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { Loader2 } from 'lucide-react';

export default function Chart({ ticker }: { ticker: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    
    const fetchChartData = () => {
      fetch(`http://localhost:8000/api/chart/${ticker}`)
        .then(res => res.json())
        .then(json => {
          if (json.data && json.data.length > 0) {
            setData(json.data);
          }
          setLoading(false);
        })
        .catch(err => {
          console.error("Failed to fetch chart data", err);
          setLoading(false);
        });
    };
    
    // Initial fetch
    fetchChartData();
    
    // Poll every 60 seconds for live chart updates
    const interval = setInterval(fetchChartData, 60000);
    return () => clearInterval(interval);
  }, [ticker]);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
      },
      width: chartContainerRef.current.clientWidth > 0 ? chartContainerRef.current.clientWidth : 600,
      height: chartContainerRef.current.clientHeight > 0 ? chartContainerRef.current.clientHeight : 400,
      autoSize: true,
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candlestickSeries.setData(data);
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ 
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  if (loading) {
     return <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%'}}><Loader2 className="animate-spin text-gray-400" /></div>
  }

  return <div ref={chartContainerRef} style={{ flexGrow: 1, height: '100%', minHeight: '400px' }} />;
}
