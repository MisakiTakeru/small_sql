# small_sql
A project playing around with mysql and sqlalchemy

## Table classes
* Wares:
  * ID
  * Name
  * Description
  * Category (relationship)
  * Price
  * Amount in stock
* Categories:
  * ID
  * Category name
  * Description
* Transactions:
  * ID
  * Ware ID
  * Time
  * Amount
  * Type of transaction
## Possible Functions
* Add Ware
* Remove Ware
* Update variable in Ware
* Show warehouse (both everything, and from a specific Category)
* Generate reports (Maybe gain and losses in every Ware category or simply for each month)
## Coding Style and Choices
* Forced to use OOP and mySQL
* Will use the Object Relation Mapper (ORM) from sqlalchemy to implement mySQL with nice [small examples](https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/python-sqlalchemy.rst).
