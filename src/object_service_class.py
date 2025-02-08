import csv
import os
from src.api_object import ApiObject
from src.database import get_db_connection


class ObjectService:

    """Base service class with static methods for object management"""

    @staticmethod
    def create_object(item_object: ApiObject, table: str):
        item_dict = item_object.generate_dict()

        try:
            name = item_dict["name"]
        except KeyError:
            raise (KeyError("Cannot create object without a name!"))

        try:
            item_id = item_dict["id"]
        except KeyError:
            item_id = None

        city_id = item_dict.get("city_id", None)

        if item_id is None:
            latest_id = ObjectService.get_latest_id(table)
            latest_id += 1
        else:
            latest_id = item_id
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            if city_id is None:
                query = f"INSERT INTO {table} (id, name) VALUES (?, ?)"
                cursor.execute(query, (latest_id, name))
                connection.commit()
                to_return = {"id": latest_id, "name": name}
            else:
                query = f"INSERT INTO {table} (id, name, city_id) VALUES (?, ?, ?)"
                cursor.execute(query, (latest_id, name, city_id))
                connection.commit()
                to_return = {"id": latest_id, "name": name, "city_id": city_id}
        finally:
            connection.close()

        item_object.set_all_to_none()
        item_object.create_from_dict(to_return)
        return item_object

    @staticmethod
    def initialize_database(table: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if table == "cities":
            file_path = os.path.join(base_dir, "../csvs", "cities.csv")
            try:
                with open(file_path, "r") as city_file:
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    city_reader = csv.reader(city_file, delimiter=",")
                    next(city_reader)
                    for row in city_reader:
                        city_id, city_name = row
                        cursor.execute(
                            "INSERT OR IGNORE INTO cities (id, name) VALUES (?, ?)",
                            (city_id, city_name),
                        )
                    connection.commit()
                    connection.close()
            except Exception as e:
                print(f"Error initializing cities data: {e}")
                if connection:
                    connection.close()

        elif table == "airports":
            file_path = os.path.join(base_dir, "../csvs", "airports.csv")
            try:
                with open(file_path, "r") as airport_file:
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    airport_reader = csv.reader(airport_file, delimiter=",")
                    next(airport_reader)
                    for row in airport_reader:
                        airport_id, airport_name, city_id = row

                        cursor.execute(
                            "INSERT OR IGNORE INTO airports (id, name, city_id) VALUES (?, ?, ?)",
                            (airport_id, airport_name, city_id),
                        )
                    connection.commit()
                    connection.close()
            except Exception as e:
                print(f"Error initializing airports data: {e}")
                if connection:
                    connection.close()

        elif table == "flights":
            file_path = os.path.join(base_dir, "../csvs", "flights.csv")
            try:
                with open(file_path, "r") as flight_file:
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    flight_reader = csv.reader(flight_file, delimiter=",")
                    next(flight_reader)
                    for row in flight_reader:
                        (
                            flight_id,
                            flight_number,
                            origin_airport_id,
                            destination_airport_id,
                            price,
                            departure_time,
                            arrival_time,
                            travel_time,
                        ) = row
                        cursor.execute(
                            "INSERT OR IGNORE INTO flights "
                            "(id, name, departure_city, arrival_city, price, "
                            "departure_time, arrival_time, travel_time) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                flight_id,
                                flight_number,
                                origin_airport_id,
                                destination_airport_id,
                                price,
                                departure_time,
                                arrival_time,
                                travel_time,
                            ),
                        )
                    connection.commit()
                    connection.close()
            except Exception as e:
                print(f"Error initializing flights data: {e}")
                if connection:
                    connection.close()

        else:
            raise KeyError("Wrong table name!")

        return " "

    @staticmethod
    def update_object(item_id: int, item_object: ApiObject, table: str):
        item_dict = item_object.generate_dict()

        try:
            obj = ObjectService.get_object(item_id, table).generate_dict()

        except KeyError:
            raise KeyError(f"Object with ID {item_id} is not in the current table!")
        ObjectService.delete_object(item_id, table)
        item_dict["id"] = obj["id"]
        item_object.set_all_to_none()
        item_object.create_from_dict(item_dict)
        ObjectService.create_object(item_object, table)
        return " "

    @staticmethod
    def update_all_objects(list_of_objects: [ApiObject], table: str):
        obj = [i.generate_dict() for i in ObjectService.get_all_objects(table)]

        if obj is not []:
            ObjectService.delete_all_objects(table)

        for value in list_of_objects:
            try:
                ObjectService.create_object(value, table)
            except KeyError:
                print("Item without name.")

        return " "

    @staticmethod
    def get_latest_id(table: str):
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT MAX(id) FROM {table}")
            result = cursor.fetchone()[0]
            return result if result is not None else 0
        finally:
            connection.close()

    @staticmethod
    def get_all_objects(table: str):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        connection.close()
        arr_of_objects = []
        for row in rows:
            item_object = ApiObject()
            item_object.set_all_to_none()
            item_object.create_from_dict(dict(row))
            arr_of_objects.append(item_object)
        return arr_of_objects

    @staticmethod
    def get_object(item_id: int, table: str):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            raise KeyError(f"Object with ID {item_id} not found")
        item_object = ApiObject()
        item_object.set_all_to_none()
        item_object.create_from_dict({key: value for key, value in dict(row).items() if value is not None})

        return item_object

    @staticmethod
    def delete_object(item_id: int, table: str):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (item_id,))
        object_id = cursor.fetchone()

        if object_id is None:
            connection.close()
            raise KeyError(f"No object found with id {item_id}")

        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        connection.commit()
        connection.close()

        return " "

    @staticmethod
    def delete_all_objects(table: str):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table}")
        connection.commit()
        connection.close()
        return " "
