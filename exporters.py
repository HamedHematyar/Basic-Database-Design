# -*- coding: utf-8 -*-
"""
Main module to implement different databse exporters.
"""

import os
import sys
import logging
import inspect
from abc import ABCMeta, abstractmethod

import const


class Exporter(metaclass=ABCMeta):
    """
    database base class exporter, follow the signatures and implement the abstracted methods.
    """
    extension = ''

    def __init__(self, file_name=const.DEFAULT_DATABASE_FILE_NAME):
        self.file_name = file_name
        self.export_path = ''
        self.records = []

    def set_file_name(self, file_name):
        """set export file name
        Args:
            file_name(str): file name
        """
        self.file_name = file_name

    def set_export_dir(self, export_path):
        """set export directory path
        Args:
            export_path(str): export directory path
        """
        self.export_path = export_path

    def set_export_data(self, data):
        """set export data
        Args:
            data(list, dict): valid records data to be exported
        """
        self.records = data

    def get_export_path(self):
        """build and return the export file path
        Returns:
            str: output path
        """
        if not self.file_name:
            message = 'export file name is not valid  : {}'.format(self.file_name)
            raise RuntimeError(message)

        if not self.extension:
            message = 'export file extension is not valid  : {}'.format(self.extension)
            raise RuntimeError(message)

        return os.path.join(self.export_path, f'{self.file_name}{self.extension}')

    def pre_export(self, force=False):
        """function runs before the actual export to run pre-checks and validations
        Args:
            force(bool): control state of overriding existing database files
        """
        export_file = self.get_export_path()
        if os.path.isfile(export_file) and not force:
            logging.debug(f'export file already exist, try with Force argument to override : {export_file}')
            return False

        if not os.path.exists(os.path.dirname(export_file)) and os.path.dirname(export_file):
            os.makedirs(os.path.dirname(export_file))

        return True

    @abstractmethod
    def do_export(self):
        """main function to export the data as a file, needs to be implemented in subclasses
        """
        return True

    def post_export(self):
        """function runs after the actual export to run post-checks and validations
        """
        return True

    def export(self, force=False):
        """main export function which takes care of order of operations
        """
        self.pre_export(force)
        self.do_export()
        self.post_export()


class JSONExporter(Exporter):
    extension = '.json'

    def __init__(self, *args, **kwargs):
        super(JSONExporter, self).__init__(*args, **kwargs)

    def do_export(self, *args, **kwargs):
        import json
        with open(self.get_export_path(), 'w') as fp:
            json.dump(self.records, fp, indent=4)

        super(JSONExporter, self).do_export()


class YAMLExporter(Exporter):
    extension = '.yaml'

    def __init__(self, *args, **kwargs):
        super(YAMLExporter, self).__init__(*args, **kwargs)

    def do_export(self, *args, **kwargs):
        import yaml
        output_dict = {}
        for idx, item in enumerate(self.records):
            output_dict[idx] = item

        with open(self.get_export_path(), 'w') as fp:
            yaml.dump({idx: record for idx, record in enumerate(self.records)}, fp, indent=4)

        super(YAMLExporter, self).do_export()


class XMLExporter(Exporter):
    extension = '.xml'

    def __init__(self, *args, **kwargs):
        super(XMLExporter, self).__init__(*args, **kwargs)

    def do_export(self, *args, **kwargs):
        import dicttoxml

        # Variable name of Dictionary is data
        xml = dicttoxml.dicttoxml({str(idx): record for idx, record in enumerate(self.records)})
        xml_decode = xml.decode()

        with open(self.get_export_path(), 'w') as fp:
            fp.write(xml_decode)

        super(XMLExporter, self).do_export()


def get_registered_exporters():
    classes = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and getattr(obj, 'extension', ''):
            classes.append(obj)

    return classes

