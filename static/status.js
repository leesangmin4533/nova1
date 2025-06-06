async function refresh() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('sentiment').innerText = data.sentiment || '-';
        document.getElementById('strategy').innerText = data.strategy || '-';
        if (data.selected_strategy) {
            const prob = (data.strategy_score * 100).toFixed(2);
            document.getElementById('selected_strategy').innerText = `${data.selected_strategy} (${prob}%)`;
        } else {
            document.getElementById('selected_strategy').innerText = '-';
        }
        document.getElementById('signal').innerText = data.signal || '-';
        document.getElementById('price').innerText = (data.price !== null && data.price !== undefined) ? data.price.toFixed(2) : '-';
        document.getElementById('balance').innerText = (data.balance !== null && data.balance !== undefined) ? data.balance.toFixed(2) : '-';
        if (data.position && data.position.entry_price !== undefined) {
            const rr = (data.position.return_rate * 100).toFixed(2);
            document.getElementById('position').innerText = `${data.position.entry_price} (${rr}%)`;
        } else {
            document.getElementById('position').innerText = '-';
        }
        document.getElementById('weight').innerText = (data.weight !== undefined && data.weight !== null) ? data.weight.toFixed(2) : '-';
        document.getElementById('rsi').innerText = (data.rsi !== undefined && data.rsi !== null) ? data.rsi.toFixed(2) : '-';
        document.getElementById('bb_score').innerText = data.bb_score !== undefined ? data.bb_score : '-';
        document.getElementById('ts_score').innerText = data.ts_score !== undefined ? data.ts_score : '-';
        if (data.return_rate !== null && data.return_rate !== undefined) {
            const elem = document.getElementById('return_rate');
            const val = (data.return_rate * 100).toFixed(2);
            elem.innerText = val + '%';
            elem.classList.toggle('positive', data.return_rate > 0);
            elem.classList.toggle('negative', data.return_rate < 0);
        } else {
            document.getElementById('return_rate').innerText = '-';
        }
        document.getElementById('last_trade_time').innerText = data.last_trade_time || '-';
        if (data.cumulative_return !== null && data.cumulative_return !== undefined) {
            const elem = document.getElementById('cumulative_return');
            const val = (data.cumulative_return * 100).toFixed(2);
            elem.innerText = val + '%';
            elem.classList.toggle('positive', data.cumulative_return > 0);
            elem.classList.toggle('negative', data.cumulative_return < 0);
        } else {
            document.getElementById('cumulative_return').innerText = '-';
        }

        if (data.weights && Object.keys(data.weights).length > 0) {
            const labels = Object.keys(data.weights);
            const values = labels.map(k => data.weights[k]);
            const trace = {x: labels, y: values, type: 'bar'};
            Plotly.react('weights_chart', [trace], {margin: {t: 20}});
        }

        if (data.bid_volume !== null && data.ask_volume !== null) {
            const total = data.bid_volume + data.ask_volume;
            const ratio = total ? ((data.bid_volume - data.ask_volume) / total) : 0;
            document.getElementById('selected_strategy').title = `Orderbook score: ${ratio.toFixed(2)}`;
            document.getElementById('orderbook_ratio').innerText = ratio.toFixed(2);
            document.getElementById('orderbook_ratio').classList.toggle('positive', ratio > 0);
            document.getElementById('orderbook_ratio').classList.toggle('negative', ratio < 0);
        }

        // 📈 실시간 시세 그래프
        if (!window.priceHistory) window.priceHistory = [];
        const now = new Date();
        window.priceHistory.push({ x: now, y: data.price });
        if (window.priceHistory.length > 100) window.priceHistory.shift();

        Plotly.react('priceChart', [{
          x: window.priceHistory.map(p => p.x),
          y: window.priceHistory.map(p => p.y),
          mode: 'lines+markers',
          name: 'Price',
          line: { color: 'blue' }
        }], {
          title: '실시간 시세 차트',
          xaxis: { title: '시간' },
          yaxis: { title: '가격' }
        });

        // 🏛️ 호가창 시각화
        const bids = data.bids?.slice(0, 10).reverse() || [];
        const asks = data.asks?.slice(0, 10) || [];

        Plotly.react('orderbookChart', [
          {
            x: bids.map(b => b[1]),
            y: bids.map(b => b[0].toString()),
            orientation: 'h',
            name: '매수호가',
            type: 'bar',
            marker: { color: 'green' }
          },
          {
            x: asks.map(a => -a[1]),
            y: asks.map(a => a[0].toString()),
            orientation: 'h',
            name: '매도호가',
            type: 'bar',
            marker: { color: 'red' }
          }
        ], {
          title: '호가창 (상하 10개)',
          barmode: 'overlay',
          xaxis: { title: '거래량', zeroline: true },
          yaxis: { title: '가격', autorange: 'reversed' }
        });
    } catch (e) {
        console.error(e);
    }
}
setInterval(refresh, 1000);
refresh();

