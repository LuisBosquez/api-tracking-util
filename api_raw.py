# -*- coding: utf-8 -*-
"""Collect API calls from GitHub into a SQL Database

Reads a formatted resource file with URLs per line and creates a SQL insert statement
that includes a timestamp of the request.

Todo:
    * Configurable connections
    * Create table based on API response?
"""

# Imports
import sys
from urlparse import urlparse

import httplib2
import validators

import pymssql

# Global Configuration
DATABASE_SERVER = '10.120.212.174'
DATABASE_NAME = 'OS_tracker'
SOURCES_FILE_PATH = './api_urls.res'
DATABASE_TABLE = 'api_repository'
DATABASE_USER = 'sa'
DATABASE_PASSWORD = 'Luis9000'

# Helper data structures
ROWS = []
DEBUG = True


def load_sources():
    """ Loads the list of URL sources from the resource file into an array   """
    sources = None
    try:
        sources = [line.rstrip('\n') for line in open(SOURCES_FILE_PATH)]
    except IOError:
        raise

    return sources

def collect_payload(sources):
    """ Collects the content from each of the sources into the ROWS array.  """

    if not sources:
        return

    for source in sources:
        if validators.url(source):
            rows = retrieve_api_data(source.strip())
            if len(rows) > 0:
                tsql = generate_tsql_insert_statement(rows)
                print tsql
            insert_into_database(tsql)
        else:
            print "Invalid URL."
    print "Successfully collected data from {0} sources. Ignored {1} sources".format(
        len(ROWS),
        len(sources) - len(ROWS))

def connect_to_database(user, password):
    """ Handles connection to database with retry logic. """

    conn = False
    while not conn:
        try:
            if not user:
                user = raw_input("Enter your login for {0}: ".format(DATABASE_SERVER))
                password = raw_input("Enter the password: ")
            conn = pymssql.connect(
                server=DATABASE_SERVER,
                user=user, password=password,
                database=DATABASE_NAME, port='1433')
        except pymssql.OperationalError as e:
            print "Connection error: please try again."
            print e.message
    print "Successfully connected to {0}.\n".format(DATABASE_SERVER)
    return conn

def generate_tsql_insert_statement(row):
    """ Create INSERT statement from arrays """
    fields = row.keys()
    result = "INSERT INTO dbo.{0} ({1}) VALUES\n".format(DATABASE_TABLE, ', '.join(fields))

    result += "("
    for field in row.keys():
        value = row[field]
        parameter = str(value).strip()
        if parameter.isdigit():
            result += parameter
        else:
            parameter = parameter.replace("'", "''")
            parameter = parameter.decode('utf-8', 'ignore').encode("utf-8")
            result += "'%s'" % parameter
        result += ","
    result = result[:-1] + ");\n"

    return result

def insert_into_database(tsql):
    """ Initiates the connection to the database.
    Then forms and executes the insert statements into it  """

    conn = connect_to_database(DATABASE_USER, DATABASE_PASSWORD)
    if conn:
        cursor = conn.cursor()
    try:
        cursor.execute(tsql)
        conn.commit()
    except pymssql.Error:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    print "Successfully inserted rows into {0} database.".format(DATABASE_NAME)

def retrieve_api_data(url):
    """ Retrieves the APIs content. """

    row = {}
    try:
        resp, content = httplib2.Http().request(url)
        if resp.status == 200:
            row['content'] = content
            row['source'] = urlparse(url).netloc
        else:
            print "ERROR: Http status {0}".format(resp.status)
    except httplib2.HttpLib2Error:
        print "Connection error to {0}. Site might be down.".format(url)

    return row

def main():
    """ Main function. """

    sources = load_sources()
    collect_payload(sources)

main()
