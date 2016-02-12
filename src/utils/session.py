import shelve


class SessionDB:
    """
        In real world applications, choosing a very efficient way to store
        sessions on databases is essential. Here it's ok.
        Shelve is pure simple python to create a disk persistent map.
        https://docs.python.org/2/library/shelve.html#example
    """

    def __init__(self, db_path, view_name):
        self.db_path = db_path
        self.view_name = view_name

    def get(self, key):
        _db = shelve.open(self.db_path)
        viewdb = _db.get(self.view_name, {})
        _db.close()
        return viewdb.get(key)

    def set(self, key, value):
        _db = shelve.open(self.db_path)
        try:
            viewdb = _db.get(self.view_name, {})
            viewdb[key] = value
            _db[self.view_name] = viewdb
        finally:
            _db.close()
