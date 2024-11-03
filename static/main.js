/**
 * Main JavaScript file for Blackjack game interface
 * Handles UI updates, game state management, and API interactions
 */

// Game state management
let gameActive = false;

// DOM Elements
const elements = {
    hitButton: document.getElementById('hit-button'),
    standButton: document.getElementById('stand-button'),
    newGameButton: document.getElementById('new-game-button'),
    message: document.getElementById('message')
};

/**
 * Initializes the game by setting up event listeners
 */
function initializeGame() {
    elements.hitButton.addEventListener('click', handleHit);
    elements.standButton.addEventListener('click', handleStand);
    elements.newGameButton.addEventListener('click', startNewGame);

    // Disable game buttons initially
    toggleGameButtons(false);

    // Start first game automatically
    startNewGame();
}

/**
 * Handles the Hit action
 * Sends request to server and updates game state
 */
async function handleHit() {
    try {
        const response = await fetch('/api/hit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        const data = await response.json();
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        updateGameState(data);
        displayGameResults(data);

        if (data.done) {
            endGame();
        }
    } catch (error) {
        showMessage('Error during hit action', 'error');
        console.error('Hit error:', error);
    }
}

/**
 * Handles the Stand action
 * Sends request to server and updates game state
 */
async function handleStand() {
    try {
        const response = await fetch('/api/stand', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        const data = await response.json();
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        updateGameState(data);
        displayGameResults(data);
        endGame();
    } catch (error) {
        showMessage('Error during stand action', 'error');
        console.error('Stand error:', error);
    }
}

/**
 * Starts a new game
 * Resets the game state and requests new cards from server
 */
async function startNewGame() {
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        const data = await response.json();
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        gameActive = true;
        toggleGameButtons(true);
        clearResults();
        updateGameState(data);
        showMessage('New game started!', 'info');
    } catch (error) {
        showMessage('Error starting new game', 'error');
        console.error('New game error:', error);
    }
}

/**
 * Updates the game state in the UI
 * @param {Object} data - Game state data from server
 */
function updateGameState(data) {
    // Update dealer's hand
    const dealerCards = document.querySelector('#dealer-cards');
    dealerCards.textContent = data.done ?
    data.dealer_hand.join(' ') :
    `${data.dealer_hand[0]} 🂠`;

    // Update player's hand
    const playerCards = document.querySelector('#player-cards');
    playerCards.textContent = data.player_hand.join(' ');

    // Update AI's hand
    const aiCards = document.querySelector('#ai-cards');
    aiCards.textContent = data.ai_hand.join(' ');

    // Update scores
    document.querySelector('#dealer-score').textContent = `Score: ${data.dealer_value}`;
    document.querySelector('#player-score').textContent = `Score: ${data.player_value}`;
    document.querySelector('#ai-score').textContent = `Score: ${data.ai_value}`;
}

/**
 * Displays game results for all participants
 * @param {Object} data - Game state data from server
 */
function displayGameResults(data) {
    if (!data.done) return;

    const dealerValue = data.dealer_value;
    const playerValue = data.player_value;
    const aiValue = data.ai_value;

    const results = determineWinners(dealerValue, playerValue, aiValue);

    document.querySelector('#dealer-result').textContent = results.dealer;
    document.querySelector('#player-result').textContent = results.player;
    document.querySelector('#ai-result').textContent = results.ai;
}

/**
 * Determines winners based on final hand values
 * @param {number} dealerValue - Dealer's hand value
 * @param {number} playerValue - Player's hand value
 * @param {number} aiValue - AI's hand value
 * @returns {Object} Results for each participant
 */
function determineWinners(dealerValue, playerValue, aiValue) {
    const results = {
        dealer: '',
        player: '',
        ai: ''
    };

    // Check for busts
    const dealerBust = dealerValue > 21;
    const playerBust = playerValue > 21;
    const aiBust = aiValue > 21;

    // Handle dealer bust scenario
    if (dealerBust) {
        results.dealer = '💥 Bust!';
        results.player = playerBust ? '💥 Bust!' : '🏆 Winner!';
        results.ai = aiBust ? '💥 Bust!' : '🏆 Winner!';
        return results;
    }

    // Handle player results
    results.player = playerBust ? '💥 Bust!' :
    playerValue > dealerValue ? '🏆 Winner!' :
    playerValue < dealerValue ? '❌ Lost' :
    '🤝 Push';

    // Handle AI results
    results.ai = aiBust ? '💥 Bust!' :
    aiValue > dealerValue ? '🏆 Winner!' :
    aiValue < dealerValue ? '❌ Lost' :
    '🤝 Push';

    // Determine dealer's final result
    if (!dealerBust) {
        const dealerWonAgainstSomeone = (playerBust || dealerValue > playerValue) ||
        (aiBust || dealerValue > aiValue);
        const dealerLostAgainstSomeone = (!playerBust && dealerValue < playerValue) ||
        (!aiBust && dealerValue < aiValue);

        results.dealer = dealerWonAgainstSomeone && !dealerLostAgainstSomeone ? '🏆 Winner!' :
        dealerLostAgainstSomeone ? '❌ Lost' :
        '🤝 Push';
    }

    return results;
}

/**
 * Clears all game results from the UI
 */
function clearResults() {
    document.querySelector('#dealer-result').textContent = '';
    document.querySelector('#player-result').textContent = '';
    document.querySelector('#ai-result').textContent = '';
    elements.message.textContent = '';
}

/**
 * Toggles game button states
 * @param {boolean} enabled - Whether buttons should be enabled
 */
function toggleGameButtons(enabled) {
    elements.hitButton.disabled = !enabled;
    elements.standButton.disabled = !enabled;
}

/**
 * Ends the current game
 */
function endGame() {
    gameActive = false;
    toggleGameButtons(false);
}

/**
 * Displays a message to the user
 * @param {string} text - Message text
 * @param {string} type - Message type (error, info)
 */
function showMessage(text, type = 'info') {
    elements.message.textContent = text;
    elements.message.className = `message ${type}`;
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', initializeGame);
