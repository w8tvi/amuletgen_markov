import os
import random
import hashlib
import markovify
from multiprocessing import Pool
import time
from collections import Counter
import csv
from datetime import datetime

def generate_markov_text(model, length):
    """Generate text using a Markov chain model."""
    text = model.make_short_sentence(length)
    return text

def is_amulet(text):
    """Check if a text is an amulet."""
    utf8_text = text.encode('utf-8')
    if len(utf8_text) > 64:
        return False, ""
    hash_obj = hashlib.sha256(utf8_text)
    hash_hex = hash_obj.hexdigest()
    return '8888' in hash_hex, hash_hex

def determine_rarity(hash_value):
    """Determine the rarity of the amulet based on its hash."""
    for i in range(10, 3, -1):
        if '8' * i in hash_value:
            return {
                10: "???",
                9: "mythic",
                8: "legendary",
                7: "epic",
                6: "rare",
                5: "uncommon",
                4: "common",
            }[i]
    return "not an amulet"

def generate_and_check_amulet(model):
    """Generate text and check if it's an amulet."""
    text = generate_markov_text(model, 64)
    if text:  # Ensure text is not None
        amulet_found, hash_value = is_amulet(text)
        if amulet_found:
            return text, hash_value
    return None, None



def find_amulets(num_processes, num_attempts, model):
    with Pool(num_processes) as pool:
        results = pool.starmap(generate_and_check_amulet, [(model,)] * num_attempts)
    return [result for result in results if result[0] is not None]

def main():
    start_time = time.time()
    num_processes = 20
    num_attempts = 500000
    
    print(f"Run Configuration:")
    print(f"Processes used: {num_processes}")
    print(f"Attempts tried: {num_attempts}")

    print("Loading text data...")
    with open('markov.txt', 'r', encoding='utf-8') as file:
        text_data = file.read()

    print("Building Markov model...")
    text_model = markovify.Text(text_data)

    # Get the current timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Finding amulets...")
    amulets = find_amulets(num_processes, num_attempts, text_model)

    # Define a simple rarity ranking for sorting
    rarity_ranking = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5, "mythic": 6, "???": 7}

    # Sort amulets by rarity
    sorted_amulets = sorted(amulets, key=lambda x: rarity_ranking[determine_rarity(x[1])])

    # Write sorted amulets to a CSV file
    csv_file = 'found_amulets.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Timestamp', 'Text', 'SHA-256 Hash', 'Rarity']) # Writing headers

        for amulet in sorted_amulets:
            text, hash_value = amulet
            rarity = determine_rarity(hash_value)
            writer.writerow([current_timestamp, text, hash_value, rarity])


    end_time = time.time()

    rarity_counter = Counter()
    unique_texts = set()
    total_length = 0

    if amulets:
        print("Amulets found:")
        for amulet in amulets:
            text, hash_value = amulet
            amulet_rarity = determine_rarity(hash_value)
            rarity_counter[amulet_rarity] += 1
            unique_texts.add(text)
            total_length += len(text)
            print(f"Amulet Text: {text}, SHA-256 Hash: {hash_value}, Rarity: {amulet_rarity}")
    else:
        print("No amulets found.")

    # Printing statistics
    print("\nStatistics:")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    print(f"Total Amulets Found: {len(amulets)}")
    print(f"Unique Texts Generated: {len(unique_texts)}")
    print(f"Average Text Length: {total_length / len(amulets) if amulets else 0:.2f} characters")
    print(f"Attempts per Amulet Found: {num_attempts / len(amulets) if amulets else 'Infinity'}")
    print("Amulets found by rarity:")
    for rarity, count in rarity_counter.items():
        print(f"{rarity}: {count}")
    print(f"CSV File: {csv_file}")

if __name__ == '__main__':
    main()