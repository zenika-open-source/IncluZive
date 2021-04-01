from difflib import SequenceMatcher

import pandas as pd


def matcher(string, pattern):
    """
    Return the start and end index of any pattern present in the text.
    """
    match_list = []
    pattern = pattern.strip()
    seq_match = SequenceMatcher(None, string, pattern, autojunk=False)
    match = seq_match.find_longest_match(0, len(string), 0, len(pattern))
    if match.size == len(pattern):
        start = match.a
        end = match.a + match.size
        match_tup = (start, end)
        string = string.replace(pattern, "X" * len(pattern), 1)
        match_list.append(match_tup)

    return match_list, string


def mark_sentence(s, match_list):
    """
    Marks all the entities in the sentence as per the BIO scheme.
    """
    word_dict = {word: 'O' for word in s.split()}

    for start, end, e_type in match_list:
        temp_str = s[start:end]
        tmp_list = temp_str.split()
        if len(tmp_list) > 1:
            word_dict[tmp_list[0]] = 'B-' + e_type
            for w in tmp_list[1:]:
                word_dict[w] = 'I-' + e_type
        else:
            word_dict[temp_str] = 'B-' + e_type
    return word_dict


def clean(text):
    """
    Just a helper function to add a space before the punctuations for better tokenization
    """
    filters = ["!", "#", "$", "%", "&", "(", ")", "/", "*", ".", ":", ";", "<", "=", ">", "?", "@", "[",
               "\\", "]", "_", "`", "{", "}", "~", "'"]
    for i in text:
        if i in filters:
            text = text.replace(i, " " + i)

    return text


def create_data(df, filepath):
    """
    The function responsible for the creation of data in the said format.
    """
    with open(filepath, 'w') as f:
        for text, annotation in zip(df.text, df.annotation):
            text = clean(text)
            match_list = []
            for i in annotation:
                a, text_ = matcher(text, i[0])
                match_list.append((a[0][0], a[0][1], i[1]))

            d = mark_sentence(text, match_list)

            for i in d.keys():
                f.writelines(i + ' ' + d[i] + '\n')
            f.writelines('\n')


def main():
    data = pd.DataFrame([["Horses are too tall and they pretend to care about your feelings", [("Horses", "ANIMAL")]],
                         ["Who is Shaka Khan?", [("Shaka Khan", "PERSON")]],
                         ["I like London and Berlin.", [("London", "LOCATION"), ("Berlin", "LOCATION")]],
                         ["There is a banyan tree in the courtyard", [("banyan tree", "TREE")]]],
                        columns=['text', 'annotation'])

    filepath = 'train.txt'
    create_data(data, filepath)


if __name__ == '__main__':
    main()
