from flask import Flask, render_template, jsonify, request
from blackjack import BlackjackEnv, QLearningAgent, train_agent
import os

app = Flask(__name__)
app.debug = True

# Global game state
game_env = None
ai_agent = None

def initialize_game():
    global game_env, ai_agent
    game_env = BlackjackEnv()

    if os.path.exists('trained_agent.npy'):
        print("Loading trained agent...")
        ai_agent = QLearningAgent()
        ai_agent.load('trained_agent.npy')
    else:
        print("Training new agent...")
        ai_agent = train_agent(episodes=10000)
        ai_agent.save('trained_agent.npy')
        print("Training completed and agent saved!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    global game_env
    try:
        game_env = BlackjackEnv()
        initial_state = game_env.reset()

        # Initial AI decision
        if ai_agent:
            state = (
                game_env.calculate_hand_value(game_env.ai_hand),
                game_env.dealer_hand[0].get_numeric_value(),
                1 if any(card.value == 'A' for card in game_env.ai_hand) else 0
            )
            action = ai_agent.get_action(state, training=False)
            if action == 1:  # AI decides to hit
                game_env.ai_step()

        return jsonify({
            'player_hand': [str(card) for card in game_env.player_hand],
            'dealer_hand': [str(card) for card in game_env.dealer_hand[:1]],  # Only first dealer card
            'ai_hand': [str(card) for card in game_env.ai_hand],
            'player_value': game_env.calculate_hand_value(game_env.player_hand),
            'dealer_value': game_env.calculate_hand_value(game_env.dealer_hand[:1]),
            'ai_value': game_env.calculate_hand_value(game_env.ai_hand),
            'done': False
        })
    except Exception as e:
        print(f"New game error: {str(e)}")
        return jsonify({'error': 'Error starting new game'}), 500

@app.route('/api/hit', methods=['POST'])
def hit():
    global game_env
    try:
        if game_env is None:
            return jsonify({'error': 'No active game'}), 400

        state, reward, done = game_env.step(1)  # 1 for hit

        # Convert numpy.int64 to regular Python int
        reward = int(reward) if hasattr(reward, 'item') else reward

        # AI takes action after player
        if not done and ai_agent:
            state = (
                int(game_env.calculate_hand_value(game_env.ai_hand)),
                int(game_env.dealer_hand[0].get_numeric_value()),
                1 if any(card.value == 'A' for card in game_env.ai_hand) else 0
            )
            action = ai_agent.get_action(state, training=False)
            if action == 1:  # AI decides to hit
                game_env.ai_step()

        response_data = {
            'player_hand': [str(card) for card in game_env.player_hand],
            'dealer_hand': [str(card) for card in game_env.dealer_hand[:1]],
            'ai_hand': [str(card) for card in game_env.ai_hand],
            'player_value': int(game_env.calculate_hand_value(game_env.player_hand)),
            'dealer_value': int(game_env.calculate_hand_value(game_env.dealer_hand[:1])),
            'ai_value': int(game_env.calculate_hand_value(game_env.ai_hand)),
            'done': bool(done),
            'reward': int(reward)
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Hit error: {str(e)}")
        return jsonify({'error': 'Error during hit'}), 500


@app.route('/api/stand', methods=['POST'])
def stand():
    global game_env
    try:
        if game_env is None:
            return jsonify({'error': 'No active game'}), 400

        # Execute stand action
        state, reward, done = game_env.step(0)  # 0 for stand

        # Convert numpy.int64 to regular Python int
        reward = int(reward) if hasattr(reward, 'item') else reward

        # Handle AI actions
        if ai_agent:
            ai_state = (
                int(game_env.calculate_hand_value(game_env.ai_hand)),
                int(game_env.dealer_hand[0].get_numeric_value()),
                1 if any(card.value == 'A' for card in game_env.ai_hand) else 0
            )

            while True:
                action = ai_agent.get_action(ai_state, training=False)
                if action == 0:  # AI stands
                    break
                ai_state, _, ai_done = game_env.ai_step()
                if ai_done:
                    break

        # Convert all numeric values to Python native types
        response_data = {
            'player_hand': [str(card) for card in game_env.player_hand],
            'dealer_hand': [str(card) for card in game_env.dealer_hand],
            'ai_hand': [str(card) for card in game_env.ai_hand],
            'player_value': int(game_env.calculate_hand_value(game_env.player_hand)),
            'dealer_value': int(game_env.calculate_hand_value(game_env.dealer_hand)),
            'ai_value': int(game_env.calculate_hand_value(game_env.ai_hand)),
            'done': bool(done),
            'reward': int(reward)
        }

        return jsonify(response_data)

    except Exception as e:
        import traceback
        print(f"Stand error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_game()
    app.run(debug=True)
