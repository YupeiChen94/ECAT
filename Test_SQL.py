import pyodbc
import pandas as pd
server = 'DESKTOP-G4MFTGK'
database = 'ALB'
# username = 'UsingAD'
# password = 'UsingAD'
trusted_cnxn = 'yes'
cnxn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER='+server+';'
                      'DATABASE='+database+';'
                      'TRUSTED_CONNECTION='+trusted_cnxn+';')


# cursor = cnxn.cursor()
# cursor.execute('Select TOP 10 * FROM dbo.DrySamples')
# for row in cursor:
#     print(row)

# Multiple Units, Single SampleType, DateRange
query_table = 'ALB.dbo.DrySamples'
query_units = (540, 76)
query_sample_type = 'ECAT'
params = [query_sample_type]
params += query_units
# print(params)

# TODO: Try block to validate query returns data

# query_string = f"""
#                 SELECT TOP 10 Sample_Number, Refinery_ID, Sample_Type FROM {query_table}
#                 WHERE Refinery_ID IN {query_units} AND Sample_Type = '{query_sample_type}'
# """
# df = pd.read_sql_query(query_string, cnxn)

query_string = """Select TOP 10 Sample_Number, Refinery_ID, Sample_Type
                    FROM dbo.DrySamples
                    WHERE Sample_Type = {0} AND Refinery_ID IN ({1})"""
query_string = query_string.format('?', ','.join('?' * len(query_units)))
# print(query_string)
df = pd.read_sql_query(query_string, cnxn, params=params)

print(df)
