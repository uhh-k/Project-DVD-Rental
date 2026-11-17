"""Demonstrations of querying a PostgreSQL database and displaying the query results."""

from dvdrental_controller import DVDrentalController
from dvdrental_model import (Customer, Address, City, Country, Store, Inventory, Rental, Payment, Staff, Actor, Category,
                             Film_Category, Film, Language, Film_Actor)

class DVDrentalDemos:
    """The class provide demonstrations of querying a PostgreSQL database and displaying the query results."""

    def __init__(self):
        """
        Initiate a private controller for demonstrations.
        """
        classes_list = [Customer, Address, City, Country, Store, Inventory, Rental, Payment, Staff, Actor, Category,
                        Film_Category, Film, Language, Film_Actor]
        self.__controller = DVDrentalController("dvdrental", classes_list)
        self.__controller.load_data()

    def close(self):
        """
        Close the connection to the database via the controller.
        """
        self.__controller.close()

    # # A demo merely for testing whether data are successfully loaded and saved in dataframes and objects
    # def demo_load_data(self):
    #     # print(self.controller.get_dataframes()['film_category'])
    #     for x in self.__controller.get_objects()['film_category']:
    #         if x.film_id == 118:
    #             print(x)

    def demo_query_where(self):
        """
        Demo: Find the films that have a length greater than 180 and a rental rate less than 1.
        """
        columns = ["title", "length", "rental_rate"]
        query = (f"SELECT {', '.join(columns)} "
                 f"FROM film "
                 f"WHERE length > 180 "
                 f"AND rental_rate < 1")
        print(self.__controller.query_database(query, columns))

    def demo_query_join(self):
        """
        Demo: Find customers who live in Germany.
        """
        columns = ["city", "country", "customer"]
        query = (f"SELECT city.city, country.country, customer.first_name || ' ' || customer.last_name "
                 f"FROM country "
                 f"INNER JOIN city ON country.country_id = city.country_id "
                 f"INNER JOIN address ON address.city_id = city.city_id "
                 f"INNER JOIN customer ON customer.address_id = address.address_id "
                 f"WHERE country.country = 'Germany' "
                 f"ORDER BY city.city")
        print(self.__controller.query_database(query, columns))

    def demo_view_histogram(self):
        """
        Demo: Analyze the payments whose ID is between 17503 and 19505 and aggregate the results by customer.
              Display customers on a scatter plot according to the sum and count of their payments.
        """
        columns = ["customer", "sum_of_payments", "count_of_payments"]
        query = (f"SELECT first_name || ' ' || last_name, SUM(amount) AS total, COUNT(payment_id) "
                 f"FROM customer "
                 f"INNER JOIN payment ON customer.customer_id = payment.customer_id "
                 f"WHERE payment_id BETWEEN 17503 AND 19505 "
                 f"GROUP BY customer.customer_id "
                 f"ORDER BY total DESC")
        result = self.__controller.query_database(query, columns)
        print(result)

        input("\nPress Enter to display a scatter plot...")

        x = result["count_of_payments"].tolist()
        y = result["sum_of_payments"].tolist()
        self.__controller.view_scatter(x=x, y=y, xlabel="count", ylabel="sum", title="Payments")
        # self.__controller.view_scatter(x, y, xlabel="count", ylabel="sum")

if __name__ == "__main__":
    demo = DVDrentalDemos()

    while True:
        # Menu of demos
        intro = """
                Welcome to the DVD rental demos!
                1. Find the films that have a length greater than 180 and a rental rate less than 1.
                2. Find customers who live in Germany.
                3. Analyze the payments whose ID is between 17503 and 19505 and aggregate the results by customer.
                   Display customers on a scatter plot according to the sum and count of their payments.
                """
        print(intro)

        # Choose and execute a demo
        userInput = input("Please choose a demo (0 to exit): ")
        match userInput:
            case "0": break
            case "1": demo.demo_query_where()
            case "2": demo.demo_query_join()
            case "3": demo.demo_view_histogram()
            case _  :
                print("Not a valid option. Please try again.")
                continue

        input("\nPress Enter to continue...")

    demo.close()