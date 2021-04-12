# To-Do

## High Priorities

- Finish custom auth app
  - Forgot password
    - Enter email and send reset link
    - Reset with code and new password
  - Change password
    - Reset with code and new password
- Create dictionary app
  - Define models

## Medium Priorities

*None at this time.*

## Low Priorities

- Refactor success and error messages
  - Define `default_error_messages` dictionary for use with `self.fail()` method
  - Add `gettext as _` methods to messages for later use in translation
  - Replace uses of `ValidationError` with `self.fail()` method
