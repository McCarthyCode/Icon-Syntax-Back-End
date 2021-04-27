import re
import string

from django.utils.translation import gettext_lazy as _, ngettext_lazy as _n

from rest_framework.exceptions import ValidationError


class ContainsUppercaseValidator:
    """
    Validate whether the password contains a specified minimum number of uppercase letters.
    """
    def __init__(self, min_chars=1):
        assert min_chars > 0, _(
            'Minimum character limit for ContainsUppercaseValidator must be at least %{min_chars}.'
        ) % {
            'min_chars': min_chars
        }
        self.min_chars = min_chars

    def validate(self, password, user=None):
        if len(re.findall(r'[A-Z]', password)) < self.min_chars:
            raise ValidationError(
                self.get_help_text(), 'password_missing_upper')

    def get_help_text(self):
        return _n(
            'Your password must contain at least %(min_chars)d uppercase character.',
            'Your password must contain at least %(min_chars)d uppercase characters.',
            self.min_chars) % {
                'min_chars': self.min_chars
            }


class ContainsLowercaseValidator:
    """
    Validate whether the password contains a specified minimum number of lowercase letters.
    """
    def __init__(self, min_chars=1):
        assert min_chars > 0, _(
            'Minimum character limit for ContainsLowercaseValidator must be at least %{min_chars}.'
        ) % {
            'min_chars': min_chars
        }
        self.min_chars = min_chars

    def validate(self, password, user=None):
        if len(re.findall(r'[a-z]', password)) < self.min_chars:
            raise ValidationError(
                self.get_help_text(), 'password_missing_lower')

    def get_help_text(self):
        return _n(
            'Your password must contain at least %(min_chars)d lowercase character.',
            'Your password must contain at least %(min_chars)d lowercase characters.',
            self.min_chars) % {
                'min_chars': self.min_chars
            }


class ContainsNumberValidator:
    """
    Validate whether the password contains a specified minimum number of numbers.
    """
    def __init__(self, min_nums=1):
        assert min_nums > 0, _(
            'Minimum character limit for ContainsNumberValidator must be at least %{min_nums}.'
        ) % {
            'min_nums': min_nums
        }
        self.min_nums = min_nums

    def validate(self, password, user=None):
        if len(re.findall(r'\d', password)) < self.min_nums:
            raise ValidationError(
                self.get_help_text(), 'password_missing_num')

    def get_help_text(self):
        return _n(
            'Your password must contain at least %(min_nums)d number.',
            'Your password must contain at least %(min_nums)d numbers.',
            self.min_nums) % {
                'min_nums': self.min_nums
            }


class ContainsPunctuationValidator:
    """
    Validate whether the password contains a specified minimum number of punctuation characters.
    """
    def __init__(self, min_chars=1):
        assert min_chars > 0, _(
            'Minimum character limit for ContainsPunctuationValidator must be at least %{min_chars}.'
        ) % {
            'min_chars': min_chars
        }
        self.min_chars = min_chars

    def validate(self, password, user=None):
        if len(re.findall(r'[!"#$%&\'()*+,-.\/:;<=>?@\[\\\]^_`{|}~]',
                          password)) < self.min_chars:
            raise ValidationError(self.get_help_text(), 'password_missing_punc')

    def get_help_text(self):
        return _(
            'Your password must contain at least %(min_chars)d of the following punctuation characters: %(punctuation)s'
        ) % {
            'min_chars': self.min_chars,
            'punctuation': string.punctuation,
        }
