import nltk
nltk.download('words')
nltk.download('cmudict')
from nltk.corpus import words as nltk_words
from nltk.corpus import cmudict
import string
from typing import Dict, List
import json
import re

class WordGradeClassifier:
    def __init__(self):
        # Load phoneme dictionary and word list
        self.phoneme_dict = cmudict.dict()
        self.words = set(nltk_words.words())
        
        self.grade_levels = {
            'K': [],  # 3-4 letters, simple phonics
            '1': [],  # 4-5 letters, basic sight words
            '2': [],  # 5-6 letters, basic patterns
            '3': [],  # 6-7 letters, compound words
            '4': [],  # 7-8 letters, prefixes/suffixes
            '5': [],  # 8-9 letters, academic words
            '6': [],  # 9-10 letters, complex patterns
            '7': [],  # 10-11 letters, advanced vocabulary
            '8': [],  # 11-12 letters, scientific terms
            '9': [],  # 12-13 letters, specialized vocabulary
            '10': [], # 13-14 letters, advanced academic
            '11': [], # 14-15 letters, technical terms
            '12': []  # 15+ letters, professional vocabulary
        }

# Count syllables in a word using the phoneme dictionary or heuristic fallback
    def count_syllables(self, word: str) -> int:
        word = word.lower()  # Normalize to lowercase
        try:
            # Count phonemes that are not letters (syllable markers)
            return len([ph for ph in self.phoneme_dict[word][0] if ph.strip(string.ascii_letters)])
        except KeyError:
            # Heuristic method for words not in the phoneme dictionary
            count = 0
            vowels = 'aeiouy'
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith('e'):  # Silent 'e' handling
                count -= 1
            if count == 0:  # At least one syllable
                count += 1
            return count

    # Calculate a complexity score for a word based on length, syllables, and patterns
    def calculate_complexity_score(self, word: str) -> float:
        word = word.lower()  # Normalize to lowercase
        score = 0.0
        
        # Add points for word length
        length = len(word)
        score += min(length / 3, 5)
        
        # Add points for syllables
        syllables = self.count_syllables(word)
        score += syllables * 0.6
        
        # Add points for specific patterns
        patterns = {
            r'([^aeiou]{3,})': 1.0,  # Consonant clusters
            r'(ph|th|ch|sh|wh)': 0.5,  # Common digraphs
            r'(tion|sion)': 1.0,  # Suffixes
            r'(pre|sub|trans)': 0.5,  # Prefixes
            r'(ing|ed|ly|er|est)': 0.3,  # Common endings
            r'([^aeiou]y)': 0.3,  # 'y' as vowel
            r'([aeiou]{2,})': 0.4,  # Vowel clusters
        }
        
        for pattern, weight in patterns.items():
            if re.search(pattern, word):  # Match pattern
                score += weight
                
        return score

    # Assign a grade level to a word based on its complexity score
    def assign_grade_level(self, word: str) -> str:
        score = self.calculate_complexity_score(word)
        
        # Thresholds for each grade level
        thresholds = {
            'K': 2,    '1': 3,    '2': 4,    '3': 5,
            '4': 6,    '5': 7,    '6': 8,    '7': 9,
            '8': 10,   '9': 11,   '10': 12,  '11': 13,
            '12': 14
        }
        
        # Return the first grade level where the score is less than or equal to the threshold
        for grade, threshold in thresholds.items():
            if score <= threshold:
                return grade
        return '12'  # Default to the highest grade level

    # Classify a list of words into grade levels
    def classify_word_list(self, words: List[str]) -> Dict[str, List[str]]:
        # Reset grade level dictionary
        self.grade_levels = {grade: [] for grade in self.grade_levels.keys()}
        
        for word in words:
            word = word.strip().lower()  # Normalize and clean word
            if word and word.isalpha():  # Skip empty or non-alphabetic strings
                grade = self.assign_grade_level(word)
                self.grade_levels[grade].append(word)  # Add word to appropriate grade level
        
        return self.grade_levels

    # Save grade level classifications to a JSON file
    def save_grade_levels(self, filename: str = 'grade_level_words.json'):
        with open(filename, 'w') as file:
            json.dump(self.grade_levels, file, indent=2)

    # Load grade level classifications from a JSON file, or classify new words if file is missing
    def load_grade_levels(self, filename: str = 'grade_level_words.json') -> Dict[str, List[str]]:
        try:
            with open(filename, 'r') as file:
                self.grade_levels = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found. Creating new classifications...")
            words = list(self.words)[:5000]  # Use a subset of words for classification
            self.classify_word_list(words)
            self.save_grade_levels()
        return self.grade_levels