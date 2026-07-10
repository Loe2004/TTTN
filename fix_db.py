import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT phone, COUNT(*) FROM accounts_user GROUP BY phone HAVING COUNT(*) > 1")
    duplicate_phones = cursor.fetchall()
    for phone, count in duplicate_phones:
        # For each duplicated phone (including empty string)
        cursor.execute("SELECT id FROM accounts_user WHERE phone = %s OR (phone IS NULL AND %s IS NULL)", [phone, phone])
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            if i > 0:
                new_phone = f"dup{i}_{row[0]}"
                cursor.execute("UPDATE accounts_user SET phone = %s WHERE id = %s", [new_phone, row[0]])
                print(f"Updated duplicate phone id {row[0]} to {new_phone}")
    connection.commit()
    print("Done")
