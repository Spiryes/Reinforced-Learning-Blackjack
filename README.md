# Blackjack Game with AI Player

A web-based implementation of Blackjack featuring an AI player trained using Q-Learning.

## Project Structure

```
blackjack_game/
├── static/           # Static assets
│   ├── styles.css   # Game styling
│   └── main.js      # Frontend game logic
├── templates/        # HTML templates
│   └── index.html   # Main game page
├── blackjack.py     # Game logic and AI implementation
└── server.py        # Flask server implementation
```

## Features

- Three-way gameplay between human player, AI player, and dealer
- Reinforcement learning AI opponent
- Real-time game state updates
- Visual feedback for game outcomes
- Responsive design

## Setup Instructions

1. Install required Python packages:
```bash
pip install flask numpy
```

2. Run the server:
```bash
python server.py
```

3. Access the game at `http://localhost:5000`

## Game Rules

- Standard Blackjack rules apply
- Dealer must hit on 16 and below, stand on 17 and above
- AI player uses Q-learning strategy
- Aces can be worth 1 or 11
- Multiple winners possible if dealer busts

## Technical Implementation

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- AI: Q-Learning implementation
- State Management: Server-side game state with RESTful API

## API Endpoints

- `/api/new_game` (POST): Start a new game
- `/api/hit` (POST): Request a new card
- `/api/stand` (POST): End current turn

## Contributing

Feel free to submit issues and pull requests for improvements.
