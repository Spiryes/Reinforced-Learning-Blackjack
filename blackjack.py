import numpy as np
from collections import defaultdict
import random

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def get_numeric_value(self):
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 11
        return int(self.value)

    def __str__(self):
        return f"{self.value}{self.suit}"

class Deck:
    def __init__(self):
        self.reset()

    def reset(self):
        suits = ['♠', '♣', '♥', '♦']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for suit in suits for value in values]
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.reset()
        return self.cards.pop()

class BlackjackEnv:
    def __init__(self):
        self.deck = Deck()

    def reset(self):
        self.deck.reset()
        self.player_hand = [self.deck.draw(), self.deck.draw()]
        self.dealer_hand = [self.deck.draw(), self.deck.draw()]
        self.ai_hand = [self.deck.draw(), self.deck.draw()]
        return self._get_state()

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0

        for card in hand:
            card_value = card.get_numeric_value()
            if card_value == 11:
                aces += 1
            value += card_value

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    def _get_state(self):
        return (
            self.calculate_hand_value(self.player_hand),
            self.dealer_hand[0].get_numeric_value(),
            1 if any(card.value == 'A' for card in self.player_hand) else 0
        )

    def ai_step(self):
        """Handle AI player's actions"""
        self.ai_hand.append(self.deck.draw())
        ai_value = self.calculate_hand_value(self.ai_hand)

        done = ai_value >= 21
        reward = 0
        if ai_value > 21:
            reward = -1

        return self._get_state(), reward, done

    def step(self, action):
        # action: 0 = stick, 1 = hit
        done = False
        reward = 0

        if action == 1:  # hit
            self.player_hand.append(self.deck.draw())
            player_value = self.calculate_hand_value(self.player_hand)

            if player_value > 21:
                done = True
                reward = -1
        else:  # stick
            done = True
            player_value = self.calculate_hand_value(self.player_hand)

            # Dealer's turn
            dealer_value = self.calculate_hand_value(self.dealer_hand)
            while dealer_value < 17:
                self.dealer_hand.append(self.deck.draw())
                dealer_value = self.calculate_hand_value(self.dealer_hand)

            # Compare hands
            if dealer_value > 21:
                reward = 1
            else:
                reward = np.sign(player_value - dealer_value)

        return self._get_state(), reward, done

class QLearningAgent:
    def __init__(self, epsilon=0.1, alpha=0.1, gamma=0.9):
        self.q_table = defaultdict(lambda: np.zeros(2))
        self.epsilon = epsilon  # exploration rate
        self.alpha = alpha     # learning rate
        self.gamma = gamma     # discount factor

    def get_action(self, state, training=True):
        if training and random.random() < self.epsilon:
            return random.randint(0, 1)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.alpha * td_error

    def save(self, filename):
        # Convert defaultdict to regular dict for saving
        q_dict = dict(self.q_table)
        np.save(filename, q_dict)

    def load(self, filename):
        # Load and convert back to defaultdict
        q_dict = np.load(filename, allow_pickle=True).item()
        self.q_table = defaultdict(lambda: np.zeros(2), q_dict)

def train_agent(episodes=10000):
    env = BlackjackEnv()
    agent = QLearningAgent()

    for episode in range(episodes):
        state = env.reset()
        done = False

        while not done:
            action = agent.get_action(state, training=True)
            next_state, reward, done = env.step(action)
            agent.learn(state, action, reward, next_state)
            state = next_state

        if episode % 1000 == 0:
            print(f"Training episode {episode}/{episodes}")

    return agent
