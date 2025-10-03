import pandas as pd
from studentcorner.models import AcademicSession

df = pd.read_excel('../excel_data/Session.xlsx')

for index, row in df.iterrows():
    AcademicSession.objects.create(
        session_code=row['session_code'],
        start_date=pd.to_datetime(row['start_date']).date(),
        end_date=pd.to_datetime(row['end_date']).date(),
        is_current=bool(row.get('is_current', False))
    )

print("Import complete!")