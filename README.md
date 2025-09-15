# Gestor_LaPrimera
DEMO Invoice and billing manager of La Primera Bakery 

_This manager was custom made for "La Primera S.A." company_
_This is a 'father' application designed to manage and modify information from various other systems used within the company_


### Requirements 📋

- _MySQL Community Server version 8 en adelante_
- _Lector de archivos .PDF_
- _Lector de archivos .Excel_


## Installation

Make sure you have a working MySQL database and run the .sql
(where it contains the structures of the tables and some data to make it functional.) 
then configure the .ini in the user dir (example: C:\Users\..)

```bash
[DEFAULT]
db_name = schema
db_user = username
db_password = password
db_host = 127.0.0.1
db_port = 3306
```

## To Consider

The script comments and the UI language are in Spanish, and the search button in "Clientes" is disabled,
the reason behind this is due to this application not allowed to communicate with The Federal Administration of Public Income,
which was the revenue service of Argentina (AFIP), when using the DEMO version only


## Usage

Being a demo, only the "Ventas" (sales), "Clientes" (clients) and "Precio" (prices) functionalities found in the "Productos" (products) tab are enabled.
If an error occurs, a log.txt file will be generated in the user's folder containing the error details.

## Features (in full version)

1. **-Invoice Management:** sales, purchases, and expenses
	- Managed by month and year periods, which are editable. Invoices can be voided if necessary.

2. **-Create, delete, and modify:** clients and suppliers
	- Includes an "alias" field to avoid modifying or remembering legal names.
	- Clients have fields for Discount and Surcharge (%) to simplify sales.
	- Suppliers have a DRG% field that auto-loads based on province for convenience.

3. **-Import and export:** invoices and clients
	- Both have a manager that handles duplicates and inconsistencies.
	- Import from text files:
		- Clients
		- General invoices
	- Export (Backups) in .CSV format:
		- Clients
		- Invoices (by date range and type)
	- Includes a dedicated manager to sync the database with a mobile invoicing system (for field sales).

4. **-Report Management:** with Excel and PDF output formats
	- Sales reports:
		- VAT Sales Book
		- Summary by document type (A, B, C, Tickets)
   	- Sales by province
		- Purchase reports:
		- VAT Purchase Book
		- Expense listings
		- Purchases by supplier
		- Fixed assets
	- Generates files required by AFIP in digital format:
		- Purchases
		- Sales
	- Reports can be automatically sent to a designated email address.

5. **-Listings:** (by date range, client, or both)
	- Sales
	- Purchases
	- Sold products
	- Amounts by point of sale

6. **-Settings:** Includes a quick-access configuration section.

7. **-Create, delete, and modify price lists:**
	- For the same product, multiple sales lists (or groups) with different 
		prices can be created. Each client is assigned a specific list.

8. **-Create, delete, and modify products:**
	- Practical interface to modify VAT % and product prices across all assigned lists.
	- Includes a fast-edit list for quick price updates.

9. **-Complete management of budgets and pricing:**
	- All functions of the factory’s internal pricing manager can be handled from this program.

10. **-Connection to AFIP servers:**
	- Clients and suppliers can be searched directly on AFIP servers using only their CUIT.
	- Electronic invoices can be issued directly from the application, using a configured point of sale.


## Built with 🛠️

* [Python](https://www.python.org/)
* [Qt](https://www.qt.io/) - Graphic Framework (I used PyQt5)

## External Libraries
* [PyInvoice](https://pypi.org/project/PyInvoice/) - Used for X invoices
* [FileLock](https://pypi.org/project/filelock/.io/rome/)
* [XlsxWriter](https://pypi.org/project/XlsxWriter/)

## Images
https://imgur.com/a/ovYlxBV

## Author ✒️

* **Gonzalez Magaldi Juan Pablo** - *Development, Testing and Deploy* - [Juspi07](https://github.com/juspi07)


## License
[MIT](https://choosealicense.com/licenses/mit/)