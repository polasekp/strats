import re
import string

import pandas as pd
import unidecode
from numpy.random import choice
import random
from activities.models import Activity


ACTIVITY_TYPE = Activity.TYPE.RIDE

dict_df = pd.DataFrame(columns=["lead", "follow", "freq"])
words = []


def collect_all_words():
    # for activity in Activity.objects.filter(type=ACTIVITY_TYPE):
    for activity in Activity.objects.all():
        name = activity.name
        name = unidecode.unidecode(name.lower().translate(str.maketrans('', '', string.punctuation)))
        name_split = name.split(" ")
        for word in name_split:
            if word not in ("ride", "afternoon", "lunch", " ", "") and not (word.isdigit() and len(word) > 4):
                words.append(word)


def is_valid_word(word):
    return word not in ("ride", "afternoon", "lunch", " ", "") and not (word.isdigit() and len(word) > 4)


lead = []
follow = []
words = set()
def fill_dict_df():
    for activity in Activity.objects.all():
        name = activity.name
        name = unidecode.unidecode(name.lower().translate(str.maketrans('', '', string.punctuation)))
        name_split = name.split(" ")
        for i in range(len(name_split) - 1):
            lead_word = name_split[i]
            follow_word = name_split[i + 1]
            if is_valid_word(lead_word) and is_valid_word(follow_word):
                lead.append(lead_word)
                follow.append(follow_word)
                words.add(follow_word)
                words.add(lead_word)

    dict_df["lead"] = lead
    dict_df["follow"] = follow


fill_dict_df()
# dict_df["lead"] = words
# follow = words[1:]
# follow.append("EndWord")
# dict_df["follow"] = follow

end_words = []
for word in words:
    try:
        if word[-1] in [".", "!", "?"] and word != ".":
            end_words.append(word)
    except IndexError:
        continue

dict_df["freq"] = dict_df.groupby(by=["lead", "follow"])[["lead", "follow"]].transform("count").copy()


dict_df = dict_df.drop_duplicates()
pivot_df = dict_df.pivot(index="lead", columns="follow", values="freq")

sum_words = pivot_df.sum(axis=1)
pivot_df = pivot_df.apply(lambda x: x / sum_words)


def choose_not_used_word(sentence):
    for _ in range(100):
        next_word = random.sample(words, 1)[0]
        if next_word not in sentence:
            return next_word
    return "word"


def choose_random_starting_with(start):
    found_words = []
    for word in words:
        if word.startswith(start):
            found_words.append(word)
    return random.choice(found_words) if len(found_words) > 0 else None


def get_next_word(word, sentence):
    try:
        next_word = choice(a=list(pivot_df.columns), p=pivot_df.iloc[pivot_df.index == word].fillna(0).values[0])
    except (IndexError, ValueError):
        next_word = choose_not_used_word(sentence)
    return next_word


def make_a_sentence(start=None, length=None):
    if start is None:
        start = random.choice(lead)

    elif start not in words:
        start = choose_random_starting_with(start)
        if not start:
            print(f"{start} not in words")
            return

    if length is None:
        length = random.randint(3, 10)

    word = start
    sentence = [word]
    while len(sentence) < length:
        next_word = get_next_word(word, sentence)
        if next_word == "EndWord":
            continue
        elif next_word in end_words:
            if len(sentence) > 2:
                sentence.append(next_word)
                break
            else:
                continue
        else:
            sentence.append(next_word)
        word = next_word

    # we want to end up with follow word (not lead word)
    while sentence[-1] not in follow:
        print(f"Searching next word for {sentence[-1]}")
        next_word = get_next_word(word, sentence)
        sentence.append(next_word)
        word = next_word

    sentence[0] = sentence[0].capitalize()
    sentence = " ".join(sentence)
    return sentence
