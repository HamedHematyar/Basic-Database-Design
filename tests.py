import os
import core

# create database instance to interact with data
db = core.DatabaseHandler()

# add few sample records
db.add(**dict(name='alex', phone='(+1)605-556-1235', address='2550 Marine Way Ave'))

# testing double entry
db.add(**dict(name='alex', phone='(+1)605-556-1235', address='2550 Marine Way Ave'))

db.add(**dict(name='chan', phone='(+1)554-636-6870', address='857 Patterson Ave'))
db.add(**dict(name='martin', phone='(+1)778-686-6970', address='2150 West Ave'))

# commit all changes to db
db.commit(True)

# deleting records with filter
db.delete(dict(name='alex'))
db.commit(True)

# updating record
db.update(dict(name='chan'), dict(name='shelley'))
db.commit(True)

# querying records
db.query(dict(name='martin'))

# test export to json
db.export(os.path.join(os.path.dirname(__file__), 'export', 'export.json'), True)

# test export to xml
db.export(os.path.join(os.path.dirname(__file__), 'export', 'export.xml'), True)