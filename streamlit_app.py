import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col
 
st.set_page_config(
    page_title="Custom Smoothie Order Form",
    page_icon="🥤",
)
 
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom smoothie!")
 
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)
 
cnx = st.connection("snowflake")
session = cnx.session()
 
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON"),
)
 
pd_df = my_dataframe.to_pandas()
fruit_options = pd_df["FRUIT_NAME"].tolist()
 
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5,
)
 
if ingredients_list:
    ingredients_string = ""
 
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
 
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON",
        ].iloc[0]
 
        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            ".",
        )
 
        st.subheader(f"{fruit_chosen} Nutrition Information")
 
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
 
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True,
        )
 
    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
        VALUES
            ('{ingredients_string}', '{name_on_order}')
    """
 
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
 
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅",
        )
