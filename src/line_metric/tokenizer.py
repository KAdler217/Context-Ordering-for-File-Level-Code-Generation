from functools import lru_cache
import re


class TokenizerRegexp():
    def __init__(self):
        self._re = [
            # language-dependent part (assuming Western languages)
            (re.compile(r"([\{-\~\[-\` -\&\(-\+\:-\@\/])"), r" \1 "),
            # tokenize period and comma unless preceded by a digit
            (re.compile(r"([^0-9])([\.,])"), r"\1 \2 "),
            # tokenize period and comma unless followed by a digit
            (re.compile(r"([\.,])([^0-9])"), r" \1 \2"),
            # tokenize dash when preceded by a digit
            (re.compile(r"([0-9])(-)"), r"\1 \2 "),
            # one space only between words
            # NOTE: Doing this in Python (below) is faster
        ]

    @lru_cache(maxsize=2 ** 16)
    def __call__(self, line):
        """Common post-processing tokenizer for `13a` and `zh` tokenizers.
        :param line: a segment to tokenize
        :return: the tokenized line
        """
        for (_re, repl) in self._re:
            line = _re.sub(repl, line)

        # no leading or trailing spaces, single space within words
        # This line is changed with regards to the original tokenizer (seen above) to return individual words
        return line.split()


class Tokenizer13a():
    def __init__(self):
        self._post_tokenizer = TokenizerRegexp()

    @lru_cache(maxsize=2 ** 16)
    def __call__(self, line):
        """Tokenizes an input line using a relatively minimal tokenization
        that is however equivalent to mteval-v13a, used by WMT.
        :param line: a segment to tokenize
        :return: the tokenized line
        """

        # language-independent part:
        line = line.replace("<skipped>", "")
        line = line.replace("-\n", "")
        line = line.replace("\n", " ")

        if "&" in line:
            line = line.replace("&quot;", '"')
            line = line.replace("&amp;", "&")
            line = line.replace("&lt;", "<")
            line = line.replace("&gt;", ">")

        return self._post_tokenizer(f" {line} ")
