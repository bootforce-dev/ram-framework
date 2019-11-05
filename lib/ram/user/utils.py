import random
import string
import pwquality

import ram.context


with ram.context(__name__):
    from wiz.utils import ValidateNonEmpty


_first_chars = string.ascii_letters
_other_chars = string.ascii_letters + string.digits + '-'


def ValidateUsername(value, banned=None):
    if banned is not None and value in banned:
        raise ValueError("cannot be `%s`" % value)
    elif len(value) >= 31:
        raise ValueError("too long")
    elif not (((value[0] in _first_chars) if value else True) and all(c in _other_chars for c in value)):
        raise ValueError("contains symbols that aren't allowed")
    else:
        return ValidateNonEmpty(value)


def ValidateDictPath(dictpath):
    if dictpath is None:
        return dictpath
    elif dictpath == '-':
        dictpath = ''

    pwqs = pwquality.PWQSettings()
    pwqs.dictpath = dictpath

    try:
        pwqs.generate(0)
    except pwquality.PWQError as e:
        raise ValueError()

    return dictpath


def ValidatePassword(password, username=None, dictpath=None):
    pwqs = pwquality.PWQSettings()
    pwqs.difok = min(5, (min(len(username), len(password)) + 1) / 2)
    pwqs.minlen = 8
    pwqs.ucredit = 0
    pwqs.lcredit = 0
    pwqs.dcredit = 0
    pwqs.ocredit = 0
    pwqs.minclass = 3
    pwqs.dictpath = dictpath

    try:
        try:
            pwqs.check(password, username, None)
        except pwquality.PWQError as e:
            if e.args[0] == -9:
                pwquality.PWQSettings().check('12345678', None, '12345678')
            elif e.args[0] == -22 and dictpath is None:
                pass
            else:
                raise
    except pwquality.PWQError as e:
        raise ValueError(e.args[1].lower())

    return password


ValidatePasswordRequirements = (
    "The following requirements are in effect:\n"
    "  - it must be at least 8 characters long;\n"
    "  - it must contain at least 3 different\n"
    "    groups of symbols: latin lowercase, latin\n"
    "    uppercase, digits and special symbols;\n"
    "  - it can not be similar to username.\n"
)


def ValidateBasePassword(password, username, dictpath=None):
    return ValidatePassword(password, username, dictpath)


def ValidateSamePassword(password, password_, username, dictpath=None):
    if not password == password_:
        raise ValueError("doesn't match")
    else:
        return (
            ValidateNonEmpty(password) and
            ValidateBasePassword(password, username, dictpath)
        )


def GenerateSalt(len=8):
    return "".join(random.choice(string.ascii_letters + string.digits + "./") for n in range(len))


def HiddenText(s):
    return "".join("*" for c in s)
