# To-Do

## High Priorities

- Finish custom auth app
  - Security changes to database structure
    - Encrypt username and email fields
    - Split database into auth and default
  - Settings updates
    - Set token timeouts and update email messages to say when links expire
    - Test and confirm RegisterVerify and PasswordForgotVerify cases where
      activation link has already been clicked
  - Set throttle limits
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

_None at this time._

## Low Priorities

- Change verbiage of views to make sense for OPTIONS outputs
- Move password errors to password field in registration endpoint
- Change serializer imports to only include abstract.py
- Change TOKEN_REGEX to a regular expression object
- Remove unused imports
- Implement and test multiple errors on field and non-field bases
- Import camelCase library
