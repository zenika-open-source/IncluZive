from typing import Tuple, List


def annotation_to_bio_tags(text: str, annotations: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    token_dict = {token: "O" for token in text.split()}
    tagged_tokens = [(annotation[0].split(), annotation[1]) for annotation in annotations]
    tagged_tokens = [
        (token, f"{'I' if i > 0 else 'B'}-{tag}") for tokens, tag in tagged_tokens for i, token in enumerate(tokens)
    ]
    token_dict.update(tagged_tokens)
    return list(token_dict.items())
