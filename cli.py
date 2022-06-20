# -*- coding: utf-8 -*-
"""
Examples :
python cli.py add --name 'Martin' --phone '(+1)604-636-4153' --address '6188 Wilson Ave'
python cli.py update --data '{"name":"Ron"}' --filters '{"name":"shelley"}'
python cli.py delete --filters '{"name":"ron"}'
python cli.py query --filters '{"name":"chan"}'
python cli.py export --path "exports/export.xml" --force True

"""
import core
import json
import logging
import argparse

import const
import exporters

logging.basicConfig(level=logging.INFO)


def parse_cli_args():
    """A function to parse and return CLI arguments
    Returns:
        Namespace: CLI args as an internal argparse type
    """
    parser = argparse.ArgumentParser()
    action_parser = parser.add_subparsers(dest='action')

    add_action = action_parser.add_parser('add', help='action to add a new record to database.')
    delete_action = action_parser.add_parser('delete', help='action to delete record/s from database.')
    update_action = action_parser.add_parser('update', help='action to update a record in database.')
    query_action = action_parser.add_parser('query', help='action to query and display database records.')
    export_action = action_parser.add_parser('export', help='action to export database to a file.')

    add_action.add_argument('--name', type=str, required=True)
    add_action.add_argument('--phone', type=str, required=True)
    add_action.add_argument('--address', type=str, required=True)

    delete_action.add_argument('--filters', type=json.loads, help='A dict mapping to filter records for deletion.')

    update_action.add_argument('--data', type=json.loads, help='A dictionary mapping with update data for record.')
    update_action.add_argument('--filters', type=json.loads, help='A dictionary mapping to filter target record.')

    query_action.add_argument('--filters', type=json.loads, help='A dictionary mapping to filter records.')
    exporter_types = [exp.extension for exp in exporters.get_registered_exporters()]
    query_action.add_argument('--display_format', type=str, default='json', help=' | '.join(exporter_types))
    query_action.add_argument('--all', type=bool, help='pass to query all records.')

    export_action.add_argument('--path', type=bool, help='full path of exported database file.')
    export_action.add_argument('--force', type=bool, help='force overriding an existing file.')

    args = parser.parse_args()

    return args


def process_action(db, cli_args):
    """main entry point of command line action processing
    Args:
        db(DatabaseHandler): database instance
        cli_args(Namespace): parsed CLI Namespace
    """
    action_function = getattr(db, str(cli_args.action), None)
    fail_message = f'no API method provided for this actions : {cli_args.__dict__}'

    if not action_function:
        raise Exception(fail_message)

    if not getattr(action_function, 'api'):
        raise Exception(fail_message)

    logging.info(f'processing action : {cli_args.__dict__}')

    cli_args.__dict__.pop('action')
    action_function(**cli_args.__dict__)


if __name__ == '__main__':
    # create database instance to interact with data
    database = core.DatabaseHandler(const.AccessType.CLI)
    parsed_cli_args = parse_cli_args()

    # run main processing function
    process_action(database, parsed_cli_args)

