# -*- coding: utf-8 -*-
"""Collect API calls from GitHub into a SQL Database

Reads a formatted resource file with URLs per line and creates a SQL insert statement
that includes a timestamp of the request.

Todo:
    * Configurable connections
    * Create table based on API response?
"""

# Imports
import json
import sys

import httplib2
import validators

import pymssql

# Global Configuration
DATABASE_SERVER = ''
DATABASE_NAME = 'OS_tracker'
SOURCES_FILE_PATH = './urls.res'
DATABASE_TABLE = 'github'
GITHUB_FIELDS = [
    'stargazers_count',
    'updated_at',
    'full_name',
    'id',
    'subscribers_count',
    'network_count',
    'has_pages',
    'open_issues_count',
    'watchers_count',
    'size',
    'homepage',
    'fork',
    'forks',
    'open_issues',
    'has_issues',
    'has_downloads',
    'watchers',
    'name',
    'language',
    'url',
    'created_at',
    'pushed_at',
    'forks_count',
    'default_branch'
]
DATABASE_USER = ''
DATABASE_PASSWORD = ''

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
            retrieve_api_data(source.strip())
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

def generate_tsql_insert_statement():
    """ Create INSERT statement from arrays """
    result = "INSERT INTO dbo.{0} ({1}) VALUES\n".format(DATABASE_TABLE, ', '.join(GITHUB_FIELDS))
    for row in ROWS:
        result += "("
        for field in row.keys():
            if field not in GITHUB_FIELDS:
                continue
            value = row[field]
            parameter = str(value).strip()
            if parameter.isdigit():
                result += parameter
            else:
                parameter = parameter.replace("'", "''")
                parameter = parameter.decode('utf-8', 'ignore').encode("utf-8")
                result += "'%s'" % parameter
            result += ","
        result = result[:-1] + "),\n"
    result = result[:-2] + ";\n"

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
    try:
        resp, content = httplib2.Http().request(url)
        if resp.status == 200:
            ROWS.append(json.loads(content))
        else:
            print "ERROR: Http status {0}".format(resp.status)
    except httplib2.HttpLib2Error:
        print "Connection error to {0}. Site might be down.".format(url)

def main():
    """ Main function. """

    sources = load_sources()
    collect_payload(sources)
    if len(ROWS) == 0:
        print "No data collected. Exiting now."
        return
    tsql = generate_tsql_insert_statement()
    print tsql
    insert_into_database(tsql)
main()
