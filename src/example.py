# ;encoding=utf-8
# Example file to redact Social Security Numbers from the
# text layer of a PDF and to demonstrate metadata filtering.

import regex as re

import pdf_redactor

## Set options.

options = pdf_redactor.RedactorOptions()

options.metadata_filters = {
    # Clear all other fields.
    "DEFAULT": [lambda value: None],
}

# Clear any XMP metadata, if present.
options.xmp_filters = [lambda xml: None]

# Redact things that look like social security numbers, replacing the
# text with X's.
options.content_filters = [
    # First convert all dash-like characters to dashes.
    (
        re.compile(r"\Stephane"),
        lambda m: ''.ljust(len('Stephane'), '-')
    ),

    (
        re.compile(r"\Cohan"),
        lambda m: ''.ljust(len('Cohan'), '-')
    ),

    # Then do an actual SSL regex.
    # See https://github.com/opendata/SSN-Redaction for why this regex is complicated.
    (
        re.compile(
            r"(?<!\d)(?!666|000|9\d{2})([OoIli0-9]{3})([\s-]?)(?!00)([OoIli0-9]{2})\2(?!0{4})([OoIli0-9]{4})(?!\d)"),
        lambda m: "XXX-XX-XXXX"
    ),

    # Content filter that runs on the text comment annotation body.
    (
        re.compile(r"comment!"),
        lambda m: "annotation?"
    ),
]

# Filter the link target URI.
options.link_filters = [
    lambda href, annotation: "https://www.google.com"
]

# Perform the redaction using PDF on standard input and writing to standard output.
pdf_redactor.redactor(options)
