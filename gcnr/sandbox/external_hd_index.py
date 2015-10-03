import os
import datetime
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

def main():
    t0 = time.clock()
    parser = argparse.ArgumentParser()
    parser.add_argument('volume_name')
    args = parser.parse_args()

    insert_datetime = datetime.datetime.now()
    volume_name = args.volume_name
    for dirpath, dirnames, filenames in os.walk('.'):
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


def query():
    query = session.query(FileSystemEntry)
    df = pd.read_sql(query.statement.compile(engine), engine)

    pd.set_option('display.width', 5000)
    pd.set_option('display.max_columns', 500)

    df2 = df[['full_path', 'extension', 'size']]
    import pdb; pdb.set_trace()
