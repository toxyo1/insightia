const startBtn = document.getElementById('start-btn');
const navStartBtn = document.getElementById('nav-start-btn');
const backHomeBtn = document.getElementById('back-home-btn');
const homeScreen = document.getElementById('home-screen');
const chatScreen = document.getElementById('chat-screen');

const API_BASE_URL = 'https://data-analyst-assistant-rdc4.onrender.com';

function switchScreen(hideScreen, showScreen) {
    hideScreen.classList.remove('active');
    hideScreen.classList.add('hidden');
    showScreen.classList.remove('hidden');
    showScreen.classList.add('active');
}

startBtn.addEventListener('click', () => switchScreen(homeScreen, chatScreen));
navStartBtn.addEventListener('click', () => switchScreen(homeScreen, chatScreen));
backHomeBtn.addEventListener('click', () => switchScreen(chatScreen, homeScreen));

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileNameSpan = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');

const statLinhas = document.getElementById('stat-linhas');
const statNulos = document.getElementById('stat-nulos');
const statDuplicatas = document.getElementById('stat-duplicatas');
const statScore = document.getElementById('stat-score');
const aiReportContent = document.getElementById('ai-report-content');
const openRulesBtn = document.getElementById('open-rules-btn');

const rulesModal = document.getElementById('rules-modal');
const cancelRulesBtn = document.getElementById('cancel-rules-btn');
const confirmRulesBtn = document.getElementById('confirm-rules-btn');
const confirmRulesBtnOriginalHTML = confirmRulesBtn.innerHTML;
const ruleDuplicatas = document.getElementById('rule-duplicatas');
const ruleNulos = document.getElementById('rule-nulos');
const ruleColunas = document.getElementById('rule-colunas');

let currentFile = null;

openRulesBtn.addEventListener('click', () => {
    if (!currentFile || openRulesBtn.disabled) return;
    rulesModal.classList.remove('hidden');
});

cancelRulesBtn.addEventListener('click', () => {
    rulesModal.classList.add('hidden');
});

rulesModal.addEventListener('click', (e) => {
    if (e.target === rulesModal) rulesModal.classList.add('hidden');
});

confirmRulesBtn.addEventListener('click', () => {
    const regras = {
        duplicatas: ruleDuplicatas.checked,
        nulos: ruleNulos.checked,
        colunas: ruleColunas.checked
    };
    downloadCleanedFile(currentFile, regras);
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}, false);

fileInput.addEventListener('change', function () {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            currentFile = file;
            fileNameSpan.textContent = file.name;
            dropZone.classList.add('hidden');
            fileInfo.classList.remove('hidden');
            analyzeFile(file);
        } else {
            alert('Formato inválido. Por favor, envie apenas arquivos .CSV.');
        }
    }
}

removeFileBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    dropZone.classList.remove('hidden');
    resetUI();
});

function resetUI() {
    statLinhas.textContent = '--';
    statNulos.textContent = '--';
    statDuplicatas.textContent = '--';
    statScore.textContent = '--/100';
    aiReportContent.innerHTML = '<p class="placeholder-text">Aguardando o envio do arquivo para gerar o relatório de qualidade...</p>';
    openRulesBtn.disabled = true;
    rulesModal.classList.add('hidden');
}

async function analyzeFile(file) {
    aiReportContent.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; gap:14px;">
            <div class="loading-dots"><span></span><span></span><span></span></div>
            <p class="placeholder-text" style="font-style:normal;">Analisando qualidade dos dados e gerando relatório...</p>
        </div>
    `;
    openRulesBtn.disabled = true;
    statLinhas.textContent = '...';
    statNulos.textContent = '...';
    statDuplicatas.textContent = '...';
    statScore.textContent = '.../100';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Erro na comunicação com o servidor');

        const data = await response.json();

        updateDashboard(data);

        openRulesBtn.disabled = false;

    } catch (error) {
        console.error('Erro na Análise:', error);
        aiReportContent.innerHTML = `<p class="placeholder-text" style="color: #ef4444;">Erro ao analisar o arquivo. Verifique se o servidor FastAPI está rodando.</p>`;
        statLinhas.textContent = '--';
        statNulos.textContent = '--';
        statDuplicatas.textContent = '--';
        statScore.textContent = '--/100';
    }
}

function updateDashboard(data) {
    statLinhas.textContent = data.estatisticas.linhas.toLocaleString('pt-BR');
    statNulos.textContent = data.estatisticas.nulos.toLocaleString('pt-BR');
    statDuplicatas.textContent = data.estatisticas.duplicatas.toLocaleString('pt-BR');
    statScore.textContent = `${data.estatisticas.score}/100`;
    aiReportContent.innerHTML = `<p style="text-align: left; margin: 0; font-size: 0.95rem;">${data.relatorio_ia.replace(/\n/g, '<br>')}</p>`;
}

async function downloadCleanedFile(file, regras) {
    rulesModal.classList.add('hidden');
    confirmRulesBtn.innerHTML = 'Padronizando...';
    confirmRulesBtn.disabled = true;
    openRulesBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('remover_duplicatas', regras.duplicatas);
    formData.append('preencher_nulos', regras.nulos);
    formData.append('normalizar_colunas', regras.colunas);

    try {
        const response = await fetch(`${API_BASE_URL}/clean`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Erro ao processar limpeza');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `Insightia_Padronizado_${file.name}`;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Erro no Download:', error);
        alert('Ocorreu um erro ao tentar padronizar o arquivo. Verifique o servidor.');
    } finally {
        confirmRulesBtn.innerHTML = confirmRulesBtnOriginalHTML;
        confirmRulesBtn.disabled = false;
        openRulesBtn.disabled = false;
    }
}