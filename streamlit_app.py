
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("""
Choose the fruits you want in your custom Smoothie!
""")

name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")

session = cnx.session()

my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    submit_button = st.button("Submit Order")

    if submit_button:

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES
        ('{ingredients_string.strip()}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )


# New section: Display SmoothieFroot nutrition information

st.header("SmoothieFroot Nutrition Information")

try:
    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/watermelon",
        timeout=15
    )

    smoothiefroot_response.raise_for_status()

    st.dataframe(
        data=smoothiefroot_response.json(),
        use_container_width=True
    )

except requests.RequestException as e:
    st.error(f"Unable to fetch fruit information: {e}")
