from collections import defaultdict
import math
import nltk

# Downloading the words corpus to be used
try:
    from nltk.corpus import words
except LookupError:
    print("NLTK 'words' corpus not found locally. Downloading now...")
    nltk.download("words")
    from nltk.corpus import words

# --- 1. CORE FEEDBACK LOGIC ---

def get_feedback(
        guess: str,
        answer: str,
) -> tuple[int, ...]:
    '''
    Core helper: Simulates a guess against a single answer  and returns the feedback pattern as a tuple of integers.
    
    2 = Green (correct letter, correct spot)
    1 = Yellow (correct letter, wrong spot)
    0 = Gray (letter not in word)
    '''
    length = len(guess)
    answer_chars = list(answer)
    guess_chars = list(guess)
    res = [0] * length
    
    # First pass: Check for Greens (2)
    for i in range(length):
        if guess_chars[i] == answer_chars[i]:
            res[i] = 2
            answer_chars[i] = None
            guess_chars[i] = None
            
    # Second pass: Check for Yellows (1)
    for i in range(length):
        if guess_chars[i] is not None:
            if guess_chars[i] in answer_chars:
                res[i] = 1
                answer_chars[answer_chars.index(guess_chars[i])] = None
            else:
                res[i] = 0          
    return tuple(res)

def get_feedback_buckets(
        guess: str,
        possible_answers: list[str],
) -> dict[str, list[str]]:
    '''
    Groups a list of possible answers into buckets based on the feedback they would produce for a given guess.
    '''
    buckets = defaultdict(list)
    for answer in possible_answers:
        feedback_pattern = get_feedback(guess, answer)
        buckets[feedback_pattern].append(answer)
    return dict(buckets)

# --- 2. ENTROPY & RANKING ---

def calculate_entropy(
        guess: str,
        possible_answers: list[str],
) -> float:
    '''
    Calculates the Shannon entropy (expected information in bits of a numeric guess given the current set of possible answers).
    '''
    if not possible_answers:
        return 0.0
        
    total_words = len(possible_answers)
    buckets = get_feedback_buckets(guess, possible_answers)
    
    entropy = 0.0

    # Shannon entropy contribution: - Σ [ P(x) * log2(P(x)) ]
    for pattern, bucket_words in buckets.items():
        probability = len(bucket_words) / total_words
        entropy -= probability * (math.log2(probability))       
    return entropy

def rank_all_guesses(
        guesses: list[str],
        possible_answers: list[str],
) -> list[tuple[str, float]]:
    '''
    Calculates entropy for a list of guesses against the possible answers and returns them sorted from highest to lowest entropy.
    '''
    guess_entropies = {}

    if len(possible_answers) == 1:
        print(f"\nOnly one possible answer left! Recommended Guess: {possible_answers[0]}")
        guess_entropies[possible_answers[0]] = 0
    
    else:
        for guess in guesses:
            entropy = calculate_entropy(guess, possible_answers)
            guess_entropies[guess] = entropy
        
    # Sort from highest entropy (most informative) to lowest
    sorted_guesses = sorted(guess_entropies.items(), key = lambda item: item[1], reverse = True)
    return sorted_guesses

def recommended_guess(
        guesses: list[str],
        possible_answers: list[str]
) -> None:
    '''
    Calculates and prints the recommended guesses.
    '''
    ranked_guess = rank_all_guesses(guesses, possible_answers)
    print_top_guesses(ranked_guess)

# --- 3. FILTERING FUNCTIONS ---

def filter_possible_answers(
        guess: str,
        actual_feedback: tuple[int, ...],
        possible_answers: list[str],
) -> list[str]:
    '''
    Filters the list of possible answers, keeping only the words that would produce the exact same feedback pattern against the guess.
    '''
    filtered_answers = []
    for answer in possible_answers:
        if get_feedback(guess, answer) == actual_feedback:
            filtered_answers.append(answer)
    return filtered_answers

def filter_guess_pool(
        guesses: list[str],
        rejected_letters: set[str],
        min_valid_chars: int = 1,
) -> list[str]:
    '''
    Filters the guess pool, keeping only words that contain at least  `min_valid_chars` characters that are NOT in the rejected letters set.
    '''
    filtered_guesses = []
    
    for word in guesses:
        # Count how many characters in this word are NOT rejected
        valid_char_count = sum(1 for char in word if char not in rejected_letters)
        
        # Keep the word if it meets the minimum threshold
        if valid_char_count >= min_valid_chars:
        
            filtered_guesses.append(word)
    return filtered_guesses

# --- 4. PRINTING FUNCTIONS ---

def print_top_guesses(
        ranked_guesses: list[tuple[str, float]],
        top_n: int = 5,
) -> None:
    '''
    
    '''
    print('Recommended Guesses')
    for i in range(min(top_n, len(ranked_guesses))):
        print(f'{ranked_guesses[i][0]}: {ranked_guesses[i][1]} bits')

def print_wordle_results(results: dict[str, tuple[int, ...]]) -> None:
    '''
    Prints previous Wordle guesses with color-coded feedback.
    '''
    # ANSI Background Color mappings
    BG_GREEN = "\033[42m\033[30m"   # Green background, black text for readability
    BG_YELLOW = "\033[43m\033[30m"  # Yellow background, black text
    BG_GRAY = "\033[100m\033[37m"   # Dark gray background, white text
    RESET = "\033[0m"

    for guess, feedback in results.items():
        display_row = []

        for char, code in zip(guess, feedback):
            if code == 2:
                display_row.append(f"{BG_GREEN} {char} {RESET}")
            elif code == 1:
                display_row.append(f"{BG_YELLOW} {char} {RESET}")
            else:
                display_row.append(f"{BG_GRAY} {char} {RESET}")

        print("".join(display_row))

def print_choices():
    '''
    Prints the available options for the user.
    '''
    print('1: Input guess word and placement')
    print('2: Print previous guesses')
    print('3: Get Recommened guess')
    print('4: Quit')

# --- 5. GAME STATE ---

def process_guess(
        possible_answers: list[str],
        guess_pool: list[str],
        previous_guesses: dict[str, tuple[int, ...]],
        known_letters: set[str],
        excluded_letters: set[str],
) -> tuple[list[str], list[str]]:
    '''
    Gets a guess and its feedback from the user, then updates the previous guesses, known letters, excluded letters, possible answers, and guess pool.
    '''
    guess = input('Enter a guess: ').upper()

    feedback = tuple(
        int(x)
        for x in input(
            'Enter the feedback separated by a space '
            '(2 = Green, 1 = Yellow, 0 = Gray): '
        ).split()
    )

    previous_guesses[guess] = feedback

    for letter, status in zip(guess, feedback):
        if status in (1, 2):
            known_letters.add(letter)

        elif status == 0 and letter not in known_letters:
            excluded_letters.add(letter)

    possible_answers = filter_possible_answers(
        guess,
        feedback,
        possible_answers
    )

    guess_pool = filter_guess_pool(
        guess_pool,
        excluded_letters
    )
    return possible_answers, guess_pool


if __name__ == "__main__":

    raw_words = words.words()
    word_len = int(input('Length of word guess: '))
    word_list = list(set(w.upper() for w in raw_words if len(w) == word_len and w.isalpha()))
    
    print(f"Loaded {len(word_list)} valid {word_len}-letter words from NLTK.")
    
    # Initialize game lists
    possible_answers = word_list.copy()
    guess_pool = word_list.copy()
    previous_guesses = {}

    known_letters = set()
    excluded_letters = set()

    while True:
        print_choices()
        choice = int(input('Enter choice: '))

        match choice:
            case 1:
                possible_answers, guess_pool = process_guess(
                    possible_answers,
                    guess_pool,
                    previous_guesses,
                    known_letters,
                    excluded_letters
                )
            case 2:
                print_wordle_results(previous_guesses)
            case 3:
                recommended_guess(guess_pool, possible_answers)
            case 4:
                quit()
            case _:
                print('Invalid Choice. Quitting')
                quit()