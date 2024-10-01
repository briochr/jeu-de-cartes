import math
import re
import random


class Value:
    def __init__(self, value, cValue):
        self.value = value  # Real part
        self.cValue = cValue  # Imaginary part

    def __add__(self, other):
        if isinstance(other, Value):
            return Value(self.value + other.value, self.cValue + other.cValue)
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, Value):
            self.value += other.value
            self.cValue += other.cValue
        return self

    def __sub__(self, other):
        if isinstance(other, Value):
            return Value(self.value - other.value, self.cValue - other.cValue)
        return NotImplemented

    def __isub__(self, other):
        if isinstance(other, Value):
            self.value -= other.value
            self.cValue -= other.cValue
        return self

    def __mul__(self, other):
        if isinstance(other, Value):
            return Value(self.value * other.value - self.cValue * other.cValue,
                         self.value * other.cValue + self.cValue * other.value)
        return NotImplemented

    def __imul__(self, other):
        if isinstance(other, Value):
            temp_value = self.value * other.value - self.cValue * other.cValue
            temp_cValue = self.value * other.cValue + self.cValue * other.value
            self.value, self.cValue = temp_value, temp_cValue
        return self

    def __truediv__(self, other):
        if isinstance(other, Value):
            denom = other.value ** 2 + other.cValue ** 2
            if denom == 0:
                raise ZeroDivisionError("division by zero")
            real_part = (self.value * other.value + self.cValue * other.cValue) / denom
            imag_part = (self.cValue * other.value - self.value * other.cValue) / denom
            return Value(real_part, imag_part)
        return NotImplemented

    def __itruediv__(self, other):
        if isinstance(other, Value):
            denom = other.value ** 2 + other.cValue ** 2
            if denom == 0:
                raise ZeroDivisionError("division by zero")
            real_part = (self.value * other.value + self.cValue * other.cValue) / denom
            imag_part = (self.cValue * other.value - self.value * other.cValue) / denom
            self.value, self.cValue = real_part, imag_part
        return self

    def __repr__(self):
        return f"Value(real={self.value}, imaginary={self.cValue})"


class Card:
    def __init__(self, name, value):
        self._name = name  # ID
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"Card(name='{self._name}', value={self._value})"


class FunctionCard(Card):
    def __init__(self, name, func):
        super().__init__(name, None)
        self.func = func

    def apply(self, value: Value):
        return self.func(value)

    def __repr__(self):
        return f"FunctionCard(name='{self._name}', function={self.func.__name__})"


class CardContainer:
    def __init__(self):
        self.cards = []

    def append(self, item: Card):
        self.cards.append(item)

    def remove(self, item: Card):
        self.cards.remove(item)

    def print(self):
        for card in self.cards:
            print(card)

    def draw(self):
        if self.cards:
            return self.cards.pop(0)  # Draw the first card
        return None


class CardTable(Card):
    def __init__(self, name: str, value: Value):
        super().__init__(name, value)
        self.isReturned = True  # At the start, cards are all face down

    def returnCard(self):
        self.isReturned = not self.isReturned

    def setTrue(self):
        self.isReturned = True

    def __repr__(self):
        return f"CardTable(name='{self._name}', value={self._value}, isReturned={self.isReturned})"


class Player:
    def __init__(self, name):
        self.name = name
        self.inv = CardContainer()
        self.score: Value = Value(0, 0)

    def addInv(self, item: Card):
        self.inv.append(item)

    def removeInv(self, item: Card):
        self.inv.remove(item)

    def setScore(self, value: Value):
        self.score = value

    def addScore(self, value: Value):
        self.score += value

    def subScore(self, value: Value):
        self.score -= value

    def mulScore(self, value: Value):
        self.score *= value

    def divScore(self, value: Value):
        self.score /= value

    def __repr__(self):
        return f"Player(name='{self.name}', score={self.score})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Player):
            return self.name == other.name
        return False

    def showDeck(self):
        for card in self.inv.cards:
            print(card)


class Operand:
    def __init__(self, operator):
        self.operator = operator

    def apply(self, left: Value, right: Value):
        if self.operator == '+':
            return left + right
        elif self.operator == '-':
            return left - right
        elif self.operator == '*':
            return left * right
        elif self.operator == '/':
            return left / right
        elif self.operator == '%':
            # Assuming modulus is intended for the real part only
            return Value(left.value % right.value, left.cValue % right.cValue)
        elif self.operator == '^':
            # Assuming exponentiation is for real numbers only
            return Value(left.value ** right.value, left.cValue ** right.cValue)
        elif self.operator == '=':
            return left  # or however you want to handle '=' operator
        else:
            raise ValueError("Unknown operator")


class WinConditionCard(Card):
    def __init__(self, name, win_condition):
        super().__init__(name, None)
        self.win_condition = win_condition

    def apply(self, player: Player):
        return self.win_condition(player)

    def __repr__(self):
        return f"WinConditionCard(name='{self._name}', win_condition={self.win_condition.__name__})"


# Initializing the LA PIOCHE
pioche = CardContainer()

# Setting up cards on the table at the start
cartes_sur_la_table = CardContainer()
[cartes_sur_la_table.append(CardTable(str(i), Value(i, 0))) for i in range(10)]
cartes_sur_la_table.append(CardTable("e", Value(math.e, 0)))
cartes_sur_la_table.append(CardTable("pi", Value(math.pi, 0)))

# Adding function cards to the deck
pioche.append(FunctionCard("sin", lambda v: Value(math.sin(v.value), 0)))
pioche.append(FunctionCard("cos", lambda v: Value(math.cos(v.value), 0)))

random.shuffle(pioche.cards)

# Players draw cards at the start (we say 3 cards each)
player1 = Player("Robert")
player2 = Player("Gatito")
players = [player1, player2]

for player in players:
    for _ in range(3):
        card = pioche.draw()
        if card:
            player.addInv(card)

counter = 0
turn = 0
while pioche.cards:
    operands = 2
    current_player = players[counter]
    counter = (counter + 1) % len(players)
    print(f"\n{current_player.name}'s turn")

    target_player_name = input('Which player do you want to target?\n-> ')
    target_player = next((player for player in players if player.name == target_player_name), None)

    if not target_player:
        print("Target player not found.")
        continue

    card_drawn = pioche.draw()
    if card_drawn is None:
        print("No more cards to draw.")
        break

    print(f"{current_player.name} drew {card_drawn}")
    result = 0

    while True:
        stack = []

        choice = input('Quelle carte souhaite-tu jouer de ta main?\n-> ')

        if choice == 'show':
            current_player.showDeck()

        elif choice == 'end':
            break

        elif re.match(r'[+\-*/%^=]', choice):  # find an operator
            pattern = r'[+\-*/%^=]'
            operator = re.findall(pattern, choice)[0]
            stack.append(Operand(operator))

        elif re.match(r"\b(1000|[1-9][0-9]{0,2}|0)\b", choice):  # find a card
            pattern = r"\b(1000|[1-9][0-9]{0,2}|0)\b"
            matches = re.findall(pattern, choice)
            card_index = int(matches[0]) if matches else None

            if card_index is not None and 0 <= card_index < len(current_player.inv.cards):
                card = current_player.inv.cards[card_index]
                stack.append(card)
            else:
                print("Invalid card selection.")

        if len(stack) == 2:  # If there are two elements in the stack
            operand = stack.pop(0)
            card = stack.pop(0)

            if isinstance(operand, Operand) and isinstance(card, Card):
                current_player.score = operand.apply(current_player.score, card.value)
                print(f'{target_player} now has a score of {target_player.score}')
            else:
                print("Invalid operation.")

    print(f"{current_player.name}'s new score: {current_player.score}")

    turn += 1

# Display final scores
print("\nGame over!")
print(f"{player1.name}'s final score: {player1.score}")
print(f"{player2.name}'s final score: {player2.score}")

if player1.score.value > player2.score.value:
    print(f"{player1.name} wins!")
elif player2.score.value > player1.score.value:
    print(f"{player2.name} wins!")
else:
    print("scores are equals")

