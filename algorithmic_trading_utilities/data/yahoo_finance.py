"""
Yahoo Finance data provider module.

This module provides access to Yahoo Finance market screeners and data feeds
for stock discovery and market analysis.
"""

from yahooquery import Screener
import pandas as pd
import time

# List of useful yfinance screeners for reference
SCREENERS = [
    "accident_health_insurance",
    "advertising_agencies",
    "aerospace_defense_major_diversified",
    "aerospace_defense_products_services",
    "aggressive_small_caps",
    "agricultural_chemicals",
    "air_delivery_freight_services",
    "air_services_other",
    "all_cryptocurrencies_au",
    "all_cryptocurrencies_ca",
    "all_cryptocurrencies_eu",
    "all_cryptocurrencies_gb",
    "all_cryptocurrencies_in",
    "all_cryptocurrencies_us",
    "aluminum",
    "apparel_stores",
    "appliances",
    "application_software",
    "asset_management",
    "auto_dealerships",
    "auto_manufacturers_major",
    "auto_parts",
    "auto_parts_stores",
    "auto_parts_wholesale",
    "basic_materials",
    "basic_materials_wholesale",
    "beverages_brewers",
    "beverages_soft_drinks",
    "beverages_wineries_distillers",
    "biotechnology",
    "broadcasting_radio",
    "broadcasting_tv",
    "building_materials_wholesale",
    "business_equipment",
    "business_services",
    "business_software_services",
    "catalog_mail_order_houses",
    "catv_systems",
    "cement",
    "chemicals_major_diversified",
    "cigarettes",
    "cleaning_products",
    "closedend_fund_debt",
    "closedend_fund_equity",
    "closedend_fund_foreign",
    "communication_equipment",
    "computer_based_systems",
    "computer_peripherals",
    "computers_wholesale",
    "confectioners",
    "conglomerates",
    "conservative_foreign_funds",
    "consumer_defensive",
    "consumer_goods",
    "consumer_services",
    "copper",
    "credit_services",
    "dairy_products",
    "data_storage_devices",
    "day_gainers",
    "day_gainers_americas",
    "day_gainers_asia",
    "day_gainers_au",
    "day_gainers_br",
    "day_gainers_ca",
    "day_gainers_de",
    "day_gainers_dji",
    "day_gainers_es",
    "day_gainers_europe",
    "day_gainers_fr",
    "day_gainers_gb",
    "day_gainers_hk",
    "day_gainers_in",
    "day_gainers_it",
    "day_gainers_ndx",
    "day_gainers_nz",
    "day_gainers_sg",
    "day_losers",
    "day_losers_americas",
    "day_losers_asia",
    "day_losers_au",
    "day_losers_br",
    "day_losers_ca",
    "day_losers_de",
    "day_losers_dji",
    "day_losers_es",
    "day_losers_europe",
    "day_losers_fr",
    "day_losers_gb",
    "day_losers_hk",
    "day_losers_in",
    "day_losers_it",
    "day_losers_ndx",
    "day_losers_nz",
    "day_losers_sg",
    "department_stores",
    "diagnostic_substances",
    "discount_variety_stores",
    "diversified_communication_services",
    "diversified_computer_systems",
    "diversified_electronics",
    "diversified_investments",
    "diversified_machinery",
    "diversified_utilities",
    "drug_delivery",
    "drug_manufacturers_major",
    "drug_manufacturers_other",
    "drug_related_products",
    "drug_stores",
    "drugs_generic",
    "drugs_wholesale",
    "education_training_services",
    "electric_utilities",
    "electronic_equipment",
    "electronics_stores",
    "electronics_wholesale",
    "entertainment_diversified",
    "fair_value_screener",  # Undervalued stocks with strong & consistent earnings/revenue growth
    "farm_construction_machinery",
    "farm_products",
    "financial",
    "food_major_diversified",
    "food_wholesale",
    "foreign_money_center_banks",
    "foreign_regional_banks",
    "foreign_utilities",
    "gaming_activities",
    "gas_utilities",
    "general_building_materials",
    "general_contractors",
    "general_entertainment",
    "gold",
    "grocery_stores",
    "growth_technology_stocks",
    "health_care_plans",
    "healthcare",
    "healthcare_information_services",
    "heavy_construction",
    "high_yield_bond",  # High Yield Bond with Performance Rating of 4 & 5
    "home_furnishing_stores",
    "home_furnishings_fixtures",
    "home_health_care",
    "home_improvement_stores",
    "hospitals",
    "hotels_motels",
    "household_personal_products",
    "independent_oil_gas",
    "industrial_electrical_equipment",
    "industrial_equipment_wholesale",
    "industrial_metals_minerals",
    "information_technology_services",
    "insurance_brokers",
    "insurance_diversified",
    "insurance_life",
    "insurance_property_casualty",
    "integrated_oil_gas",
    "internet_information_providers",
    "internet_software_services",
    "investment_brokerage_national",
    "investment_brokerage_regional",
    "jewelry_stores",
    "lumber_wood_production",
    "machine_tools_accessories",
    "major_airlines",
    "major_drugs",
    "major_integrated_oil_gas",
    "management_services",
    "manufactured_housing",
    "marine_shipping",
    "medical_appliances_equipment",
    "medical_equipment_wholesale",
    "medical_instruments_supplies",
    "medical_laboratories_research",
    "medical_practitioners",
    "metal_fabricating",
    "midscore_growth",
    "mobile_telecommunications",
    "money_center_banks",
    "mortgage_investment",
    "most_actives",
    "motor_vehicles",
    "movie_entertainment",
    "multimedia_graphics_software",
    "music",
    "natural_gas_distribution",
    "networking_communication_devices",
    "nonferrous_metals",
    "oil_gas_drilling",
    "oil_gas_equipment_services",
    "oil_gas_integrated",
    "oil_gas_pipelines",
    "oil_gas_refining_marketing",
    "optical_networking",
    "other_consumer_services",
    "other_specialty_stores",
    "packaging_containers",
    "paper_lumber",
    "personal_computers",
    "personal_products",
    "photographic_equipment_supplies",
    "plastic_rubber",
    "pollution_treatment_controls",
    "printing_services",
    "processed_packaged_goods",
    "property_casualty_insurance",
    "publishing_books",
    "publishing_newspapers",
    "publishing_periodicals",
    "real_estate_development",
    "real_estate_diversified",
    "real_estate_investment_trusts",
    "real_estate_operations",
    "recreational_activities",
    "recreational_products",
    "recreational_vehicles",
    "regional_mid_atlantic_banks",
    "regional_midwest_banks",
    "regional_northeast_banks",
    "regional_pacific_banks",
    "regional_southeast_banks",
    "regional_southwest_banks",
    "reit_diversified",
    "reit_healthcare_facilities",
    "reit_hotel_motel",
    "reit_industrial",
    "reit_office",
    "reit_residential",
    "reit_retail",
    "rental_leasing_services",
    "research_services",
    "residential_construction",
    "resorts_casinos",
    "restaurants",
    "rubber_plastics",
    "savings_loans",
    "scientific_technical_instruments",
    "security_protection_services",
    "security_software_services",
    "semiconductor_broad_line",
    "semiconductor_equipment_materials",
    "semiconductor_integrated_circuits",
    "semiconductor_memory_chips",
    "semiconductor_specialized",
    "services",
    "shipping",
    "silver",
    "small_cap_gainers",  # Small Caps with 1 day price change of 5.0% or more
    "small_tools_accessories",
    "solid_large_growth_funds",
    "solid_midcap_growth_funds",
    "specialized_health_services",
    "specialty_chemicals",
    "specialty_eateries",
    "specialty_retail_other",
    "sporting_activities",
    "sporting_goods",
    "sporting_goods_stores",
    "staffing_outsourcing_services",
    "steel_iron",
    "surety_title_insurance",
    "synthetics",
    "technical_services",
    "technical_system_software",
    "technology",
    "telecom_services_domestic",
    "telecom_services_foreign",
    "textile_apparel_clothing",
    "textile_apparel_footwear_accessories",
    "textile_industrial",
    "tobacco_products_other",
    "top_energy_us",
    "top_etfs",  # ETFs with Performance Rating of 4 & 5 ordered by Percent Change
    "top_etfs_hk",
    "top_etfs_in",
    "top_etfs_us",
    "top_iv_options_us",
    "top_mutual_funds",
    "top_mutual_funds_au",
    "top_mutual_funds_br",
    "top_mutual_funds_ca",
    "top_mutual_funds_de",
    "top_mutual_funds_es",
    "top_mutual_funds_fr",
    "top_mutual_funds_gb",
    "top_mutual_funds_hk",
    "top_mutual_funds_in",
    "top_mutual_funds_it",
    "top_mutual_funds_nz",
    "top_mutual_funds_sg",
    "top_mutual_funds_us",
    "top_options_implied_volatality",
    "top_options_open_interest",
    "toy_hobby_stores",
    "toys_games",
    "trucking",
    "trucks_other_vehicles",
    "undervalued_growth_stocks",  # Stocks with earnings growth >25% and low PE/PEG ratios
    "undervalued_large_caps",  # Large cap stocks that are potentially undervalued
    "utilities",
    "waste_management",
    "water_utilities",
    "wireless_communications",
]


def get_stock_gainers_table():
    """
    Get the table of stock gainers for the day with retry logic to handle rate limits.

    Returns:
        pandas.DataFrame: A DataFrame containing information about the top stock gainers for the day, filtered by LargeCap.
            Columns include 'exchange', 'symbol', 'shortName', 'regularMarketChangePercent', and 'fiftyDayAverageChangePercent'.
    """
    s = Screener()
    max_retries = 5
    delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            data = s.get_screeners(
                ["day_gainers"], 250
            )  # Fetch data from Yahoo Finance
            gainers_df = pd.DataFrame(data["day_gainers"]["quotes"])

            try:
                # Filter by LargeCap
                gainers_df = gainers_df[gainers_df["marketCap"] >= 10000000000]

                # Filter by tradeable
                # gainers_df = gainers_df[gainers_df['tradeable']=='True']

                gainers_df = gainers_df[
                    [
                        "exchange",
                        "symbol",
                        "shortName",
                        "regularMarketChangePercent",
                        "fiftyDayAverageChangePercent",
                    ]
                ]
                return gainers_df

            except KeyError:
                gainers_df = pd.DataFrame(
                    columns=[
                        "exchange",
                        "symbol",
                        "shortName",
                        "regularMarketChangePercent",
                        "fiftyDayAverageChangePercent",
                    ]
                )
                return gainers_df

        except Exception as e:
            if "429" in str(e):  # Handle rate limit errors
                print(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Error fetching stock gainers: {e}")
                raise

    raise Exception("Failed to fetch stock gainers table after multiple retries.")


def get_screener_data(screener_name, count=250):
    """
    Get data from a specific Yahoo Finance screener.

    Args:
        screener_name (str): Name of the screener from the SCREENERS list
        count (int): Number of results to return (default: 250)

    Returns:
        pandas.DataFrame: DataFrame containing the screener results
    """
    if screener_name not in SCREENERS:
        raise ValueError(
            f"Screener '{screener_name}' not found. Available screeners: {SCREENERS}"
        )

    s = Screener()
    max_retries = 5
    delay = 1

    for attempt in range(max_retries):
        try:
            data = s.get_screeners([screener_name], count)
            return pd.DataFrame(data[screener_name]["quotes"])
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error fetching screener data: {e}")
                raise

    raise Exception(
        f"Failed to fetch {screener_name} screener data after multiple retries."
    )
