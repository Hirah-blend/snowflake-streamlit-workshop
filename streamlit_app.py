
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("""
Choose the fruits you want in your custom Smoothie!
""")

# Customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve fruit names and their API search terms
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Create mapping between display names and API search terms
fruit_options = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in my_dataframe.collect()
    if row["SEARCH_ON"]
}

# Fruit selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    list(fruit_options.keys()),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Keep customer-facing fruit name for the order
        ingredients_string += fruit_chosen + " "

        # Use SEARCH_ON value for API lookup
        search_term = fruit_options[fruit_chosen]

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}",
                timeout=15
            )

            smoothiefroot_response.raise_for_status()

            st.subheader(f"Nutrition information: {fruit_chosen}")

            st.json(smoothiefroot_response.json())

        except requests.exceptions.RequestException as e:
            st.warning(
                f"Nutrition information for {fruit_chosen} "
                f"could not be retrieved."
            )

    # Submit order
    submit_button = st.button("Submit Order")

    if submit_button:

        if not name_on_order.strip():
            st.error("Please enter a name for your smoothie.")

        else:
            # Safely insert order using parameter binding
            session.sql(
                """
                INSERT INTO smoothies.public.orders
                (ingredients, name_on_order)
                VALUES (?, ?)
                """,
                params=[
                    ingredients_string.strip(),
                    name_on_order.strip()
                ]
            ).collect()

            st.success(
                f"Your Smoothie is ordered, {name_on_order}!",
                icon="✅"
            )

