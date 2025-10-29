
"""
A simple TodoList where each item is made up of a description and
a category.  The class supports adding and removing items one at a time,
and getting the items with an optional category filter.
"""
from collections import namedtuple

# A namedtuple is quick way to create a class-like type
# where the fields are accessible such as todo_item.description
# See https://docs.python.org/3/library/collections.html#collections.namedtuple
TodoItem = namedtuple('TodoItem', ['description', 'category'])


class DuplicateException(Exception):
    """
    Exception to indicate an attempt to add a duplicate TodoItem
    """
    pass


class NoSuchItemException(Exception):
    """
    Exception to indicate that a TodoItem is not found
    """
    pass


class TodoList:
    """
    A collection of TodoItems.
    """

    def __init__(self):
        """
        Create an instance with no items.
        """
        self.items = []

    def get_list(self, category=None):
        """
        Get the current items
        :param category: a category to filter on
        :return: a list of TodoItems, possibly empty
        """
        if category is None:
            return self.items
        # See https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        # For a discussion of the list comprehension sytax
        return [item for item in self.items if item.category == category]

    def contains(self, description, category):
        """
        Determine if a TodoItem is currently in the TodoList
        :param description: description to search for
        :param category: category to search for
        :return: True if a TodoItem matching both values is present
        """
        to_check = TodoItem(description, category)
        return to_check in self.items

    def add(self, description, category):
        """
        Add an TodoItem to the TodoList
        :param description: the item description
        :param category: the item category
        :return: None
        :raises: DuplicateException if the TodoItem is already present
        """
        to_add = TodoItem(description, category)
        if to_add in self.items:
            raise DuplicateException()

        self.items.append(to_add)

    def remove(self, description, category):
        """
        Remove a TodoItem from the TodoList
        :param description: the description of the item
        :param category: the category of the item
        :return: None
        :raises: NoSuchItemException if no item matchs both values
        """
        to_remove = TodoItem(description, category)
        if to_remove not in self.items:
            raise NoSuchItemException()
        self.items.remove(to_remove)

