longitudinal_register README
==================

Getting Started
---------------

- $easy_install pip

- $pip install virtualenv

- $pip install virtualenvwrapper (optional)

- $virtualenv longitudinal_register

- $cd longitudinal_register

- $git clone git@github.com:etoko/longitudinal_register.git OR git clone https://github.com/etoko/longitudinal_register.git

- cd <directory containing this file>

- $pip install -r requirements.txt

- NOTE: Ensure that your in the intended database system, you have created the necessary user account and database and provided that user account with the necessary privileges to create database tables.

PostgreSQL 9.1 server was used in the development of this application. In the event that you use a different database system, you should install the appropriate database driver or replace the PostgreSQL driver in the requirements.txt file (psycopg2) with the appropriate one. 

The next step is to configure the appropriate user accounts in the development.ini/production.ini file like so: under the section DATABASE Settings, replace neo:whatisthematrix with your username:password

- $venv/bin/python setup.py develop

- $venv/bin/initialize_longitudinal_register_db development.ini OR $venv/bin/initialize_longitudinal_register_db production.ini

- $venv/bin/pserve development.ini

