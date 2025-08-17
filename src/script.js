document.addEventListener('DOMContentLoaded', () =>{    
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const promptInput = document.getElementById('prompt');
    const analyzeButton = document.getElementById('analyzeButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultBox = document.getElementById('resultBox');
    const resultText = document.getElementById('resultText');
    const startAudioButton = document.getElementById('startAudioButton');
    const stopAudioButton = document.getElementById('stopAudioButton')
    const audioStatus = document.getElementById('audioStatus')
    const transcriptionDisplay = document.getElementById('transcriptionDisplay')
    const audioObsText = document.getElementById('audioObservationText')
    const startWebcamButton = document.getElementById('startWebcamButton')
    const webcamVideo = document.getElementById('webcamVideo')
    const videoCanvas = document.getElementById('videoCanvas')
    const videoCanvasContext = videoCanvas.getContext('2d')
    const webcamStatus = document.getElementById('webcamStatus')
    const videoObservationText = document.getElementById('videoObservationText')
    
    let uploadedImageBase64 = null;
    let uploadedImageMimeType = null;
    let webcamStream = null;
    let capIntId = null; // interval ID
    let audioStream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let audioInterval = null;

    const V_ENDPOINT = 'http://127.0.0.1:5000/process-video-frame';
    const A_ENDPOINT = 'http://127.0.0.1:5000/process-audio-chunk';
    const ANALYZE_IMAGE_ENDPOINT = 'http://127.0.0.1:5000/analyze-image'


    const toggleLoadingState = (isLoading) =>{
        loadingIndicator.classList.toggle('hidden' , !isLoading);
        analyzeButton.disabled = isLoading;
    };

    const showMessage = (message , type = 'info') =>{
        console.log(`[Message - ${type.toLocaleUpperCase()}]: ${message}`)
        resultBox.classList.remove('hidden')
        resultText.textContent = message
        resultBox.style.borderColor = type == 'error' ? 'red' : (type == 'success' ? 'green' : 'blue');
    };

    startWebcamButton.addEventListener('click', async() => {
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamVideo.classList.add('hidden')
            webcamVideo.srcObject = null;
            webcamStatus.textContent = "Webcam Stopped. ";
            clearInterval(capIntId);
            capIntId = null;
            webcamStream = null;
            startWebcamButton.textContent = "Start Webcam Recording";
            videoObservationText.textContent = 'Video: Not Availaible'
            return;
        }
        try{
            webcamStream = await navigator.mediaDevices.getUserMedia({video: true, audio:false});
            webcamVideo.srcObject = webcamStream;
            webcamVideo.classList.remove('hidden');
            webcamStatus.textContent = "Webcam started. Analyzing...";
            startWebcamButton.textContent = "Stop Webcam Analysis";
            webcamVideo.onloadedmetadata = () =>{
                videoCanvas.width = webcamVideo.videoWidth
                videoCanvas.height = webcamVideo.videoHeight;
            };
            capIntId = setInterval(() => {
                if(webcamStream){
                    videoCanvasContext.drawImage(webcamVideo , 0 , 0, videoCanvas.width , videoCanvas.height);
                    const base64Url = videoCanvas.toDataURL('image/jpeg' , 0.8);
                    sendVideoFrame(base64Url)
                }
            }, 5000)
        } catch (err) {
            console.error("Error Acessing webcam: ", err);
            webcamStatus.textContent = `Error: ${err.message}`;
            showMessage("Could not access webcam. Esure permission grated and webcam persent" , 'error')
        }
    });

    const sendVideoFrame = async (base64Url) => {
        try {
            const response = await fetch(V_ENDPOINT, {
                method : 'POST',
                headers : {'Content-Type' : 'application/json'},
                body: JSON.stringify({imageUrl: base64Url})
            });
            if(!response.ok){
                throw new Error(`HTTP Error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Video analysis data:', data)
            if(data.observations){
                const {mood, concentration_level} = data.observations;
                videoObservationText.textContent = `Video: Mood - ${mood}, Concentration - ${concentration_level}%`;
            }
        } catch (error) {
            console.error('Error Sending video Frame:', error);
            videoObservationText.textContent = 'Video: Error processing frame';
        }
    };
    imageInput.addEventListener('change', function(event) {
        const file = event.target.files && event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" class="w-full h-full object-contain rounded-lg" alt="Image preview">`;
                uploadedImageBase64 = e.target.result.split(',')[1];
                uploadedImageMimeType = file.type;
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = 'Image preview will appear here';
            uploadedImageBase64 = null;
            uploadedImageMimeType = null;
        }
    });

    startAudioButton.addEventListener('click' , async () => {
        if(!navigator.mediaDevices) {
            showMessage("Device does not support the media devices API. cannot record audio.", 'error');
            return;
        }
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({audio: true});
            mediaRecorder = new MediaRecorder(audioStream, {mimeType: 'audio/webm;codecs=opus' });
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if(event.data.size > 0){
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {

            }

            mediaRecorder.start(3000);
            audioStatus.textContent = 'Microphone is listening...'
            startAudioButton.disabled = true;
            stopAudioButton.disabled = false;
            transcriptionDisplay.innerHTML = '<p>Transcription will appear here...</p>'
            audioObsText.textContent = 'Audio: Listening....';
            audioInterval = setInterval(() => {
                if (audioChunks.length > 0){
                    sendAudioChunk(audioChunks);
                    audioChunks = [];
                }
            }, 3000);
        } catch (error) {
            console.error("Error accessing microphones: ", err);
            audioStatus.textContent = 'Error accessing microphone....'
            showMessage('Could not access microphone. grant permission', 'error')
        }
    });

    stopAudioButton.addEventListener('click' , () =>{
        if(mediaRecorder && mediaRecorder.state !== 'inactive'){
            mediaRecorder.stop();
            audioStream.getTracks().forEach(track => track.stop());
            clearInterval(audioInterval);
            audioStatus.textContent = 'Microphone stopped.';
            startAudioButton.disabled = false;
            stopAudioButton.disabled = true;
            audioObsText.textContent = 'Audio not Availaible'
        }
    });

    const sendAudioChunk = async (chunks) => {
        const audioBlob = new Blob(chunks, {type: 'audio/webm;codecs=opus'});
        const reader = new FileReader();

        reader.onloadend = async () => {
            const audioBase64Audio = reader.result;
            try{
                const response = await fetch(A_ENDPOINT, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({audio: audioBase64Audio})
                }); 

                if(!response.ok){
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log('Audio Transcription:', data);
                if(data.transcription) {
                    transcriptionDisplay.innerHTML = `<p>${data.transcription}</p>`;
                    audioObsText.textContent = `Audio: ${data.transcription}`;
                }
            }catch (error){
                console.error('Error sending audio chunks:', error);
                audioObsText.textContent = 'Audio: Error processing audio';
            }
        };
        reader.readAsDataURL(audioBlob)
    };

// --- Image Upload and Analysis Functionality ---
    imageInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Image Preview" class="w-full h-full object-contain rounded-lg">`;
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = 'Image preview will appear here';
        }
    });

    analyzeButton.addEventListener('click', async () => {
        const prompt = promptInput.value;
        const imageUrl = imagePreview.querySelector('img')?.src;
        let base64Data = null;
        let mimeType = null;

        if (webcamStream) {
            videoCanvasContext.drawImage(webcamVideo, 0, 0, videoCanvas.width, videoCanvas.height);
            base64Data = videoCanvas.toDataURL('image/jpeg', 0.8);
            mimeType = 'image/jpeg';
        } else if (imageUrl) {
            base64Data = imageUrl;
            mimeType = uploadedImageMimeType;
        }

        if (!base64Data) {
            showMessage('Please select an image or start the webcam.', 'error');
            return;
        }

        if (!prompt) {
            showMessage('Please enter a prompt.', 'error');
            return;
        }

        toggleLoadingState(true);
        resultBox.classList.add('hidden');
        resultText.textContent = '';

        try {
            const response = await fetch(ANALYZE_IMAGE_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    imageUrl: base64Data,
                    mimeType: mimeType
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            toggleLoadingState(false);
            resultBox.classList.remove('hidden');
            resultText.textContent = data.result || data.error;

        } catch (error) {
            console.error('Analysis failed:', error);
            toggleLoadingState(false);
            showMessage(`Analysis failed. Check the server connection. Error: ${error.message}`, 'error');
        }
    });
});