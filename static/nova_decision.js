async function fetchDecision() {
    try {
        const res = await fetch('/api/decision');
        const data = await res.json();
        updateUI(data);
    } catch(e) {
        console.error(e);
    }
}

function updateUI(data) {
    const emo = document.getElementById('marketEmotion');
    emo.textContent = `${data.emotion} ${data.emotion_score ?? ''}`.trim();

    const cmp = document.getElementById('humanVsNova');
    cmp.textContent = `인간 예상: ${data.human_judgement} / NOVA: ${data.nova_judgement}`;

    const score = document.getElementById('score');
    score.textContent = `판단력: ${data.judgement_score ?? '-'}`;

    const history = document.getElementById('history');
    history.innerHTML = (data.history || []).map(h => `<div>${h}</div>`).join('') || '-';

    const strategy = document.getElementById('strategy');
    strategy.innerHTML = (data.strategy_updates || []).map(s => `<div>${s}</div>`).join('') || '-';

    if(data.nova_judgement) {
        score.classList.toggle('hold', data.nova_judgement === 'HOLD');
        score.classList.toggle('sell', data.nova_judgement === 'SELL');
    }
}

fetchDecision();
setInterval(fetchDecision, 60000);
