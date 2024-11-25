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

    def count_syllables(self, word: str) -> int:
        word = word.lower()
        try:
            return len([ph for ph in self.phoneme_dict[word][0] if ph.strip(string.ascii_letters)])
        except KeyError:
            count = 0
            vowels = 'aeiouy'
            word = word.lower()
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith('e'):
                count -= 1
            if count == 0:
                count += 1
            return count

    def calculate_complexity_score(self, word: str) -> float:
        word = word.lower()
        score = 0.0
        
        length = len(word)
        score += min(length / 3, 5)
        
        syllables = self.count_syllables(word)
        score += syllables * 0.6
        
        patterns = {
            r'([^aeiou]{3,})': 1.0,
            r'(ph|th|ch|sh|wh)': 0.5,
            r'(tion|sion)': 1.0,
            r'(pre|sub|trans)': 0.5,
            r'(ing|ed|ly|er|est)': 0.3,
            r'([^aeiou]y)': 0.3,
            r'([aeiou]{2,})': 0.4,
        }
        
        for pattern, weight in patterns.items():
            if re.search(pattern, word):
                score += weight
                
        return score

    def assign_grade_level(self, word: str) -> str:
        score = self.calculate_complexity_score(word)
        
        thresholds = {
            'K': 2,    '1': 3,    '2': 4,    '3': 5,
            '4': 6,    '5': 7,    '6': 8,    '7': 9,
            '8': 10,   '9': 11,   '10': 12,  '11': 13,
            '12': 14
        }
        
        for grade, threshold in thresholds.items():
            if score <= threshold:
                return grade
        return '12'

    def classify_word_list(self, words: List[str]) -> Dict[str, List[str]]:
        self.grade_levels = {grade: [] for grade in self.grade_levels.keys()}
        
        for word in words:
            word = word.strip().lower()
            if word and word.isalpha():
                grade = self.assign_grade_level(word)
                self.grade_levels[grade].append(word)
        
        return self.grade_levels

    def save_grade_levels(self, filename: str = 'grade_level_words.json'):
        with open(filename, 'w') as file:
            json.dump(self.grade_levels, file, indent=2)

    def load_grade_levels(self, filename: str = 'grade_level_words.json') -> Dict[str, List[str]]:
        try:
            with open(filename, 'r') as file:
                self.grade_levels = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found. Creating new classifications...")
            words = list(self.words)[:5000]
            self.classify_word_list(words)
            self.save_grade_levels()
        return self.grade_level