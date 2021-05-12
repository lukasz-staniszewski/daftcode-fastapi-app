# %%
from functools import wraps
import re

# %%
# GREETING DECORATOR
def greetings(function_orig):
    @wraps(function_orig)
    def wrapper(*args, **kwargs):
        result = function_orig(*args, **kwargs).title()
        return "Hello {}".format(result)

    return wrapper


# DECORATOR CHECKING PALINDROME
def is_palindrome(function_orig):
    @wraps(function_orig)
    def wrapper(*args, **kwargs):
        sentence = function_orig(*args, **kwargs)
        letters_numbers = re.sub("[^A-Za-z0-9Ą-Ż]", "", sentence).upper()
        reverse = letters_numbers[::-1]
        if letters_numbers == reverse:
            sentence += " - is palindrome"
        else:
            sentence += " - is not palindrome"
        return sentence

    return wrapper


# DECORATOR FORMATING OUTPUT
def format_output(*dec_args):
    def real_dec(to_dec):
        def wrapper(*args, **kwargs):
            dict_foo = to_dec(*args, **kwargs)
            dict_to_ret = dict([])
            for arg in dec_args:
                splitted = arg.split("__")
                resp = []
                for arg_spl in splitted:
                    if arg_spl not in dict_foo.keys():
                        raise ValueError
                    resp.append(dict_foo[arg_spl])
                dict_to_ret[arg] = " ".join(resp)
            return dict_to_ret

        return wrapper

    return real_dec


# DECORATOR MAKING FUNCTION AS METHOD OF GIVEN CLASS INSTANCE
def add_instance_method(ClassName):
    def real_dec(to_dec):
        def wrapper(self, *args, **kwargs):
            return to_dec(*args, **kwargs)

        # assigning method to class before executing
        setattr(ClassName, to_dec.__name__, wrapper)
        # now when function to decorate is returned, there is possibility
        # in code to run to_dec() without need to add 'ClassName().' before
        return to_dec

    return real_dec


# DECORATOR MAKING FUNCTION AS METHOD OF GIVEN CLASS
def add_class_method(ClassName):
    def real_dec(to_dec):
        def wrapper(*args, **kwargs):
            return to_dec(*args, **kwargs)

        # assigning method to class before executing
        setattr(ClassName, to_dec.__name__, wrapper)
        return wrapper

    return real_dec

# %%
@greetings
def welcome():
    return "adam sandler"
# %%
welcome()
# %%
