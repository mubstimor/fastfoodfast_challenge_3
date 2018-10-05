""" Class to manage CRUD operations on order objects"""
import psycopg2
import psycopg2.extras
from api.database import DatabaseConnection

class Order(object):
    """docstring for Orders"""
    def __init__(self):
        """ define attributes for order. """
        self.db = DatabaseConnection()
        self.db.create_all_tables()

    def create_order(self, user_id, order_data):
        """ add order to orders list """
        order = order_data
        order['item'] = int(order_data['item'])
        order['quantity'] = str(order_data['quantity'])
        order['status'] = 'new'
        try:
            self.db.cursor.execute("INSERT INTO orders(item, quantity, status, user_id) \
                                VALUES('"+ str(order['item']) + "','"+ order['quantity'] +"', '"+ \
                                order['status']+"', '"+str(user_id)+"') RETURNING id")
            order_id = self.db.cursor.fetchone()[0]
            return order_id
        except (psycopg2.DatabaseError) as error:
            return
        
        
    def check_if_order_exists(self, user_id, item, quantity):
        """ retrieve order with given id. """
        self.db.cursor.execute("SELECT * FROM orders where user_id='"+str(user_id) \
            +"' AND item='"+ str(item)+"' AND quantity='"+ str(quantity)+"'")
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            return True

    def fetch_all_orders(self):
        """ retrieve all orders from db """
        self.db.cursor.execute("SELECT od.id as id, menu.name as item, od.quantity as quantity, cu.name as user_id, od.status as status \
                            FROM orders as od, users as cu, fooditems as menu \
                            WHERE od.id=cu.id and od.id=menu.item_id and od.status !='cancelled'")
        orderitems = self.db.cursor.fetchall()
        orders = []
        for item in orderitems:
            order = {"order_id": item['id'], "item": item['item'], "quantity": item['quantity'], "status": item['status'], "customer": item['user_id']}
            orders.append(order)
        return orders

    def fetch_user_orders(self, user_id):
        """ retrieve all orders from list """
        self.db.cursor.execute("SELECT od.id as id, menu.name as item, \
                            od.quantity as quantity, od.status as status \
                            FROM orders as od, fooditems as menu \
                            WHERE od.item=menu.item_id and od.status !='cancelled' and od.user_id='"+str(user_id)+"'")
        order_items = self.db.cursor.fetchall()
        orders = []
        for item in order_items:
            order = {"id": item['id'], "item": item['item'], "quantity": item['quantity'], "status": item['status']}
            orders.append(order)
        return orders

    def get_order(self, order_id):
        """ retrieve order with given id. """
        sql = """SELECT od.id as id, menu.name as item,
             od.quantity as quantity, od.status as status, cu.name as user_id
             FROM orders as od, fooditems as menu, users as cu
              WHERE od.item=menu.item_id and od.status !='cancelled'
              and od.user_id=cu.id and od.id=%s;
             ;"""
        self.db.cursor.execute(sql, (str(order_id)))
        order_item = self.db.cursor.fetchone()
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            order = {"id": order_item['id'], "item": order_item['item'], "quantity": order_item['quantity'], "status": order_item['status'], "user_id": order_item['user_id']}
            return order

    def update_order(self, order_id, order_data):
        """ update order details. """
        order = order_data
        order['status'] = str(order_data['status'])
        self.db.cursor.execute("UPDATE orders set status='"+order['status']+"' WHERE id='"+str(order_id)+"'")
        
        rows_updated = self.db.cursor.rowcount
        if rows_updated > 0:
            return order
        else:
            return "unable to update order"

    def update_user_order(self, order_id, order_data):
        """ update order details. """
        order = order_data
        order['item'] = str(order_data['item'])
        order['quantity'] = int(order_data['quantity'])
        order['status'] = str(order_data['status'])
        self.db.cursor.execute("UPDATE orders set item='"+order['item']+"', quantity='"+ str(order['quantity'])+"', status='"+order['status']+"' WHERE id='"+str(order_id)+"'")
        rows_updated = self.db.cursor.rowcount
        if rows_updated > 0:
            order['id'] = order_id
            return order
        else:
            return "unable to update order"

    def delete_order(self, order_id):
        """ delete order. """
        self.db.cursor.execute("DELETE FROM orders WHERE id='"+str(order_id)+"'")
        rows_deleted = self.db.cursor.rowcount
        if rows_deleted > 0:
            return "order was deleted"
        else:
            return "unable to delete order"
