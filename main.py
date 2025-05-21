import xmlrpc.client
import pandas as pd

# DB stuff
url = "http://localhost:8069"
db = "db18_0"
username = "admin"
password = "admin"

# Set up xmlrpc
common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))

# Map the excel column names into odoo names
column_map = {
    "External ID": "default_code",
    "Product Name": "name",
    "Can be Sold": "sale_ok",
    "Can be Purchased": "purchase_ok",
    "Product Type": "type",
    "Barcode": "barcode",
    "Sales Price": "list_price",
    "Cost": "standard_price",
    "Product Category": "categ_id",
}

# For getting category ids and searching/creating them
categ_name = "categ_id"
category_cache = {}

# Map of columns which need data cleaned, and for each column, the values to translate to
cleaning_rules = {"type": {"Storable Product": "consu"}}


def open_file(path: str) -> pd.DataFrame:
    """Wrapper for opening filepath

    Args:
        path (str): Path to recordset excel file

    Raises:
        Exception: Bad path given

    Returns:
        pd.DataFrame: Dataframe from the excel file
    """
    try:
        df = pd.read_excel(path)

    except Exception:
        raise Exception(f"Could not open file {path}. Verify file path is correct")

    return df


def create_records(model: str, records: list[dict]) -> list[int]:
    """Creates records from list of dicts in the configured Odoo DB

    Args:
        model (str): Model to make records in
        records (list[dict]): List of record dicts with required fields

    Raises:
        Exception: Bad product input

    Returns:
        list[int]: Ids of records created in DB
    """
    try:
        ids = models.execute_kw(
            db,
            uid,
            password,
            model,
            "create",
            [records],
        )
        return ids
    except Exception as e:
        raise Exception(f"Bad input: {e}")


def parse_products(path: str) -> list[dict]:
    """Extract relevant columns for the products to import and make Odoo formated dicts for each

    Args:
        path (str): Path to excel recordset file

    Returns:
        list[dict]: Odoo formatted list of product records
    """
    # Open the products excel file
    df = open_file(path)

    # Rename relevant columns to odoo names
    df = df.rename(columns=column_map)

    # Select only the relevant columns for odoo importing and transform to dict
    cols = list(column_map.values())
    results = df[cols].to_dict("records")

    return results


def clean_category(category: str) -> dict:
    """Extract the child category from All / <categ> format

    Args:
        category (str): Raw category string from excel file

    Returns:
        dict: String for childmost category of the pair
    """
    # This would need to be changed if they had fancier categories, but they are all "All / <category>"
    return category.split(" / ")[1]


def get_or_create_category(category_name: str) -> int:
    """Creates a product category in the DB or if it exists, returns its ID

    Args:
        category_name (str): Name of category to search

    Returns:
        int: Category id reference
    """

    # Check if category name has already been searched
    if category_name in category_cache:
        return category_cache[category_name]

    # Search for existing category in database
    existing_categories = models.execute_kw(
        db,
        uid,
        password,
        "product.category",
        "search",
        [[["name", "=", category_name]]],
    )

    # Use the ID from DB if there was a match
    if existing_categories:
        category_id = existing_categories[0]
    else:
        # Create new category if there was no match, and link it to "All" parent category
        category_id = create_records(
            "product.category",
            [{"name": category_name, "parent_id": get_or_create_category("All")}],
        )[0]

    # Cache the result either way
    category_cache[category_name] = category_id
    return category_id


def clean_data(products: list[dict]) -> list[dict]:
    """Applies cleaning rules to each product in products dict and inserts category IDs

    Args:
        products (list[dict]): List of products pulled from dataframe

    Returns:
        list[dict]: Products with values cleaned for the columns in cleaning rules dict
    """
    for product in products:
        for col, translation in cleaning_rules.items():
            # Clean values for each of the columns in the rules dict
            product[col] = translation[product[col]]

            # Insert the appropriate category ID
            product["categ_id"] = get_or_create_category(
                clean_category(product["categ_id"])
            )

    return products


if __name__ == "__main__":
    # Get the products all nice for Odoo
    products = clean_data(parse_products("products.xlsx"))
    # Make the records
    create_records("product.template", products)
