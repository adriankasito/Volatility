# Volatility Forecasting for Microsoft Corporation

## Project Overview

This project aims to develop a system for real-time volatility forecasting for Microsoft Corporation's financial data. The system uses minute-level data to predict volatility, which can be valuable for risk management and trading strategies.

## Project Structure

The project is organized into several modules and files:

1. **config.py**: This module extracts information from your `.env` file and sets up configurations for the project. It includes settings for your AlphaVantage API key, database name, and model directory.

2. **main.py**: The main FastAPI application where you can interact with the volatility forecasting system. It provides endpoints for fitting the model and obtaining real-time volatility predictions.

3. **data.py**: Contains code for interacting with the AlphaVantage API to fetch financial data and the SQLite database for data storage. The `AlphaVantageAPI` class is used to retrieve minute-level data, and the `SQLRepository` class handles data insertion and retrieval from the database.

4. **model.py**: This module is responsible for training the GARCH (Generalized Autoregressive Conditional Heteroskedasticity) model for volatility forecasting. It includes functions to wrangle the data, fit the model, predict volatility, and save/load the trained model. The `GarchModel` class manages the entire modeling process.

## Getting Started

Before running the project, make sure you set up your `.env` file with your AlphaVantage API key and configure the database name and model directory in the `config.py` module.

```python
alpha_api_key="YOUR_API_KEY"
db_name="your_database_name.db"
model_directory="your_model_directory_path"
