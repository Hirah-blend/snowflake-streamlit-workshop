
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

# Retrieve fruit names and API search terms
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
    if row["SEARCH_ON"] is not None
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

        # Keep original fruit name for the order
        ingredients_string += fruit_chosen + " "

        # Get API search value from SEARCH_ON column
        search_term = fruit_options[fruit_chosen]

        # Display search value
        st.write(
            f"The search value for {fruit_chosen} is {search_term}."
        )

        try:
            # Fetch nutrition information
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}",
                timeout=15
            )

            smoothiefroot_response.raise_for_status()

            st.subheader(
                f"{fruit_chosen} Nutrition Information"
            )

            # Show nutrition info as a table (instead of st.json)
            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        except requests.exceptions.RequestException:
            st.warning(
                f"Nutrition information for {fruit_chosen} "
                "could not be retrieved."
            )

    # Submit order
    submit_button = st.button("Submit Order")

    if submit_button:

        if not name_on_order.strip():
            st.error("Please enter a name for your smoothie.")

        else:
            # Insert order into Snowflake
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


    # if submit_button:

    #     if not name_on_order.strip():
    #         st.error("Please enter a name for your smoothie.")
    
    #     else:
    #         # Temporarily disable database insert
    #         st.success(
    #             f"Your Smoothie is ordered, {name_on_order}!",
    #             icon="✅"
    #         )
