# -*- coding: utf-8 -*-
import os
import json
import pprint
import pathlib
import logging
from functools import wraps
from collections import OrderedDict

import const
import exporters

logging.basicConfig(level=logging.INFO)


def api_decorator(func):
    """
    basic wrapper to set functions as an API
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result

    wrapper.api = True
    return wrapper


class Entry(OrderedDict):
    """
    base class of database records
    """
    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs)


class DatabaseHandler:
    """
    main database class to handle all interactions with the databse file
    """
    def __init__(self, access_type=const.AccessType.API):
        self.records = DatabaseHandler.load_db()
        self.access_type = access_type

    @staticmethod
    def load_db():
        """
        reading and loading database records from main database file

        Returns:
        list: list of all records where each entry is a dict containing the record data
        """
        records = []

        db_path = os.path.join(os.path.dirname(__file__), f"{const.DEFAULT_DATABASE_FILE_NAME}.json")
        if not os.path.isfile(db_path):
            return records

        try:
            records = json.load(open(db_path, 'r'))
        except Exception as error:
            logging.exception(error)

        return records

    @api_decorator
    def add(self, **data):
        """
        add new record to database
        Args:
            data(dict): new record data as a dict
        Returns:
        dict: newly created record
        """
        if not data:
            logging.error('provided data is not valid.')
            return

        record = Entry(**data)
        if record in self.records:
            logging.critical('duplicated record detected, skip adding.')
            return

        self.records.append(record)

        logging.debug('new record added :{}'.format(record))

        self.commit()
        return record

    @api_decorator
    def delete(self, filters):
        """
        delete filtered database record/s
        Args:
            filters(dict): a dict containing data to filter the database records to deletion
        Returns:
        list: list of deleted record instances
        """
        records = self.filter(**filters)
        if not records:
            logging.warning('no record found to be deleted.')
            return

        for record in records:
            logging.info('deleting record : {}'.format(record))
            self.records.remove(record)

        self.commit()
        return records

    @api_decorator
    def update(self, filters, data):
        """
        update a database record filtered with given data
        Args:
            filters(dict): a dict containing data to filter the database records for update
        Returns:
        list: list of updated record instances
        """
        if not data:
            logging.warning('update data not provided.')
            return

        records = self.filter(**filters)
        if not records:
            logging.warning('not record found to be updated.')
            return records

        if len(records) > 1:
            logging.warning('more than one entry filtered, skip updating.')
            return

        target_record = records[0]
        logging.info('updating record : {}'.format(target_record))

        item_index = self.records.index(target_record)
        updated_record = self.records[item_index].copy()
        for attr in target_record.keys():
            if attr not in data:
                continue
            updated_record[attr] = data.get(attr)

        if updated_record in self.records:
            logging.critical('duplicated record detected, skip adding.')
            return

        logging.info('updating record: {} >> {}'.format(self.records[item_index], updated_record))
        self.records[item_index] = updated_record
        self.commit()
        return records

    @api_decorator
    def query(self, filters=None, all=False, display_format=None):
        """
        query database record/s with the given filters
        Args:
            filters(dict): a dict containing data to filter and query the database records
            all(bool): query all records
            display_format(str): choose a supported format to display the result
        Returns:
        list: list of queried record/s instances
        """
        # TODO implement display format and pretty printing

        if all:
            logging.info(f'response :\n{pprint.pformat(self.records)}')
            return self.records

        if not filters:
            return []

        records = self.filter(**filters)
        logging.info(f'response :\n{pprint.pformat(records)}')
        return records

    @api_decorator
    def filter(self, *arg, **filters):
        """
        filter database records based on the given filters
        Args:
            filters(dict): a dict containing data to filter the database records
        Returns:
        list: list of filtered record/s instances
        """
        filtered_records = []
        for record in self.records:
            for attr in record.keys():
                if attr not in filters:
                    continue

                if not filters.get(attr):
                    continue

                if filters[attr] != record.get(attr):
                    continue

                filtered_records.append(record)

        if not filtered_records:
            logging.debug('no records filtered.')
            return filtered_records

        logging.debug(f'records filtered:\n{pprint.pformat(filtered_records)}')
        return filtered_records

    @api_decorator
    def export(self, path, force=False):
        """
        export function to save and export database as a new format or file
        Args:
            path(str): full path containing the file name and format for database file
            force(bool): to force exporter to create a new file if there is already and existing entry
        """
        path = pathlib.Path('/Users/admin/PycharmProjects/AnimalLogic/export/export_test.xml')

        exporter_class = getattr(exporters, f'{path.suffix.strip(".").upper()}{const.EXPORTER_SUFFIX}', None)
        if not exporter_class:
            logging.error(f'no exporter found for the requested datatype : {path.suffix}')
            return

        exporter_instance = exporter_class(path.stem)
        exporter_instance.set_export_dir(path.parent)
        exporter_instance.set_export_data(self.records)
        exporter_instance.export(force)

    def commit(self, force=False):
        """
        a helper function to lazy export records on demand (designed for OOP interactions)
        Args:
            force(bool): to force exporter to create a new file if there is already and existing entry
        """
        commit_state = False

        if self.access_type == const.AccessType.CLI:
            commit_state = True

        if force:
            commit_state = True

        if not commit_state:
            return

        exporter_class = getattr(exporters, f'{const.DEFAULT_DATABASE_EXPORTER}{const.EXPORTER_SUFFIX}')
        exporter_instance = exporter_class()
        exporter_instance.set_export_data(self.records)
        exporter_instance.export()
