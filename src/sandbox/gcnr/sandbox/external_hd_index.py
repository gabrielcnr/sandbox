import os
import datetime

import shutil
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import argparse
import time

Base = declarative_base()


class FileSystemEntry(Base):
    __tablename__ = 'file_system_entry'

    DIR = 'DIR'
    FILE = 'FILE'
    LINK = 'LINK'

    id = Column(Integer, primary_key=True)
    volume_name = Column(String(255))
    full_path = Column(String)
    dirname = Column(String)
    basename = Column(String)
    basename_noext = Column(String)
    extension = Column(String)
    type = Column(String)
    size = Column(Integer)
    modified = Column(DateTime)
    created = Column(DateTime)
    comment = Column(String)
    insert_datetime = Column(DateTime)

# TODO: make (volume_name, full_path) unique


path_to_db = os.path.expandvars('$HOME/external_hd.db')
engine = create_engine('sqlite:///{}'.format(path_to_db))

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()

def backup_existing_db():
    shutil.copy(path_to_db, path_to_db+'.bak')


def main():
    """
    This method creates a full catalogue/index of a directory.
    It stores the data in the Database file: $HOME/external_hd.db
    """
    t0 = time.clock()
    parser = argparse.ArgumentParser()
    parser.add_argument('volume_name')
    args = parser.parse_args()

    backup_existing_db()

    insert_datetime = datetime.datetime.now()
    volume_name = args.volume_name
    for dirpath, dirnames, filenames in os.walk(''):
        normdir = os.path.normpath(dirpath).decode('utf-8')
        entry = FileSystemEntry(
            volume_name=volume_name,
            full_path=normdir,
            dirname=os.path.dirname(normdir),
            basename=os.path.basename(normdir),
            basename_noext=None,
            extension=None,
            type=FileSystemEntry.DIR,
            size=None,
            modified=datetime.datetime.utcfromtimestamp(
                os.path.getmtime(normdir)),
            created=datetime.datetime.utcfromtimestamp(
                os.path.getctime(normdir)),
            comment=None,
            insert_datetime=insert_datetime,
        )
        session.add(entry)

        for filename in filenames:
                normfile = os.path.normpath(
                    os.path.join(dirpath, filename)).decode('utf-8')
                basename = os.path.basename(normfile)
                basename_noext, extension = os.path.splitext(basename)
                entry = FileSystemEntry(
                    volume_name=volume_name,
                    full_path=normfile,
                    dirname=normdir,
                    basename=basename,
                    basename_noext=basename_noext,
                    extension=extension.lstrip('.').lower(),
                    type=FileSystemEntry.FILE,
                    size=os.path.getsize(normfile),
                    modified=datetime.datetime.utcfromtimestamp(
                        os.path.getmtime(normfile)),
                    created=datetime.datetime.utcfromtimestamp(
                        os.path.getctime(normfile)),
                    comment=None,
                    insert_datetime=insert_datetime,
                )
                session.add(entry)

    session.commit()

    t1 = time.clock()
    print 'Indexing took %.2f s' % (t1-t0)


def get_df():
    """
    Queries the SQL database and returns a full pandas DataFrame
    with the entire index of the files to be manipulated.

    Great for using in IPython Notebook.
    """
    query = session.query(FileSystemEntry)
    df = pd.read_sql(query.statement.compile(engine), engine)
    return df


def get_short_df():
    """ Fewer columns of the DataFrame returned by get_df().
    """
    pd.set_option('display.width', 5000)
    pd.set_option('display.max_columns', 500)

    df = get_df()
    df2 = df[['volume_name', 'basename_noext', 'extension', 'full_path', 'size']]
    return df2


def find(df, filename='', extension=''):
    if filename:
        mask = df.full_path.str.lower().str.contains(filename.lower())
        df = df[mask]
    if extension:
        mask = df.extension.str.lower().str.contains(extension.lower())
        df = df[mask]
    return df

