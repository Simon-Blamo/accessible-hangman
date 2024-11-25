from word_grade_classifier import WordGradeClassifier
import json

class WordLists:
    def __init__(self):
        self.classifier = WordGradeClassifier()
        self.grade_levels = {}
        self.custom_words = []
        self.load_or_create_word_lists()
        
    def load_or_create_word_lists(self):
        self.grade_levels = self.classifier.load_grade_levels()
        self.custom_words = self.load_custom_words()

    def add_custom_word(self, word):
        if word not in self.custom_words:
            self.custom_words.append(word)
            grade = self.classifier.assign_grade_level(word)
            self.grade_levels[grade].append(word)
            self.save_custom_words()
            self.classifier.save_grade_levels()

    def remove_custom_word(self, word):
        if word in self.custom_words:
            self.custom_words.remove(word)
            for grade in self.grade_levels:
                if word in self.grade_levels[grade]:
                    self.grade_levels[grade].remove(word)
            self.save_custom_words()
            self.classifier.save_grade_levels()

    def load_custom_words(self):
        try:
            with open('custom_words.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_custom_words(self):
        with open('custom_words.json', 'w') as f:
            json.dump(self.custom_words, f)
