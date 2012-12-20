timequery
=========

Example usage::

    import timequery
    query = timequery.Query() # defaults to "now" if no datetime supplied
    query = query.beginning_of_month() # query methods return a transformed clone
    print query.datetime() # datetime, date, & time are used to return python native types

Putting it all together::

    import timequery
    print timequery.Query().last_month().beginning_of_month().midnight().datetime()

