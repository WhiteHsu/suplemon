# -*- encoding:utf-8
import re
import helpers
from suplemon_module import Module


class AutoComplete(Module):
    def init(self):
        self.word_list = []
        self.bind_event("tab", self.auto_complete)
        self.bind_event_after("app_loaded", self.build_word_list)
        self.bind_event_after("save_file", self.build_word_list)
        self.bind_event_after("save_file_as", self.build_word_list)

    def get_separators(self):
        separators = self.app.config["editor"]["punctuation"]
        # Support words with underscores
        separators = separators.replace("_", "")
        return separators

    def build_word_list(self, *args):
        """Build word list based on contents of open files."""
        word_list = []
        for file in self.app.files:
            data = file.get_editor().get_data()
            words = helpers.multisplit(data, self.get_separators())
            for word in words:
                # Discard undesired whitespace
                word = word.strip()
                # Must be longer than 1 and not yet in word_list
                if len(word) > 1 and word not in word_list:
                    word_list.append(word)
        self.word_list = word_list
        return False

    def get_match(self, word):
        """Find a completable match for word."""
        if not word:
            return False
        # Build list of suitable matches
        candidates = []
        for candidate in self.word_list:
            if helpers.starts(candidate, word) and len(candidate) > len(word):
                candidates.append(candidate)
        # Find the shortest match
        shortest = ""
        for candidate in candidates:
            if not shortest:
                shortest = candidate
            else:
                if len(shortest) > len(candidate):
                    shortest = candidate
        if shortest:
            return shortest[len(word):]
        return False

    def run(self, app, editor):
        """Run the autocompletion."""
        self.auto_complete()

    def auto_complete(self, *args):
        """Attempt to autocomplete at each cursor position."""
        editor = self.app.get_editor()
        pattern = '|'.join(map(re.escape, self.get_separators()))
        matched = False
        for cursor in editor.cursors:
            line = editor.lines[cursor.y][:cursor.x]
            words = re.split(pattern, line)
            last_word = words[-1]
            match = self.get_match(last_word)
            if match:
                matched = True
                editor.type_at_cursor(cursor, match)
        return matched

module = {
    "class": AutoComplete,
    "name": "autocomplete",
}
