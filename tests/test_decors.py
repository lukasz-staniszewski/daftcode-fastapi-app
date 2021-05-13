import unittest
from decorators.decor import (
    greetings,
    is_palindrome,
    format_output,
    add_instance_method,
    add_class_method,
)


class ExampleClass:
    pass


@add_class_method(ExampleClass)
def cls_method():
    return "Hello!"


@add_instance_method(ExampleClass)
def inst_method():
    return "Hello!"


class ExampleTest(unittest.TestCase):
    @greetings
    def show_greetings(self):
        return "joe doe"

    @is_palindrome
    def show_sentence(self):
        return "annA"

    @format_output("first_name")
    def show_dict(self):
        return {
            "first_name": "Jan",
            "last_name": "Kowalski",
        }

    @format_output("first_name__last_name", "city")
    def first_func(self):
        return {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "city": "Warszawa",
        }

    @format_output("first_name", "age")
    def second_func(self):
        return {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "city": "Warszawa",
        }

    def test_greeting(self):
        self.assertEqual(self.show_greetings(), "Hello Joe Doe")

    def test_classes(self):
        self.assertEqual(ExampleClass.cls_method(), cls_method())
        self.assertEqual(ExampleClass().inst_method(), inst_method())

    def test_palindrome(self):
        self.assertEqual(self.show_sentence(), "annA - is palindrome")

    def test_formatting(self):
        self.assertEqual(self.show_dict(), {"first_name": "Jan"})
        self.assertEqual(
            self.first_func(),
            {"first_name__last_name": "Jan Kowalski", "city": "Warszawa"},
        )
        self.assertRaises(ValueError, self.second_func)


if __name__ == "__main__":
    unittest.main()
