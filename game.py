import csv
import random

# Define the Player class
class Player:
    def __init__(self, player_id, player_name, team, position, passing, defending, shooting, goalkeeping):
        self.player_id = player_id
        self.player_name = player_name
        self.team = team
        self.position = position
        self.passing = passing
        self.defending = defending
        self.shooting = shooting
        self.goalkeeping = goalkeeping

    def decide_action(self, current_sector, free_kick=False, penalty=False):
        """Decide on the action to take based on the current sector."""
        try:
            # Convert current_sector to an integer
            current_sector = int(current_sector)
        except ValueError:
            print(f"[ERROR] Invalid current_sector: {current_sector}")
            return None, None

        # Define the success rates for different actions
        run_success_rate = 0.7
        pass_success_rate = 0.8
        if free_kick:
            shoot_success_rate = 0.7
        else:
            shoot_success_rate = 0.6

        # Randomly determine the action
        random_number = random.random()

        if random_number < run_success_rate:
            action = 'run'
            # Move to a random sector in the same half
            target_sector = (current_sector + random.randint(1, 3)) % 10
        elif random_number < pass_success_rate:
            action = 'pass'
            # Pass to a random sector in the same half
            target_sector = (current_sector + random.randint(1, 3)) % 10
        else:
            action = 'shoot'
            # Shoot towards a random sector in the opposition half
            if free_kick:
                target_sector = random.randint(0, 9)  # Change this range based on the field configuration
            elif penalty:
                target_sector = 4  # The center of the goal for penalties
            else:
                target_sector = random.randint(0, 9)  # Change this range based on the field configuration

        return action, target_sector

# Function to load players from a CSV file
def load_players_from_csv(file_path):
    players = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player = Player(
                player_id=row['player_id'],
                player_name=row['player_name'],
                team=row['team'],
                position=row['position'],
                passing=float(row['passing']),
                defending=float(row['defending']),
                shooting=float(row['shooting']),
                goalkeeping=float(row['goalkeeping'])
            )
            players.append(player)
    return players

class Match:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b
        self.score = {'Team A': 0, 'Team B': 0}
        self.possession = None
        self.current_sector = None
        self.ticks = 90

    def kickoff(self, scoring_team=None):
        print("Kickoff!")
        if scoring_team == 'Team A':
            self.possession = self.team_b
        elif scoring_team == 'Team B':
            self.possession = self.team_a
        else:
            # If it's the start of the game or after halftime, the ball starts from the midfield
            self.possession = random.choice([self.team_a, self.team_b])
            self.current_sector = 5  # Ball starts at the midfield

        if scoring_team is not None:
            # If it's not the start of the game or after halftime, print which team is kicking off
            print(f"{scoring_team} kicks off!")

        self.current_sector = 5  # Reset ball to midfield
    def simulate_event(self, player, current_sector, tick, free_kick=False, penalty=False):
        action, target_sector = player.decide_action(current_sector, free_kick, penalty)
        if action == 'shoot':
            success, goal_scored = self.attempt_shot(player, penalty)
            if goal_scored:
                self.score[self.possession[0].team] += 1
                # Check if a goal was scored and trigger kickoff
                if self.score[self.possession[0].team] < 5:  # Change the condition as needed
                    print("Goal scored!")
                    self.kickoff(scoring_team=self.possession[0].team)
        else:
            success = True

        # Introduce a probability of possession change
        if random.random() < 0.1:  # Adjust the probability as needed
            self.possession = self.team_b if self.possession == self.team_a else self.team_a

        return success, target_sector

    def attempt_shot(self, player, penalty=False):
        target_sector = random.randint(0, 9)
        if penalty:
            goal_scored = random.random() < 0.8  # Higher chance of scoring in penalties
        else:
            goal_scored = random.random() < 0.3  # Placeholder for shot success logic
        return True, goal_scored

    def simulate_game(self):
        self.kickoff()

        for tick in range(1, self.ticks + 1):
            attacking_team = self.team_a if self.possession == self.team_a else self.team_b
            player = random.choice(attacking_team)
            success, target_sector = self.simulate_event(player, self.current_sector, tick)
            if not success:
                if tick % 90 == 0:
                    self.kickoff()
                else:
                    self.possession = self.team_b if self.possession == self.team_a else self.team_a
                    self.current_sector = 5
            if success:
                if player.position == "defender":
                    print(f"Minute {tick}: {player.player_name} ({player.team}) tackled the attacker in the penalty area.")
                elif player.position == "midfielder":
                    print(f"Minute {tick}: {player.player_name} ({player.team}) intercepted the pass in the midfield.")
                elif player.position == "forward":
                    print(f"Minute {tick}: {player.player_name} ({player.team}) dribbled past the defender in the opponent's half.")
                else:
                    if tick % 90 == 0:
                        print(f"Minute {tick}: {player.player_name} ({player.team}) got the ball in the midfield after kickoff.")
                    else:
                        print(f"Minute {tick}: {player.player_name} ({player.team}) got the ball in the penalty area.")

            # Check if halftime or end of game
            if tick % 90 == 0:
                if tick != self.ticks:
                    print("Halftime!")
                    self.kickoff()  # Start the second half
                else:
                    print("End of game.")
                    break

        print("Final Score:")
        print(f"Team A: {self.score['Team A']} - Team B: {self.score['Team B']}")
        print("Goals:")
        for team, goals in self.score.items():
            print(f"{team}: {goals}")


# Load players from CSV
players = load_players_from_csv('player_data.csv')

# Separate players by team
team_a = [p for p in players if p.team == 'Team A']
team_b = [p for p in players if p.team == 'Team B']

# Define the Match object and simulate the game
match = Match(team_a, team_b)
match.simulate_game()
