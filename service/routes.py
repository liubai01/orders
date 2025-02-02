"""
My Service

The orders resource is a collection of order items where each item represents a
product id, its quantity, and its price.
We also implement a subordinate REST API to add order items to the order collection
(e.g., /orders/{id}/items) and associate the order with a customer preferably through
its customer id. A good action for the order API is to be able to cancel an order.

"""

from flask import abort, jsonify, request, url_for, render_template
from service.models import Item, Order

# Import Flask application
from . import app
from .common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return render_template("index.html")
    # return (
    #     jsonify(
    #         name="Order Demo REST API Service",
    #         version="1.0",
    #         paths=url_for("list_orders", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for order list")
    orders = Order.all()

    results = [o.serialize() for o in orders]
    app.logger.info("Returning %d items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single order

    This endpoint will return an Order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Item with id '{order_id}' was not found.")

    app.logger.info("Returning item: %s", order.name)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Add a new order
    This endpoint will create an order based the data in the body that is posted
    """
    app.logger.info("Request to create an order")
    check_content_type("application/json")
    order = Order()
    order.deserialize(request.get_json())
    order.create()
    message = order.serialize()
    location_url = url_for("get_orders", order_id=order.id, _external=True)

    app.logger.info("Order with ID [%s] created.", order.id)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update a Order
    This endpoint will update a Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")

    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    app.logger.info("Order with ID [%s] updated.", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order
    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to delete pet with id: %s", order_id)
    order_obj = Order.find(order_id)

    if not order_obj:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")

    items_retrieve = Item.find_by_order_id(order_id)
    if items_retrieve:
        items_retrieve.delete()

    if order_obj:
        order_obj.delete()

    app.logger.info("Order with ID [%s] delete complete.", order_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ITEM DETAILS
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def list_item(order_id, item_id):
    """Returns particular item of the Order based on its id"""
    app.logger.info("Request for item with id [%s]", item_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")
    app.logger.info(item_id)
    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND,
              f"Item with id '{item_id}' was not found.")

    app.logger.info("Get item details successful")
    return item.serialize(), status.HTTP_200_OK


######################################################################
# LIST ITEMS
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_all_items(order_id):
    """Returns all of the Items for an Order"""
    app.logger.info("Request for all Items for Order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")

    results = [item.serialize() for item in order.items]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Item
    This endpoint will delete an item based on its order_id & item_id
    """
    app.logger.info(
        "Request to delete item with order_id [%s] and item_id [%s]", order_id, item_id)

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")
    item = Item.find(item_id)
    if item:
        item.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# ADD A NEW ITEM
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_items(order_id):
    """
    Add a new item
    This endpoint will create an items based the data in the body that is posted
    """
    app.logger.info("Request to create an item for order")
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")

    data = request.get_json()

    app.logger.debug("Payload = %s", data)
    item = Item()
    item.deserialize(data)
    item.order_id = order_id
    item.create()

    app.logger.info("Item for order ID [%s] created.", id)

    return item.serialize(), status.HTTP_201_CREATED


######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_item(order_id, item_id):
    """
    Update an Item
    This endpoint will update an Item based the body that is posted
    """
    app.logger.info(
        "Request to update Order %s for Item id: %s", (item_id, order_id)
    )
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Item with id '{order_id}' was not found.")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK

######################################################################
# QUERY BASED ON DATE
######################################################################


@app.route("/orders/date/<date_iso>", methods=["Get"])
def order_retrieve_based_on_date(date_iso):
    """
    Retrieve order lists based on date created
    This endpoint will return a list of orders created on a specific date
    """
    app.logger.info(
        "Request to retrieve Orders based on date %s", (date_iso)
    )
    # check_content_type("application/json")

    order_list = list(Order.find_by_date(date_iso))

    if not order_list:
        abort(status.HTTP_404_NOT_FOUND,
              f"No order was found for date '{date_iso}'")

    ret = []
    for order in order_list:
        ret.append(order.serialize())
    return jsonify(ret), status.HTTP_200_OK


######################################################################
# LIST ALL ITEMS IN ORDER IN PRICE RANGE
######################################################################
@app.route("/orders/prices", methods=["GET"])
def list_all_items_prices():
    """
    Returns all of Orders with items between max and min price
    """
    app.logger.info("Request for all Orders in the price range")

    max_price = request.args.get('max_price')
    min_price = request.args.get('min_price')

    item_list = Item.find_by_price(max_price, min_price)
    if not item_list:
        abort(status.HTTP_404_NOT_FOUND, "Items not found")

    results = [item.serialize() for item in item_list]
    list_order_id = {}
    for order_id in results:
        list_order_id.setdefault(order_id["order_id"], []).append(order_id)
    order_final = []
    for key, value in list_order_id.items():
        res = {}
        order = Order.find(key)
        res["id"] = order.id
        res["name"] = order.name
        res["address"] = order.address
        res["date_created"] = order.date_created.isoformat()
        res["items"] = value
        order_final.append(res)

    return jsonify(order_final), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Item.init_db(app)
    Order.init_db(app)


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s",
                     request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
