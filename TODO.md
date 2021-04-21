# To-Do

## High Priorities

- Finish custom auth app
  - Forgot password
    - Enter email and send reset link
    - Reset with code and new password
  - Change password
    - Reset with code and new password
- Create dictionary app
  - Define class structure
    - Abstract models
      - TimestampedModel
        - date_created
        - date_updated
    - Interfaces
      - Word
        - get_entries()
        - is_homograph()
        - get_word()
    - Enumerations
      - IconCategory
        - adjective
        - adverb
        - connective
        - noun
        - preposition
        - punctuation
        - verbIrregular
        - verbModal
        - verbRegular
        - verbTwoPart
    - Models
      - DictionaryEntry
        - id
        - icon
        - mp3
        - data
        - get_data()
        - set_data(str)
      - SingleEntry
      - Homograph
        - dictionary_entries
      - SearchTerm
        - id
        - get_words()
      - SearchResult
        - id
        - term
        - word
      - MP3
        - id
        - data
        - get_data_b64()
      - Icon
        - id
        - data
        - category
        - get_data_b64()
        - get_dictionary_entries()

## Medium Priorities

- Change format of Response objects from HTML to JSON

## Low Priorities

- Work out any translation bugs
- Move password errors to password field in registration endpoint
- Change serializer imports to only include abstract.py
