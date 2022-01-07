# To-Do

## High Priorities

- PDF manager
  - Model
  - Viewset
    - CRUD
    - Permissions

## Medium Priorities

- Use JSONFields in place of CharFields where appropriate
- Encrypt database on OS level
- Metadata
  - Field attributes
    - type: _str_
    - required: _bool_
    - read\_only: _bool_
    - label: _str_
  - Endpoints
    - Search Word
    - Word
    - Get MP3
- Move external API managers to model managers
- `ExternalAPIManager.get_word_and_entries()`
  - Cache near-misses with suggestions
- Search endpoint
  - Check timestamps in get_word_and_entries

## Low Priorities

- Ensure dictionary responses are OrderedDicts
- Change verbiage of views to make sense for OPTIONS outputs
- Move password errors to password field in registration endpoint
- Change serializer imports to only include abstract.py
- Change TOKEN_REGEX to a regular expression object
- Remove unused imports
- Implement and test multiple errors on field and non-field bases
- Import camelCase library
