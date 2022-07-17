from random import choice
from collections import defaultdict
from colorama import Fore

available_cards = {"A": 4, "2": 4, "3": 4, "4": 4, "5": 4, "6": 4, "7": 4, "8": 4, "9": 4, "10": 4, "J": 4, "Q": 4, "K": 4}
card_values = {"A": [1, 11], "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10}
colors_list = ["Fore.LIGHTBLUE_EX", "Fore.LIGHTGREEN_EX", "Fore.LIGHTMAGENTA_EX", "Fore.LIGHTRED_EX", "Fore.LIGHTCYAN_EX", "Fore.LIGHTYELLOW_EX", "Fore.LIGHTWHITE_EX"]
players_color = defaultdict(str)

# Gets list of cards where there is at least one Jack. Returns most optimal value of points.
def decide_jack_value(cards):
    jacks = [j for j in cards if j == "A"]
    non_jacks = [n for n in cards if n != "A"]
    if sum(card_values[c] for c in non_jacks) + len(jacks) - 1 >= 11:  # Then all Jacks are 1
        num = sum(card_values[c] for c in non_jacks) + sum(card_values[a][0] for a in jacks)
    else:
        # First Jack is 11, others must be 1
        num = sum(card_values[c] for c in cards if c != "A") + sum(card_values[a][1] for a in jacks[0]) + sum(card_values[a][0] for a in jacks[1:])
    return num


def show_result(cards, display=True):
    # Returns dictionary with name as key and result (points) as value
    return_value = defaultdict(int)
    for k, v in cards.items():
        # If we don't have any Jacks then result (points) are the same as values in card_values
        if "A" not in v:
            num = sum(card_values[c] for c in v)
            return_value[k] = num
        else:
            # We have at least one Jack. Call decide_jack_value to get 1 or 11 from Jack.
            num = decide_jack_value(cards[k])
            return_value[k] = num
        card = ", ".join(x for x in v)
        if num == 21 and display:
            print(eval(players_color[k]) + f"{k} {Fore.RESET} => {card} ({num}) " + Fore.RESET + Fore.YELLOW + f"BLACKJACK!" + Fore.RESET)
        elif num > 21 and display:
            print(eval(players_color[k]) + f"{k} {Fore.RESET} => {card} ({num}) " + Fore.RESET + Fore.RED + f"BUSTED!" + Fore.RESET)
        else:
            if display:
                print(eval(players_color[k]) + f"{k} {Fore.RESET} => {card} ({num}) " + Fore.RESET)
    return return_value


def give_first_two_cards(players, names):
    global players_color
    players_color = {name: colors_list[i] for i, name in enumerate(names)}
    return_value = defaultdict(list)
    for i in range(players):
        # We generate list of available cards so then we know which are available
        cards_list = [k for k, v in available_cards.items() for _ in range(v)]
        # We take 1st card
        rnd_card = list(choice(cards_list) for _ in range(1))
        # We update number of available cards
        for c in rnd_card:
            available_cards[c] -= 1
        # We generate list of available cards so then we know which are available
        cards_list = [k for k, v in available_cards.items() for _ in range(v)]
        # We take 2nd card
        rnd_card2 = list(choice(cards_list) for _ in range(1))
        # We update number of available cards
        for c in rnd_card2:
            available_cards[c] -= 1
        return_value[names[i]] = rnd_card + rnd_card2
    show_result(return_value)
    return return_value


# If someone triggers a Hit, he is given one card
def give_one_card(to_who, cards):
    cards_list = [k for k, v in available_cards.items() for _ in range(v)]
    rnd_card = list(choice(cards_list) for _ in range(1))
    for c in rnd_card:
        available_cards[c] -= 1
    cards[to_who].extend(rnd_card)


# Looping Hit or Stand
def check_input_loop(cards):
    return_value = defaultdict(int)
    for k, v in cards.items():
        stand_or_hit = ""
        # If the player has already got blackjack with first two cards, he automatically Stands
        if sum(card_values[c] for c in v if c != "A") + sum(card_values[c][1] for c in v if c == "A") == 21:
            stand_or_hit = "S"
            return_value[k] = show_result(cards, display=False)[k]
        while stand_or_hit.upper() != "S":
            print("---------------------------")
            stand_or_hit = input(eval(players_color[k]) + f"{k}: {Fore.GREEN} (S) stand, (H) hit ? " + Fore.RESET)
            print("---------------------------")
            if stand_or_hit.upper() == "S":
                results = show_result(cards)
                return_value[k] = results[k]
            elif stand_or_hit.upper() == "H":
                give_one_card(k, cards)
                res = show_result(cards)
                if res[k] >= 21:  # If someone has 21 or more points, they have either won or lost - same as Stand
                    stand_or_hit = "S"
                    return_value[k] = res[k]
            else:
                print(Fore.GREEN + "WRONG BUTTON! Try again ... (S) stand, (H) hit ? " + Fore.RESET)
    return return_value


# Printing leaderboard (if more people have equivalent points, they share the same place)
def leaderboard(results_dict):
    print(f"-------------")
    print(Fore.YELLOW + f"🏆 LEADERBOARD 🏆" + Fore.RESET)
    over_21_sorted = sorted({k: v for k, v in results_dict.items() if v > 21}.items(), key=lambda item: item[1])
    under_21_sorted = sorted({k: v for k, v in results_dict.items() if v <= 21}.items(), key=lambda item: item[1], reverse=True)

    place = 1
    under_21_sorted.append(("ignore", -1))
    i = 0
    while i < len(under_21_sorted) - 1:
        name, points = under_21_sorted[i]
        name2, points2 = under_21_sorted[i + 1]
        print(eval(players_color[name]) + f"{place}. {name} ({points})" + Fore.RESET)
        if points2 != points:
            place += 1
        i += 1

    over_21_sorted.append(("ignore", -1))
    i = 0
    while i < len(over_21_sorted) - 1:
        name, points = over_21_sorted[i]
        name2, points2 = over_21_sorted[i + 1]
        print(eval(players_color[name]) + f"{place}. {name} ({points})" + Fore.RESET)
        if points2 != points:
            place += 1
        i += 1


# Game
def blackjack():
    num_players = int(input("Number of players: "))
    names = [input(eval(colors_list[i]) + f"Name of {i+1}. player: ") for i in range(num_players)]
    print(Fore.RESET + "==========================")
    cards = give_first_two_cards(num_players, names)
    results_dict = check_input_loop(cards)
    leaderboard(results_dict)


blackjack()
