from crm.importer import import_customers


def handle_upload(request_rows):
    count = import_customers(request_rows)
    return {"imported": count}
