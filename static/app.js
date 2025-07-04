document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const pdfFileInput = document.getElementById('pdf-file');
    const extractedTextSection = document.getElementById('extracted-text-section');
    const extractedTextArea = document.getElementById('extracted-text');
    const chunkingSection = document.getElementById('chunking-section');
    const strategySelect = document.getElementById('strategy');
    const strategyExplanation = document.getElementById('strategy-explanation');
    const paramsDiv = document.getElementById('params');
    const chunkBtn = document.getElementById('chunk-btn');
    const chunksSection = document.getElementById('chunks-section');
    const chunksDiv = document.getElementById('chunks');

    let strategies = {};
    let currentText = '';

    // Fetch strategies
    fetch('/api/strategies').then(r => r.json()).then(data => {
        strategies = data;
        for (const key in strategies) {
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = strategies[key].name;
            strategySelect.appendChild(opt);
        }
        updateStrategyUI();
    });

    strategySelect.addEventListener('change', updateStrategyUI);

    function updateStrategyUI() {
        const strat = strategies[strategySelect.value];
        strategyExplanation.textContent = strat ? ' - ' + strat.explanation : '';
        paramsDiv.innerHTML = '';
        if (strat && strat.params) {
            for (const param in strat.params) {
                const label = document.createElement('label');
                label.textContent = param.charAt(0).toUpperCase() + param.slice(1) + ':';
                let input;
                if (param === 'pattern') {
                    input = document.createElement('input');
                    input.type = 'text';
                    input.name = param;
                    input.value = strat.params[param];
                } else {
                    input = document.createElement('input');
                    input.type = 'number';
                    input.name = param;
                    input.value = strat.params[param];
                    input.min = 0;
                }
                paramsDiv.appendChild(label);
                paramsDiv.appendChild(input);
            }
        }
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const file = pdfFileInput.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.text) {
                currentText = data.text;
                extractedTextArea.value = data.text.slice(0, 5000); // show first 5000 chars
                extractedTextSection.style.display = '';
                chunkingSection.style.display = '';
                chunksSection.style.display = 'none';
            } else {
                alert('Failed to extract text from PDF.');
            }
        });
    });

    chunkBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const strategy = strategySelect.value;
        const params = {};
        paramsDiv.querySelectorAll('input').forEach(input => {
            params[input.name] = input.value;
        });
        const formData = new FormData();
        formData.append('text', currentText);
        formData.append('strategy', strategy);
        for (const k in params) formData.append(k, params[k]);
        fetch('/api/chunk', {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.chunks) {
                chunksDiv.innerHTML = '';
                data.chunks.forEach((chunk, idx) => {
                    const div = document.createElement('div');
                    div.className = 'chunk';
                    div.innerHTML = `<div class="chunk-meta">Chunk ${idx+1} | Size: ${chunk.size} | Overlap: ${chunk.overlap}</div><div>${chunk.text.slice(0, 400)}${chunk.text.length>400?'...':''}</div>`;
                    chunksDiv.appendChild(div);
                });
                chunksSection.style.display = '';
            } else {
                alert('Chunking failed.');
            }
        });
    });
});
