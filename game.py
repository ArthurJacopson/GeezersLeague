import csv
import random

# Read player data from a CSV file
def read_player_data(file_path):
    players = {"Team A": [], "Team B": []}
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                player = {
                    'number': int(row['number']),
                    'name': row['name'],
                    'position': row['position'],
                    'shooting': int(row['shooting']),
                    'passing': int(row['passing']),
                    'tackling': int(row['tackling']),
                    'goalkeeping': int(row['goalkeeping'])
                }
                players[row['team']].append(player)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except ValueError as e:
        print(f"Error: Invalid data format in {file_path}. {e}")
    return players

# Modify event probability based on player stats
def modify_probability(base_prob, stat, stat_weight=1.0):
    avg_stat = 5  # Assuming average stat value
    return base_prob * (1 + stat_weight * (stat - avg_stat) / 10)

# Define events and their base probabilities for each sector
events = {
    "Midfield": {
        "Pass to Opposition": {"base_prob": 40, "next_sector": "Opposition Side"},
        "Dribble": {"base_prob": 35, "next_sector": "Opposition Side"},
        "Turnover": {"base_prob": 15, "next_sector": "Our Side"},
        "Opponent Intercepts": {"base_prob": 10, "next_sector": "Our Side"}
    },
    "Opposition Side": {
        "Pass to Penalty Area": {"base_prob": 45, "next_sector": "Opposition Penalty Area"},
        "Shoot": {"base_prob": 30, "next_sector": "Goal Attempt"},
        "Dribble": {"base_prob": 15, "next_sector": "Opposition Penalty Area"},
        "Opponent Clears": {"base_prob": 10, "next_sector": "Midfield"}
    },
    "Our Side": {
        "Pass to Midfield": {"base_prob": 50, "next_sector": "Midfield"},
        "Opponent Shoots": {"base_prob": 25, "next_sector": "Our Penalty Area"},
        "Dribble": {"base_prob": 15, "next_sector": "Midfield"},
        "Clearance": {"base_prob": 10, "next_sector": "Midfield"}
    },
    "Opposition Penalty Area": {
        "Shoot": {"base_prob": 60, "next_sector": "Goal Attempt"},
        "Foul by Defender": {"base_prob": 15, "next_sector": "Free Kick or Penalty Kick"},
        "Dribble": {"base_prob": 15, "next_sector": "Opposition Penalty Area"},
        "Opponent Clears": {"base_prob": 10, "next_sector": "Opposition Side"}
    },
    "Our Penalty Area": {
        "Save and Clearance": {"base_prob": 60, "next_sector": "Our Side"},
        "Opponent Shoots": {"base_prob": 25, "next_sector": "Goal Attempt"},
        "Dribble": {"base_prob": 10, "next_sector": "Our Side"},
        "Opponent Fouled": {"base_prob": 5, "next_sector": "Free Kick or Penalty Kick"}
    }
}

# Select an event based on player influence in the current sector
def select_event_with_player_influence(sector, team, players):
    sector_players = [p for p in players[team] if sector.lower() in p['position'].lower()]
    if not sector_players:
        return None, None, []

    total_prob = sum(event["base_prob"] for event in events[sector].values())
    rand_value = random.uniform(0, total_prob)
    cumulative = 0

    for event_name, event in events[sector].items():
        # Calculate modified probability based on player stats
        player_stat = sum(p['passing'] for p in sector_players) / len(sector_players)
        modified_prob = modify_probability(event["base_prob"], player_stat)
        cumulative += modified_prob
        if rand_value <= cumulative:
            return event_name, event["next_sector"], sector_players
    return None, None, []

# Handle goal scoring events
def handle_goal_scoring(team, players):
    goal_scorers = [p for p in players[team] if 'forward' in p['position'].lower()]
    if not goal_scorers:
        return f"An unknown player scored for {team}!"
    else:
        scorer = random.choice(goal_scorers)
        return f"{scorer['name']} scored for {team}!"

# Handle free kicks and penalty kicks
def handle_free_kick_or_penalty_kick(sector, team, players):
    if sector == "Free Kick or Penalty Kick":
        free_kick_takers = [p for p in players[team] if 'midfielder' in p['position'].lower()]
        if not free_kick_takers:
            print(f"No midfielders available to take the free kick for {team}.")
            return "Midfield", None
        else:
            taker = random.choice(free_kick_takers)
            print(f"{taker['name']} of {team} taking the free kick.")
            return "Midfield", None
    else:
        return sector, None

# Simulate a single tick of the game
def simulate_tick(current_sector, team, players, score):
    event_name, next_sector, active_players = select_event_with_player_influence(current_sector, team, players)
    if event_name:
        print(f"{team} {current_sector}: {event_name}")
        if next_sector == "Goal Attempt":
            goal_scored = random.random() < 0.3  # 30% chance of scoring
            if goal_scored:
                goal_story = handle_goal_scoring(team, players)
                print(goal_story)
                score[team] += 1
                next_sector = "Midfield"
        elif next_sector == "Free Kick or Penalty Kick":
            next_sector, _ = handle_free_kick_or_penalty_kick(next_sector, team, players)
        return next_sector, score
    else:
        print(f"No valid event in {current_sector} for {team}")
        return current_sector, score

# Simulate the entire game
def simulate_game(players):
    score = {"Team A": 0, "Team B": 0}
    current_sector_team_a = "Midfield"
    current_sector_team_b = "Midfield"

    ticks = 0
    max_ticks = 90  # Simulating a 90-minute game
    while ticks < max_ticks:
        print(f"\nTick {ticks + 1}:")
        print(f"Score: Team A {score['Team A']} - {score['Team B']} Team B")

        current_sector_team_a, score = simulate_tick(current_sector_team_a, 'Team A', players, score)
        current_sector_team_b, score = simulate_tick(current_sector_team_b, 'Team B', players, score)

        ticks += 1

    # Determine the winner
    if score['Team A'] > score['Team B']:
        winner = "Team A"
    elif score['Team A'] < score['Team B']:
        winner = "Team B"
    else:
        winner = "It's a draw!"

    print(f"\nFinal Score: Team A {score['Team A']} - {score['Team B']} Team B")
    print(f"The winner is: {winner}")

# Select an event based on player influence in the current sector
def select_event_with_player_influence(sector, team, players):
    # Determine which players can influence the current sector
    sector_positions = {
        "Midfield": ["midfielder"],
        "Opposition Side": ["midfielder", "forward"],
        "Our Side": ["midfielder", "defender"],
        "Opposition Penalty Area": ["forward"],
        "Our Penalty Area": ["defender", "goalkeeper"]
    }

    relevant_positions = sector_positions.get(sector, [])
    sector_players = [p for p in players[team] if any(pos in p['position'].lower() for pos in relevant_positions)]

    if not sector_players:
        print(f"No players available for {team} in {sector}.")
        return None, None, []

    total_prob = sum(event["base_prob"] for event in events[sector].values())
    rand_value = random.uniform(0, total_prob)
    cumulative = 0

    for event_name, event in events[sector].items():
        # Calculate modified probability based on player stats
        player_stat = sum(p['passing'] for p in sector_players) / len(sector_players)
        modified_prob = modify_probability(event["base_prob"], player_stat)
        cumulative += modified_prob
        if rand_value <= cumulative:
            return event_name, event["next_sector"], sector_players
    
    return None, None, []

# Main function to run the game
def main():
    player_data = read_player_data('player_data.csv')
    if not player_data:
        print("Error: No player data found.")
        return

    simulate_game(player_data)

if __name__ == "__main__":
    main()
