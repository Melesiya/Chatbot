document.addEventListener('DOMContentLoaded', function () {
    const messageArea = document.querySelector('.messages');
    const userInput = document.getElementById('userInput');
    const sendMessageBtn = document.getElementById('sendMessage');

    // Function to display messages in the chat area
    function displayMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', role);
        messageElement.innerText = content;
        messageArea.appendChild(messageElement);
    }

    // Function to send user input to the backend service
    async function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
    
        displayMessage('user', userMessage);
        userInput.value = '';
    
        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
    
            const responseData = await response.json();
            displayMessage('assistant', responseData.message);
        } catch (error) {
            console.error('Fetch error:', error);
            displayMessage('assistant', 'Sorry, something went wrong. Please try again.');
        }
    }
    

    // Event listener for sending message on button click
    sendMessageBtn.addEventListener('click', sendMessage);

    // Event listener for sending message on Enter key press
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
