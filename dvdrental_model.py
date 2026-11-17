"""
Modeling of data from a DVD rental business: one class per table in the database
Due to inheritance, the order and names of attributes deviate from the column names in the database.
For instance, all classes have an id attribute, whereas the corresponding primary keys are all different.
See the inline comments for more information.
"""

from dataclasses import dataclass
import datetime

@dataclass
class Identification:
    """Dataclass for id as primary key of each table, inherited by all other classes"""
    id: int # different id labels in the tables of the database "dvdrental" (e.g., "actor_id" in the table "actor"

@dataclass
class LastUpdate:
    """Dataclass for last update, inherited by all other classes except for those with only foreign keys"""
    last_update: datetime.datetime

# dataclass multiple inheritance: attributes added backwards from the inheritance list
@dataclass
class Actor(Identification, LastUpdate):
    """Dataclass for actors, inherited by the class Person, which is a superclass for Customer and Staff"""
    # person_id: int
    first_name: str
    last_name: str

@dataclass
class Person(Actor):
    """Dataclass for basic personal information, inherited by Customer and Staff"""
    address_id: int
    email: str
    store_id: int
    active: int

@dataclass
class Customer(Person):
    """Dataclass for customers, inheriting Person"""
    activebool: bool
    create_date: datetime.date

@dataclass
class Staff(Person):
    """Dataclass for staffs, inheriting Person"""
    username: str
    password: str
    picture: str

@dataclass
class Address(Identification, LastUpdate):
    """Dataclass for addresses"""
    # address_id: int
    address: str
    address2: str
    district: str
    city_id: int
    postal_code: int
    phone: str

@dataclass
class City(Identification, LastUpdate):
    """Dataclass for cities"""
    # city_id: int
    city: str
    country_id: int

@dataclass
class Country(Identification, LastUpdate):
    """Dataclass for countries"""
    # county_id: int
    country: str

@dataclass
class Store(Identification, LastUpdate):
    """Dataclass for stores"""
    # store_id: int
    manager_staff_id: int
    address_id: int

@dataclass
class Inventory(Identification, LastUpdate):
    """Dataclass for the film inventory: which DVDs (films) in which store"""
    # inventor_id: int
    film_id: int
    store_id: int

@dataclass
class Rental(Identification, LastUpdate):
    """Dataclass for DVD rental: who rented which DVD and when"""
    # rental_id: int
    rental_date: datetime.date
    inventory_id: int
    customer_id: int
    return_date: datetime.date
    staff_id: int

@dataclass
class Payment(Identification, LastUpdate):
    """Dataclass for payment for a DVD rental"""
    # payment_id: int
    customer_id: int
    staff_id: int
    rental_id: int
    amount: int
    # no last_update, but payment_date

@dataclass
class Category(Identification, LastUpdate):
    """Dataclass for categories of films"""
    # category_id: int
    name: str

@dataclass
class Film_Category(LastUpdate):
    """Dataclass for listing all films together with their categories. Both info constitutes the composite primary key."""
    film_id: int
    category_id: int

@dataclass
class Film(Identification, LastUpdate):
    """Dataclass for films/DVDs. The attribute fulltext is a collection of key-value pairs, which vary from film to film."""
    # film_id: int
    title: str
    description: str
    release_year: int
    language_id: int
    rental_duration: int # days
    rental_rate: float
    length: int # minutes
    replacement_cost: float
    rating: str
    special_features: str
    fulltext: dict

@dataclass
class Language(Identification, LastUpdate):
    """Dataclass for languages of films"""
    # language_id: int
    name: str

@dataclass
class Film_Actor(LastUpdate):
    """Dataclass for listing actors of each film. Both information constitutes the composite primary key."""
    actor_id: int
    film_id: int
