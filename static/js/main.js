document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const extractBtn = document.getElementById('extract-btn');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-img');
    const dropContent = document.querySelector('.drop-zone-content');
    const resultSection = document.getElementById('result-section');
    const outputText = document.getElementById('output-text');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');

    let selectedFile = null;

    // Handle Drop Zone Click
    dropZone.addEventListener('click', () => {
        if (!selectedFile) fileInput.click();
    });

    // File Input Change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files[0]);
    });

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        handleFiles(dt.files[0]);
    });

    function handleFiles(file) {
        if (file && file.type.startsWith('image/')) {
            selectedFile = file;
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onloadend = () => {
                imagePreview.src = reader.result;
                previewContainer.classList.remove('hidden');
                dropContent.classList.add('hidden');
                extractBtn.disabled = false;
            };
        }
    }

    // Remove Image
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        fileInput.value = '';
        previewContainer.classList.add('hidden');
        dropContent.classList.remove('hidden');
        extractBtn.disabled = true;
        resultSection.classList.add('hidden');
    });

    // Extract Text Logic
    extractBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);

        // UI Loading State
        extractBtn.disabled = true;
        btnText.textContent = 'Processing...';
        loader.classList.remove('hidden');
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                outputText.value = data.text;
                resultSection.classList.remove('hidden');
                resultSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('OCR Error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the server');
        } finally {
            extractBtn.disabled = false;
            btnText.textContent = 'Extract Text';
            loader.classList.add('hidden');
        }
    });

    // Copy to Clipboard
    copyBtn.addEventListener('click', () => {
        outputText.select();
        document.execCommand('copy');

        const originalIcon = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: #10b981;"></i>';
        setTimeout(() => {
            copyBtn.innerHTML = originalIcon;
        }, 2000);
    });

    // Download Text
    downloadBtn.addEventListener('click', () => {
        const text = outputText.value;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vision-ocr-result.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });
});
