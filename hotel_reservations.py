"""
HOTEL RESERVATION SYSTEM
by A01330566

Basic classes and unit test assignemnt
"""
import sys
import os
import json
import unittest

CUS_PATH = "customers.json"
HTL_PATH = "hotels.json"
RES_PATH = "reservations.json"


class HotelError(Exception):
    """Exception raised for errors in hotel class."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Hotel:
    """
    This class manages hotel information
    """
    def __init__(self, name, location, rooms) -> None:
        self.name = name
        self.location = location
        if (isinstance(rooms, list) and
                all(isinstance(room, int) for room in rooms)):
            self.available_rooms = rooms
        else:
            raise HotelError("Rooms must be a list of integers")
        self.reservations = {}

    def get_all_rooms(self):
        """
        This function returns all the rooms
        """
        return self.available_rooms + list(self.reservations.keys())

    def add_room(self, new_room):
        """
        This function allows to add rooms individually
        """
        if (new_room not in self.available_rooms and
                new_room not in self.reservations):
            self.available_rooms.append(new_room)

    def reserve_room(self, customer, room_number) -> bool:
        """
        This function allows the user to reserve a room
        """
        if room_number in self.available_rooms:
            self.reservations[room_number] = customer
            self.available_rooms.remove(room_number)
            print(f"Room {room_number} reserved for {customer}")
            return True
        else:
            print(f"Room {room_number} is not available")
            return False

    def cancel_reservation(self, customer, room_number) -> bool:
        """
        This function allows the user to cancel a reservation
        """
        if room_number in self.reservations:
            if self.reservations[room_number] == customer:
                self.reservations.pop(room_number)
                self.available_rooms.append(room_number)
                print(f"Reservation for {customer} in room" +
                      f" {room_number} cancelled")
                return True

        print("No such reservation found")
        return False

    def modify_info(self, name=None, location=None, rooms=None):
        """
        This function can be used to modify any of hotel's information
        """
        if name:
            self.name = name
        if location:
            self.location = location
        if rooms:
            if (isinstance(rooms, list) and
                    all(isinstance(room, int) for room in rooms)):
                self.available_rooms = rooms
            else:
                raise HotelError("Rooms must be a list of integers")
        print("Hotel information modified successfully")

    def print_info(self):
        """
        This function prints the Hotel's information
        """
        print(f"Hotel Name: {self.name}")
        print(f"Location: {self.location}")
        print(f"Available Rooms: {self.available_rooms}")
        print(f"Reserved Rooms: {list(self.reservations.keys())}")

    def to_dict(self):
        """
        Converts object to dictionary
        """
        return {
            "name": self.name,
            "location": self.location,
            "rooms": self.get_all_rooms()
        }


class Customer:
    """
    This class manages customer information
    """
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def modify_info(self, name=None, email=None):
        """
        This function can be used to modify any of customer's information
        """
        if name:
            self.name = name
        if email:
            self.email = email

        print("Hotel information modified successfully")

    def print_info(self):
        """
        This function prints the customer's information
        """
        print(f"Customer Name: {self.name}")
        print(f"Email: {self.email}")

    def to_dict(self):
        """
        This function converts object to dictionary
        """
        return {
            "name": self.name,
            "email": self.email
        }


class Reservations:
    """
    This class handles all customers and hotels info + reservations
    """
    def __init__(self) -> None:
        self.hotels = {}
        if os.path.exists(HTL_PATH):
            hotel_json = read_json_file(HTL_PATH)
            for item in hotel_json:
                if is_item_valid(item, ["name", "location", "rooms"]):
                    try:
                        new_hotel = Hotel(item.get("name"),
                                          item.get("location"),
                                          item.get("rooms"))
                        if not item.get("name") in self.hotels:
                            self.hotels[item.get("name")] = new_hotel
                    except HotelError as e:
                        print(e.args[0])

        self.customers = {}
        if os.path.exists(CUS_PATH):
            customer_json = read_json_file(CUS_PATH)
            for item in customer_json:
                if is_item_valid(item, ["name", "email"]):
                    new_customer = Customer(item.get("name"),
                                            item.get("email"))
                    self.customers[item.get("name")] = new_customer

        if os.path.exists(RES_PATH):
            rsrv_json = read_json_file(RES_PATH)
            for item in rsrv_json:
                if is_item_valid(item,
                                 ["customer", "email", "hotel",
                                  "room", "location"]):
                    room = item.get("room")
                    htl_name = item.get("hotel")
                    email = item.get("email")
                    cust = item.get("customer")
                    loctn = item.get("location")

                    if cust not in self.customers:
                        new_customer = Customer(cust, email)
                        self.customers[htl_name] = new_customer

                    if htl_name not in self.hotels:
                        new_hotel = Hotel(htl_name,
                                          loctn,
                                          [room])
                        new_hotel.reserve_room(cust, room)
                        self.hotels[htl_name] = new_hotel

                    else:
                        if (room not in
                                self.hotels[htl_name].get_all_rooms()):
                            self.hotels[htl_name].add_room(room)

                        self.hotels[htl_name].reserve_room(cust, room)

    def write_files(self):
        """
        This function writes all the values back to json file
        """
        hotels_json = []
        reserv_json = []
        for hotel in self.hotels.values():
            hotels_json.append(hotel.to_dict())
            if len(hotel.reservations) > 0:
                for res in hotel.reservations:
                    cust = hotel.reservations[res]
                    email = self.customers[cust].email
                    res_json = {"hotel": hotel.name,
                                "location": hotel.location,
                                "room": res, "customer": cust,
                                "email": email}
                    reserv_json.append(res_json)
        write_json_file(hotels_json, HTL_PATH)
        write_json_file(reserv_json, RES_PATH)

        customs_json = []
        for custom in self.customers.values():
            customs_json.append(custom.to_dict())
        write_json_file(customs_json, CUS_PATH)

    def create_hotel(self, hotel_name, location, rooms):
        """
        This function allows the user to create new hotels
        """
        try:
            if hotel_name not in self.hotels:
                new_hotel = Hotel(hotel_name, location, rooms)
                self.hotels[hotel_name] = new_hotel
        except HotelError as err:
            print(err)

    def remove_hotel(self, hotel_name):
        """
        This function allows the user to remove hotels from file
        """
        if hotel_name in self.hotels:
            self.hotels.pop(hotel_name)
        else:
            print("Hotel does not exist!")

    def display_hotel_info(self, hotel_name):
        """
        This function allows you to display hotel info
        """
        if hotel_name in self.hotels:
            self.hotels[hotel_name].print_info()
        else:
            print("Hotel not found")

    def edit_hotel(self, old_hotel_name, new_hotel_name=None,
                   new_location=None, new_rooms=None):
        """
        This function allows the user to modify a hotel
        """
        if old_hotel_name in self.hotels:
            new_hotel = self.hotels[old_hotel_name]
            self.hotels.pop(old_hotel_name)
            try:
                new_hotel.modify_info(new_hotel_name, new_location, new_rooms)
            except HotelError as ex:
                print(ex)

            self.hotels[new_hotel.name] = new_hotel

        else:
            print("Hotel Not Found!")

    def reserve_room(self, hotel_name, location, customer, email, room):
        """
        This function allows the user to reserve a new room
        """
        if hotel_name not in self.hotels:
            self.create_hotel(hotel_name, location, [room])

        self.hotels[hotel_name].reserve_room(customer, room)

        if customer not in self.customers:
            self.create_customer(customer, email)

    def cancel_reservation(self, hotel_name, room_number, customer):
        """
        This function allows the user to cancel reservationss
        """
        if hotel_name in self.hotels:
            self.hotels[hotel_name].cancel_reservation(customer, room_number)
        else:
            print("Hotel Not Found!")

    def create_customer(self, name, email):
        """
        This function allows the user create customers
        """
        if name not in self.customers:
            self.customers[name] = Customer(name, email)
        else:
            print("Customer already exists!")

    def delete_customer(self, name):
        """
        This function allows the user to delete customerss
        """
        if name in self.customers:
            self.customers.pop(name)
        else:
            print("Customer does not exist!")

    def display_customer_info(self, name):
        """
        This function prints customer's info
        """
        if name in self.customers:
            self.customers[name].print_info()
        else:
            print("Customer does not exist!")

    def modify_customer(self, old_name, new_name=None, new_email=None):
        """
        This functions allows the user to modify existent customer info
        """
        if old_name in self.customers:
            new_customer = self.customers[old_name]
            self.customers.pop(old_name)

            new_customer.modify_info(new_name, new_email)
            self.customers[new_customer.name] = new_customer
        else:
            print("Customer does not exist!")


def read_json_file(file_path):
    """
    This function reads the json file and handles errors such as:
    - File not existent
    - Json Decode Error
    - Unicode Decode Error
    """
    json_file = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_file = json.load(file)
    except FileNotFoundError:
        print("File not found:", file_path)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Invalid format in catalogue json file")
        sys.exit(1)
    except UnicodeDecodeError:
        print("File is not encoded in UTF-8. Verify and retry")
        sys.exit(1)

    return json_file


def write_json_file(data, file_path):
    """
    This function writes the json file
    """
    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def is_item_valid(item, parameters):
    """
    This function allows the user to check if
    all items in a json are not null
    """
    for param in parameters:
        if not item.get(param):
            return False
    return True


class TestHotelMethods(unittest.TestCase):
    """
    This class encloses all test cases in the Hotel Class
    """

    def setUp(self):
        """
        This function sets up the Hotel class to verify
        """
        self.hotel = Hotel("Las Brisas", "Queretaro", [101, 102, 103])

    def test_get_all_rooms(self):
        """
        Test case - Checks that the rooms are the same than saved
        """
        self.assertEqual(self.hotel.get_all_rooms(), [101, 102, 103])

    def test_add_room(self):
        """
        Test case - This test case verifies that the room is added correctly
        """
        self.hotel.add_room(104)
        self.assertIn(104, self.hotel.available_rooms)

    def test_reserve_room(self):
        """
        Test case - This test case verifies that the room is reserved correctly
        """
        self.assertTrue(self.hotel.reserve_room("Johnny Cash", 101))
        self.assertEqual(self.hotel.reservations[101], "Johnny Cash")

    def test_cancel_reservation(self):
        """
        Test case - This test case verifies that the room is cancelled
        correctly
        """
        self.hotel.reserve_room("Johnny Cash", 101)
        self.assertTrue(self.hotel.cancel_reservation("Johnny Cash", 101))
        self.assertNotIn(101, self.hotel.reservations)


class TestCustomerMethods(unittest.TestCase):
    """
    This class encloses all test cases to check the customer class
    """
    def setUp(self):
        """
        This function sets up the Customer class to verify
        """
        self.customer = Customer("Johnny Cash", "john@cash.com")

    def test_modify_info(self):
        """
        Test case - verify that the customer information can be
        modified
        """
        self.customer.modify_info(email="johnnycash@cash.com")
        self.assertEqual(self.customer.email, "johnnycash@cash.com")


class TestReservationsMethods(unittest.TestCase):
    """
    This class encloses all test cases to check the reservation class
    """
    def setUp(self):
        """
        This function sets up the Reservations class to verify
        """
        self.reservations = Reservations()

    def test_create_hotel(self):
        """
        Test Case - This test case verifies that the hotel is created correctly
        """
        self.reservations.create_hotel("Hilton Garden Inn",
                                       "Houston, TX",
                                       [101, 102])
        self.assertIn("Hilton Garden Inn", self.reservations.hotels)

    def test_remove_hotel(self):
        """
        Test case - This test case validates that test is created and removed
        properly
        """
        self.reservations.create_hotel("Residence Inn",
                                       "Livonia, MI",
                                       [101, 102])
        self.reservations.remove_hotel("Residence Inn")
        self.assertNotIn("Residence Inn", self.reservations.hotels)

    def test_reserve_room(self):
        """
        Test Case - This test case verifies that the hotel is reserved
        correctly
        """
        self.reservations.reserve_room("HardRock",
                                       "Tokyo, JP",
                                       "Uri Petrovsky",
                                       "uri@fox.com",
                                       101)
        self.assertIn(101, self.reservations.hotels["HardRock"].reservations)

    def test_cancel_reservation(self):
        """
        Test case - This test case verifies that the reservation is
        created and removed correclty
        """
        self.reservations.create_hotel("Days Inn",
                                       "Laredo, TX",
                                       [101, 102])
        self.reservations.reserve_room("Days Inn",
                                       "Laredo, TX",
                                       "John Cena",
                                       "john@wwe.com",
                                       101)
        self.reservations.cancel_reservation("Days Inn",
                                             101,
                                             "John Cena")
        self.assertNotIn(101,
                         self.reservations.hotels["Days Inn"].reservations)

    def test_edit_hotel(self):
        """
        Test case - Verifies that the hotel info is modified correctly
        """
        self.reservations.create_hotel("Mirages",
                                       "Las Vegas, NV",
                                       [101, 102])
        self.reservations.edit_hotel("Mirages",
                                     new_hotel_name="Mirage")
        self.assertIn("Mirage", self.reservations.hotels)

    def test_create_customer(self):
        """
        Test case - This test case verifies that a customer is created
        correctly
        """
        self.reservations.create_customer("Jimmy Page", "JP@LedZep.com")
        self.assertIn("Jimmy Page", self.reservations.customers)

    def test_delete_customer(self):
        """
        Test case - This test case verifies is deleted correctly
        """
        self.reservations.create_customer("Lars Ulrich", "lars@metallica.com")
        self.reservations.delete_customer("Lars Ulrich")
        self.assertNotIn("Lars Ulrich", self.reservations.customers)

    def test_modify_customer(self):
        """
        Test case - This test case verifies that the customer's info
        is modified correctly
        """
        self.reservations.create_customer("Eddie VH", "evh@esp.com")
        self.reservations.modify_customer("Eddie VH", new_name="Eddie VanH")
        self.assertIn("Eddie VanH", self.reservations.customers)

    def test_write_files(self):
        """
        Test case - This test case verifies that the files are created
        correctly.
        """

        self.reservations.create_hotel("Hard Rock",
                                       "Cancun",
                                       [101, 102])
        self.reservations.reserve_room("Hard Rock",
                                       "Cancun",
                                       "Kirk Hammet",
                                       "KH@metallica.com",
                                       101)

        self.reservations.write_files()

        self.assertTrue(os.path.exists("hotels.json"))
        self.assertTrue(os.path.exists("reservations.json"))
        self.assertTrue(os.path.exists("customers.json"))

        with open("hotels.json", "r", encoding='utf-8') as f:
            hotel_data = json.load(f)
            self.assertIn("Hard Rock",
                          [hotel["name"] for hotel in hotel_data])

        os.remove("hotels.json")
        os.remove("reservations.json")
        os.remove("customers.json")


if __name__ == '__main__':
    unittest.main()
