import re
import string

class PersianTextCleaner:
    def __init__(self, filename):
        self.stopwords = []
        with open(filename) as f:
            stopwords = f.readlines()

        for word in stopwords:
            self.stopwords.append(word.strip())

        self.emoji_pattern = re.compile("["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        u'\U0001F1F2-\U0001F1F4'  # Macau flag
                                        u'\U0001F1E6-\U0001F1FF'  # flags
                                        u"\U00002702-\U000027B0"
                                        u"\U000024C2-\U0001F251"
                                        u"\U00002700-\U000027BF"
                                        u"\U00010000-\U0010ffff"
                                        "]+", flags=re.UNICODE)

        self.link_pattern = re.compile(
            # "https?:\/\/.*[ ]", flags=re.MULTILINE)
            "http\S+", flags=re.MULTILINE)

        self.username_pattern = re.compile('@[\w]+')

        self.persian_punctuation = re.compile('[٪؟؟‌؛،٬‌]')

    def clean(self, str):
        str = self.remove_emoji(str)
        str = self.remove_usernames(str)
        str = self.remove_numbers(str)
        str = self.remove_links(str)
        str = self.remove_punctutions(str)
        str = self.remove_stopwords(str)

        return str

    def remove_emoji(self, str):
        return self.emoji_pattern.sub(r'', str)

    def remove_links(self, str):
        return self.link_pattern.sub(r'', str)

    def remove_usernames(self, str):
        return self.username_pattern.sub(r'', str)

    def remove_punctutions(self, str):
        str = self.persian_punctuation.sub(r'', str)
        return str.translate(str.maketrans('', '', string.punctuation))

    def remove_numbers(self, str):
        return ''.join(i for i in str if not i.isdigit())

    def remove_stopwords(self, str):
        querywords = str.split()
        resultwords = [word for word in querywords if word.lower()
                       not in self.stopwords]
        str = ' '.join(resultwords)

        return str

