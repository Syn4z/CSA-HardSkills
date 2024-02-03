import os


def play_rps(player1_choice, player2_choice):
    if player1_choice == player2_choice:
        return player1_choice
    elif (
            (player1_choice == 'R' and player2_choice == 'S') or
            (player1_choice == 'S' and player2_choice == 'P') or
            (player1_choice == 'P' and player2_choice == 'R')
    ):
        return player1_choice
    else:
        return player2_choice


def process_input_file(input_file_path):
    with open(input_file_path, "r") as input_file:
        lines = input_file.read().splitlines()

    n = int(lines[0])
    fight_choices = lines[1:]

    output_file_path = input_file_path.rsplit('.', 1)[0] + ".out"

    with open(output_file_path, "w") as file:
        for i in range(n):
            player1_choice, player2_choice = fight_choices[i][0], fight_choices[i][1]
            outcome = play_rps(player1_choice, player2_choice)
            file.write(outcome + "\n")


def main():
    input_files = [filename for filename in os.listdir() if filename.endswith(".in")]

    if not input_files:
        print("No input files found in the directory.")
        return

    for input_file in input_files:
        print(f"Processing {input_file}...")
        process_input_file(input_file)
        print(f"{input_file} processed successfully.")


if __name__ == "__main__":
    main()
