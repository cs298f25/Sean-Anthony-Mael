from flask import Flask, jsonify, request, render_template
from todo_list import TodoList


def todo_list_to_list_of_dict(items):
    """
    Convert a list of TodoItems into a list of dicts
    [(description='d1', category='c1')] would be converted to
    [{'description': 'd1', 'category': 'c1'}]
    :param items: a list of TodoItems, possibly empty
    :return: an equivalent list of dicts
    """
    # See https://docs.python.org/3/library/collections.html#collections.somenamedtuple._asdict
    return [item._asdict() for item in items]


def create_app(todo_list):
    """
    Create the Flask application.
    :param todo_list: the TodoList instance to use
    """

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/todos")
    def todos():
        # None if not present, but that works with the optional param to get_list
        category = request.args.get("category")
        return (
            jsonify(
                {
                    "data": todo_list_to_list_of_dict(
                        todo_list.get_list(category=category)
                    )
                }
            ),
            200,
        )

    @app.route("/add", methods=["POST"])
    def add():
        description = request.form.get("description")
        if description is None:
            return "Missing description", 400
        category = request.form.get("category")
        if category is None:
            return "Missing category", 400
        todo_list.add(description, category)
        return "", 200

    return app


def launch():
    return create_app(TodoList())


if __name__ == "__main__":
    app = create_app(TodoList())
    app.run(debug=True, port=8000, host="0.0.0.0")
