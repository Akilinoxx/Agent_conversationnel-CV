/**
 * CV Chatbot - Script d'intégration pour portfolio
 * 
 * Ce script permet d'intégrer facilement l'agent conversationnel CV
 * dans n'importe quel site web ou portfolio existant.
 * 
 * Usage:
 * 1. Inclure ce script dans votre page HTML
 * 2. Ajouter un élément avec l'id "cv-chatbot-container" où vous souhaitez afficher le chatbot
 * 3. Initialiser le chatbot avec CVChatbot.init({apiUrl: 'URL_DE_VOTRE_API'})
 */

const CVChatbot = (function() {
    // Configuration par défaut
    const defaultConfig = {
        apiUrl: 'http://localhost:8000/api',
        title: 'Assistant CV',
        welcomeMessage: 'Bonjour ! Je suis l\'assistant virtuel d\'Antoine Goupil. N\'hésitez pas à me poser des questions sur ses compétences, son expérience, sa formation ou ses projets.',
        placeholderText: 'Posez votre question ici...',
        sendButtonText: 'Envoyer',
        position: 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
        theme: 'light', // 'light', 'dark'
        width: '350px',
        height: '500px'
    };
    
    // État du chatbot
    let state = {
        initialized: false,
        open: false,
        config: {},
        messages: []
    };
    
    // Éléments DOM
    let elements = {
        container: null,
        chatWindow: null,
        chatMessages: null,
        chatInput: null,
        sendButton: null,
        toggleButton: null
    };
    
    /**
     * Initialise le chatbot avec la configuration fournie
     * @param {Object} userConfig - Configuration utilisateur
     */
    function init(userConfig = {}) {
        // Fusionner la configuration par défaut avec celle de l'utilisateur
        state.config = {...defaultConfig, ...userConfig};
        
        // Vérifier si le conteneur existe
        const container = document.getElementById('cv-chatbot-container');
        if (!container) {
            console.error('Erreur: L\'élément avec l\'id "cv-chatbot-container" n\'a pas été trouvé.');
            return;
        }
        
        elements.container = container;
        
        // Créer les éléments du chatbot
        createChatbotElements();
        
        // Ajouter les gestionnaires d'événements
        addEventListeners();
        
        // Ajouter le message de bienvenue
        addMessage(state.config.welcomeMessage, false);
        
        // Marquer comme initialisé
        state.initialized = true;
        
        console.log('CV Chatbot initialisé avec succès.');
    }
    
    /**
     * Crée les éléments HTML du chatbot
     */
    function createChatbotElements() {
        // Appliquer les styles au conteneur
        elements.container.style.position = 'relative';
        elements.container.style.width = state.config.width;
        elements.container.style.height = state.config.height;
        elements.container.style.zIndex = '1000';
        
        // Déterminer la position du chatbot
        if (state.config.position === 'fixed') {
            elements.container.style.position = 'fixed';
            
            switch (state.config.position) {
                case 'bottom-right':
                    elements.container.style.bottom = '20px';
                    elements.container.style.right = '20px';
                    break;
                case 'bottom-left':
                    elements.container.style.bottom = '20px';
                    elements.container.style.left = '20px';
                    break;
                case 'top-right':
                    elements.container.style.top = '20px';
                    elements.container.style.right = '20px';
                    break;
                case 'top-left':
                    elements.container.style.top = '20px';
                    elements.container.style.left = '20px';
                    break;
                default:
                    elements.container.style.bottom = '20px';
                    elements.container.style.right = '20px';
            }
        }
        
        // Créer la structure HTML
        elements.container.innerHTML = `
            <div class="cv-chatbot ${state.config.theme}" style="display: flex; flex-direction: column; height: 100%; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1); background-color: ${state.config.theme === 'dark' ? '#2c3e50' : '#fff'};">
                <div class="cv-chatbot-header" style="padding: 15px; background-color: ${state.config.theme === 'dark' ? '#1a2533' : '#007bff'}; color: #fff; font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
                    <div>${state.config.title}</div>
                    <button class="cv-chatbot-toggle" style="background: none; border: none; color: #fff; cursor: pointer; font-size: 16px;">−</button>
                </div>
                <div class="cv-chatbot-messages" style="flex: 1; overflow-y: auto; padding: 15px; background-color: ${state.config.theme === 'dark' ? '#34495e' : '#f8f9fa'};">
                </div>
                <div class="cv-chatbot-input" style="display: flex; padding: 10px; background-color: ${state.config.theme === 'dark' ? '#2c3e50' : '#fff'}; border-top: 1px solid ${state.config.theme === 'dark' ? '#1a2533' : '#ddd'};">
                    <input type="text" placeholder="${state.config.placeholderText}" style="flex: 1; padding: 10px; border: 1px solid ${state.config.theme === 'dark' ? '#1a2533' : '#ddd'}; border-radius: 20px; outline: none; background-color: ${state.config.theme === 'dark' ? '#34495e' : '#fff'}; color: ${state.config.theme === 'dark' ? '#fff' : '#333'};">
                    <button style="background-color: #007bff; color: white; border: none; border-radius: 20px; padding: 10px 15px; margin-left: 10px; cursor: pointer;">${state.config.sendButtonText}</button>
                </div>
            </div>
        `;
        
        // Récupérer les références aux éléments
        elements.chatWindow = elements.container.querySelector('.cv-chatbot');
        elements.chatMessages = elements.container.querySelector('.cv-chatbot-messages');
        elements.chatInput = elements.container.querySelector('.cv-chatbot-input input');
        elements.sendButton = elements.container.querySelector('.cv-chatbot-input button');
        elements.toggleButton = elements.container.querySelector('.cv-chatbot-toggle');
    }
    
    /**
     * Ajoute les gestionnaires d'événements
     */
    function addEventListeners() {
        // Gestionnaire pour le bouton d'envoi
        elements.sendButton.addEventListener('click', handleSendMessage);
        
        // Gestionnaire pour la touche Entrée
        elements.chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSendMessage();
            }
        });
        
        // Gestionnaire pour le bouton de bascule
        elements.toggleButton.addEventListener('click', toggleChatWindow);
    }
    
    /**
     * Gère l'envoi d'un message
     */
    function handleSendMessage() {
        const message = elements.chatInput.value.trim();
        if (!message) return;
        
        // Ajouter le message de l'utilisateur
        addMessage(message, true);
        
        // Vider le champ de saisie
        elements.chatInput.value = '';
        
        // Désactiver l'entrée pendant la génération de la réponse
        elements.chatInput.disabled = true;
        elements.sendButton.disabled = true;
        
        // Ajouter l'indicateur de frappe
        addTypingIndicator();
        
        // Envoyer la requête à l'API
        sendMessageToAPI(message);
    }
    
    /**
     * Envoie un message à l'API
     * @param {string} message - Message à envoyer
     */
    async function sendMessageToAPI(message) {
        try {
            // Préparer la requête
            const response = await fetch(`${state.config.apiUrl}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: message,
                    streaming: true
                })
            });
            
            // Vérifier si la requête a réussi
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            // Créer un lecteur pour le flux de données
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            // Supprimer l'indicateur de frappe
            removeTypingIndicator();
            
            // Créer un élément pour la réponse de l'agent
            const agentMessageElement = document.createElement('div');
            agentMessageElement.classList.add('cv-chatbot-message', 'agent');
            agentMessageElement.style.backgroundColor = state.config.theme === 'dark' ? '#2c3e50' : '#e9ecef';
            agentMessageElement.style.color = state.config.theme === 'dark' ? '#fff' : '#333';
            agentMessageElement.style.padding = '10px 15px';
            agentMessageElement.style.borderRadius = '18px';
            agentMessageElement.style.marginBottom = '10px';
            agentMessageElement.style.maxWidth = '80%';
            agentMessageElement.style.alignSelf = 'flex-start';
            agentMessageElement.style.borderBottomLeftRadius = '4px';
            
            elements.chatMessages.appendChild(agentMessageElement);
            
            // Lire le flux de données
            let agentResponse = '';
            
            while (true) {
                const { value, done } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // Décoder les données
                const chunk = decoder.decode(value);
                
                // Traiter les lignes de données
                const lines = chunk.split('\n\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.content) {
                                agentResponse += data.content;
                                agentMessageElement.textContent = agentResponse;
                                elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
                            }
                            
                            if (data.done) {
                                break;
                            }
                        } catch (e) {
                            console.error('Erreur de parsing JSON:', e);
                        }
                    }
                }
            }
            
            // Ajouter le message à l'état
            state.messages.push({
                content: agentResponse,
                isUser: false
            });
            
        } catch (error) {
            console.error('Erreur lors de la communication avec l\'API:', error);
            removeTypingIndicator();
            addMessage('Désolé, une erreur est survenue lors de la communication avec l\'API.', false);
        } finally {
            // Réactiver l'entrée utilisateur
            elements.chatInput.disabled = false;
            elements.sendButton.disabled = false;
            elements.chatInput.focus();
        }
    }
    
    /**
     * Ajoute un message à la conversation
     * @param {string} content - Contenu du message
     * @param {boolean} isUser - Indique si le message provient de l'utilisateur
     */
    function addMessage(content, isUser) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('cv-chatbot-message');
        messageElement.classList.add(isUser ? 'user' : 'agent');
        
        // Appliquer les styles en fonction du type de message et du thème
        messageElement.style.backgroundColor = isUser 
            ? '#007bff' 
            : (state.config.theme === 'dark' ? '#2c3e50' : '#e9ecef');
        messageElement.style.color = isUser || state.config.theme === 'dark' ? '#fff' : '#333';
        messageElement.style.padding = '10px 15px';
        messageElement.style.borderRadius = '18px';
        messageElement.style.marginBottom = '10px';
        messageElement.style.maxWidth = '80%';
        messageElement.style.alignSelf = isUser ? 'flex-end' : 'flex-start';
        
        // Ajuster les coins pour indiquer la direction
        if (isUser) {
            messageElement.style.borderBottomRightRadius = '4px';
            messageElement.style.marginLeft = 'auto';
        } else {
            messageElement.style.borderBottomLeftRadius = '4px';
        }
        
        messageElement.textContent = content;
        elements.chatMessages.appendChild(messageElement);
        
        // Faire défiler vers le bas
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        
        // Ajouter le message à l'état
        state.messages.push({
            content,
            isUser
        });
    }
    
    /**
     * Ajoute l'indicateur de frappe
     */
    function addTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.id = 'cv-chatbot-typing-indicator';
        indicatorElement.classList.add('cv-chatbot-message', 'agent');
        
        // Appliquer les styles
        indicatorElement.style.backgroundColor = state.config.theme === 'dark' ? '#2c3e50' : '#e9ecef';
        indicatorElement.style.color = state.config.theme === 'dark' ? '#fff' : '#333';
        indicatorElement.style.padding = '10px 15px';
        indicatorElement.style.borderRadius = '18px';
        indicatorElement.style.marginBottom = '10px';
        indicatorElement.style.maxWidth = '80%';
        indicatorElement.style.alignSelf = 'flex-start';
        indicatorElement.style.borderBottomLeftRadius = '4px';
        
        // Créer l'animation de frappe
        indicatorElement.innerHTML = `
            <div style="display: inline-block; width: 50px; height: 20px; position: relative;">
                <span style="display: inline-block; width: 8px; height: 8px; background-color: ${state.config.theme === 'dark' ? '#fff' : '#888'}; border-radius: 50%; margin: 0 2px; animation: typing 1.4s infinite both;"></span>
                <span style="display: inline-block; width: 8px; height: 8px; background-color: ${state.config.theme === 'dark' ? '#fff' : '#888'}; border-radius: 50%; margin: 0 2px; animation: typing 1.4s infinite both; animation-delay: 0.2s;"></span>
                <span style="display: inline-block; width: 8px; height: 8px; background-color: ${state.config.theme === 'dark' ? '#fff' : '#888'}; border-radius: 50%; margin: 0 2px; animation: typing 1.4s infinite both; animation-delay: 0.4s;"></span>
            </div>
        `;
        
        // Ajouter l'animation CSS si elle n'existe pas déjà
        if (!document.getElementById('cv-chatbot-typing-animation')) {
            const style = document.createElement('style');
            style.id = 'cv-chatbot-typing-animation';
            style.textContent = `
                @keyframes typing {
                    0% { transform: translateY(0); }
                    50% { transform: translateY(-5px); }
                    100% { transform: translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
        
        elements.chatMessages.appendChild(indicatorElement);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
    
    /**
     * Supprime l'indicateur de frappe
     */
    function removeTypingIndicator() {
        const indicator = document.getElementById('cv-chatbot-typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    /**
     * Bascule l'affichage de la fenêtre de chat
     */
    function toggleChatWindow() {
        state.open = !state.open;
        
        if (state.open) {
            elements.chatWindow.style.display = 'flex';
            elements.toggleButton.textContent = '−';
        } else {
            elements.chatWindow.style.display = 'none';
            elements.toggleButton.textContent = '+';
        }
    }
    
    // API publique
    return {
        init,
        addMessage,
        toggleChatWindow
    };
})();
