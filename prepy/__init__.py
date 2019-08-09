import glob
import csv
import sqlite3


# Create table and insert data from N CSV files
def csv_to_table(database: str, table: str, pattern: str, filters, delimiter: str = ','):
    # Connect to sqlite
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Create list of files from pattern
    files = glob.glob(pattern)

    # Create table if needed
    columnCount = create_table_from_csv_header(conn, c, table, files[0], delimiter=delimiter)

    # Insert data
    for file in files:
        header = {}
        with open(file) as csv_file:
            r = csv.reader(csv_file, delimiter=delimiter)
            for i, row in enumerate(r):
                if i == 0:
                    for k, value in enumerate(row):
                        header[value] = k
                else:
                    # Generate placeholder string based on the number of columns (eg. "?, ?")
                    placeholders = ", ".join(list(map(lambda j: f"?", range(columnCount))))

                    # Run filter on columns
                    for f in filters:
                        for field in f['fields']:
                            row[header[field]] = f["filter"](row[header[field]])

                    # Insert into table, skip any extra column if present
                    c.execute(f'INSERT INTO {table} VALUES({placeholders})', row[:columnCount])
            conn.commit()


# Create database using only "text" field from arbitrary CSV file
def create_table_from_csv_header(conn, c, table: str, filename: str, delimiter: str = ',') -> int:
    f = open(filename)
    header = f.readline().rstrip('\n').split(delimiter)
    f.close()
    fields = list(map(lambda s: s + " text", header))
    columns = ", ".join(fields)
    c.execute(f'CREATE TABLE IF NOT EXISTS {table} ({columns})')
    conn.commit()
    return len(fields)


def table_to_csv(database: str, table: str, filename: str = '', limit: int = 0):
    # Connect to sqlite
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Default value for filename
    if filename == '':
        filename = f'{table}.csv'

    # Optional limit
    if limit == 0:
        limitStr = ''
    else:
        limitStr = f'LIMIT {limit}'

    # Build CSV header
    c.execute(f'PRAGMA table_info({table})')
    headers = c.fetchall()
    fieldnames = list(map(lambda column: column[1], headers))

    with open(filename, 'w', newline='') as csv_file:
        # Setup CSV writer
        w = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Write CSV header
        w.writerow(fieldnames)

        # Generate item_id table to be used for items
        for i, row in enumerate(c.execute(f'SELECT * FROM {table} {limitStr}')):
            w.writerow(row)
            if i % 10000 == 0:
                conn.commit()
        conn.commit()
