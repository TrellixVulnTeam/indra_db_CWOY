import logging
from psycopg2.errors import DuplicateTable

logger = logging.getLogger(__name__)


class IndraDBTable(object):
    _indices = []
    _skip_disp = []
    _always_disp = ['id']

    @classmethod
    def create_index(cls, db, index, commit=True):
        inp_data = {'idx_name': index.name,
                    'table_name': cls.__tablename__,
                    'idx_def': index.definition,
                    'schema': cls.__table_args__.get('schema', 'public')}
        sql = ("CREATE INDEX {idx_name} ON {schema}.{table_name} "
               "USING {idx_def} TABLESPACE pg_default;".format(**inp_data))
        if commit:
            try:
                cls.execute(db, sql)
            except DuplicateTable as err:
                logger.warning("Got error (%s) when building %s. Skipping."
                               % (err, index.name))
        return sql

    @classmethod
    def build_indices(cls, db):
        for index in cls._indices:
            print("Building index: %s" % index.name)
            cls.create_index(db, index)

    def _make_str(self):
        s = self.__tablename__ + ':\n'
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                if k in self._skip_disp:
                    s += '\t%s: [not shown]\n' % k
                else:
                    s += '\t%s: %s\n' % (k, v)
        return s

    def display(self):
        """Display the values of this entry."""
        print(self._make_str())

    def __str__(self):
        return self._make_str()

    def __repr__(self):
        ret = self.__class__.__name__ + '('

        entries = []
        for attr_name in self._always_disp:
            attr = getattr(self, attr_name)
            if isinstance(attr, str):
                fmt = '%s="%s"'
            elif isinstance(attr, bytes):
                fmt = '%s=b"%s"'
            else:
                fmt = '%s=%s'

            entries.append(fmt % (attr_name, attr))

        ret += ', '.join(entries)
        ret += ')'
        return ret


class ReadonlyTable(IndraDBTable):
    __definition__ = NotImplemented
    __table_args__ = NotImplemented

    @classmethod
    def create(cls, db, commit=True):
        sql = "CREATE TABLE IF NOT EXISTS %s.%s AS %s;" \
              % (cls.__table_args__['schema'], cls.__tablename__,
                 cls.get_definition())
        if commit:
            cls.execute(db, sql)
        return sql

    @classmethod
    def get_definition(cls):
        return cls.__definition__

    @staticmethod
    def execute(db, sql):
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return


class NamespaceLookup(ReadonlyTable):
    __dbname__ = NotImplemented

    @classmethod
    def get_definition(cls):
        return ("SELECT db_id, ag_id, role, ag_num, type, "
                "mk_hash, ev_count FROM readonly.pa_meta "
                "WHERE db_name = '%s'" % cls.__dbname__)

