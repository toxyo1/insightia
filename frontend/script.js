document.addEventListener('DOMContentLoaded', () => {
    const homeScreen = document.getElementById('home-screen');
    const chatScreen = document.getElementById('chat-screen');
    const startBtn = document.getElementById('start-btn');
    const backHomeBtn = document.getElementById('back-home-btn');

    startBtn.addEventListener('click', () => {
        homeScreen.classList.remove('active');
        homeScreen.classList.add('hidden');
        chatScreen.classList.remove('hidden');
        chatScreen.classList.add('active');
    });

    backHomeBtn.addEventListener('click', () => {
        chatScreen.classList.remove('active');
        chatScreen.classList.add('hidden');
        homeScreen.classList.remove('hidden');
        homeScreen.classList.add('active');
    });

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    let currentFile = null;

    const handleFile = (file) => {
        if (file && file.name.endsWith('.csv')) {
            currentFile = file;

            fileNameDisplay.textContent = file.name;
            dropZone.style.display = 'none';
            fileInfo.classList.remove('hidden');
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        } else {
            alert('Por favor, envie apenas arquivos no formato .csv');
        }
    };

    fileInput.addEventListener('change', (e) => {
        handleFile(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';

        fileInfo.classList.add('hidden');
        dropZone.style.display = 'flex';

        chatInput.disabled = true;
        sendBtn.disabled = true;
        chatInput.value = '';
    });

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const text = chatInput.value.trim();

        if (text !== '') {
            chatInput.disabled = true;
            sendBtn.disabled = true;

            const userMsg = document.createElement('div');
            userMsg.classList.add('message', 'user-message');
            userMsg.textContent = text;
            chatMessages.appendChild(userMsg);
            chatInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('typing-indicator');
            typingIndicator.innerHTML = '<span></span><span></span><span></span>';
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            setTimeout(() => {
                chatMessages.removeChild(typingIndicator);
                const aiMsg = document.createElement('div');
                aiMsg.classList.add('message', 'ai-message');
                aiMsg.textContent = "Processando seus dados... Esta é uma resposta simulada para testar a interface visual da nossa aplicação. Em breve a API real assumirá este lugar!";
                chatMessages.appendChild(aiMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                chatInput.disabled = false;
                sendBtn.disabled = false;
                chatInput.focus();

            }, 2000);
        }
    });
});