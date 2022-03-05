from uuid import uuid4
import json
import os
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from itertools import groupby

import pandas as pd
import sqlalchemy
from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Boolean, MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


def count_per_day(ecg_list) -> dict:
    ecg_dates = [i.done_time.strftime('%d-%m-%Y') for i in ecg_list]
    days = {(datetime.now() - timedelta(days=d)).strftime('%d-%m-%Y'): 0 for d in range(31)}
    for ecg in ecg_dates:
        days[ecg] += 1
    return days


class Main(Base):
    __tablename__ = 'main'
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(128))
    test_id = Column(String(128))
    date_of_test = Column(DateTime)
    report = Column(String)
    path = Column(String)
    url = Column(String)
    hold_by = Column(DateTime)
    done_time = Column(DateTime)
    block_by_user_id = Column(Integer)
    done = Column(Boolean)
    history_done = Column(Boolean)
    done_by_user_id = Column(String)
    age = Column(Integer)
    sex = Column(Integer)
    anno = relationship("Annotations", backref="annotation")


class Annotations(Base):
    __tablename__ = 'annotations'
    id = Column(Integer, ForeignKey(Main.id), primary_key=True, autoincrement=True)
    anno = Column(String)

    def __repr__(self):
        return f"<Annotations()>"


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, ForeignKey(Main.id), primary_key=True, autoincrement=True)
    history = Column(String)

    def __repr__(self):
        return f"<History()>"


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    userpassword = Column(String)


class Database:
    def __init__(self, csvdb, root_url, sqldb, create_new=False, migrate=False):
        # self.df = pd.read_csv(csvdb, index_col=None)
        self.root_url = root_url
        self.db = sqldb
        self.session = self.connect()
        if create_new:
            self.init_db()
        if migrate:
            self.run_migrate()

    def connect(self):
        # TODO safety multithreading
        self.engine = create_engine(self.db)
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def init_db(self):
        metadata = MetaData()
        main_table = Main()

        annotations = Annotations()
        history = History()

        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        for row_idx, _ in enumerate(self.df.iterrows()):
            source = self.df.iloc[row_idx]
            main_row = Main(patient_id=source['patient_id'],
                            test_id=source['test_id'],
                            date_of_test=datetime.strptime(source['date_of_test'], '%Y-%m-%d'),
                            report=source['report'],
                            url=os.path.join(self.root_url, source['patient_id'], source['test_id']),
                            hold_by=datetime.strptime("01-01-2000", '%d-%m-%Y'),
                            path=source["path"],
                            age=source["age"],
                            sex=int(source["sex"]),
                            done=False,
                            history_done=False
                            )
            anno_row = Annotations(anno=json.dumps({}))
            history_row = History(history=json.dumps({}))

            # self.session.add(main_row)
            # self.session.add(anno_row)
            self.session.add(history_row)
        self.session.commit()

    def run_migrate(self):
        metadata = MetaData()
        main_table = Main()

        annotations = Annotations()
        history = History()

        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        for row_idx, _ in enumerate(self.df.iterrows()):
            source = self.df.iloc[row_idx]
            main_row = Main(
                            history_done=False
                            )
            anno_row = Annotations(anno=json.dumps({}))
            history_row = History(history=json.dumps({}))

            # self.session.add(main_row)
            # self.session.add(anno_row)
            self.session.add(history_row)
        self.session.commit()

    def query_by_uuid(self, uuid: uuid4):
        """ Query data of specific id"""
        df = pd.read_sql(f"select * from t_files tf  where tf.uuid = '{uuid}'", con=self.connection)
        return df.to_dict('records')

    def query_report_by_uuid(self, uuid: uuid4):
        df = pd.read_sql(f"select tf.uuid , tf.sex , tf.age,  tr.report  from t_reports tr  left join t_files tf on tf.uuid  = tr.uuid   where tr.uuid = '{uuid}'", con=self.connection)
        return df.to_dict('records')

