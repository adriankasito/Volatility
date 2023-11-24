# trunk-ignore-all(isort)
#!/usr/bin/env python
# coding: utf-8

# Load Required libraries

# In[1]:


%load_ext autoreload
%autoreload 2
import numpy as np
import seaborn as sns
import os
import sqlite3
from glob import glob
import matplotlib.pyplot as plt
%matplotlib inline
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import joblib
import pandas as pd
import requests
from arch.univariate.base import ARCHModelResult
from config import settings
from data import AlphaVantageAPI, SQLRepository
from arch import arch_model


# In[2]:


ticker = "MSFT"
interval = "1min"
data_type = "json"

url =  ("https://www.alphavantage.co/query?"
        "function=TIME_SERIES_INTRADAY&"
        f"symbol={ticker}&"
        f"interval={interval}&"
        f"datatype=json&"
        f"apikey={settings.alpha_api_key}")

    

print("url type:", type(url))
url


# In[3]:


#Create an HTTP request for the URL you created above
response = requests.get(url=url)

print("response type:", type(response))


# In[4]:


# Get symbol in `"Meta Data"`
symbol_ = response.json()["Meta Data"]["2. Symbol"]
symbol_


# In[5]:


#Get status code of your response and assign it to the variable response_code
response_code = response.status_code

print("code type:", type(response_code))
response_code


# In[6]:


response_data = response.json()
#Extract Time Series[Daily] from the response_data
stock_data = response_data["Time Series (1min)"]
df_msft = pd.DataFrame.from_dict(stock_data, orient="index",dtype=float)

df_msft.index = pd.to_datetime(df_msft.index)
df_msft.index.name = "Date"

df_msft.columns=[c.split('. ')[1] for c in df_msft.columns]
print("df_msft type:", type(df_msft))

df_msft.head()


# In[7]:


#size of the df_msft dataframe
df_msft.shape


# In[8]:


av = AlphaVantageAPI()

df_msft = av.get_daily(ticker="MSFT", interval="1min")
print("df_msft type:", type(df_msft))

df_msft.head()


# Connect to the database whose name is stored in the .env file for this project. Be sure to set the check_same_thread argument to False. Assign the connection to the variable connection.

# In[9]:


connection = sqlite3.connect(settings.db_name, check_same_thread=False)
connection


# In[10]:


# Get location of database for `connection`
db_location = connection.cursor().execute("PRAGMA database_list;").fetchall()[0][-1]
db_location


# In[11]:


#Insert df_msft into your database.
# Import class definition
from data import SQLRepository

# Create instance of class
repo = SQLRepository(connection=connection)

# Does `repo` have a "connection" attribute?
assert hasattr(repo, "connection")

# Is the "connection" attribute a SQLite `Connection`?
assert isinstance(repo.connection, sqlite3.Connection)


# In[12]:


MSFT = df_msft


# In[13]:


response = repo.insert_table(table_name=ticker, records=MSFT, if_exists="replace")

# Does your method return a dictionary?
assert isinstance(response, dict)

# Are the keys of that dictionary correct?
assert sorted(list(response.keys())) == ["records_inserted", "transaction_successful"]


# # Predicting Volatility

# In[14]:


#Create a Series y_msft with the 100000 most recent returns for MSFT
def wrangle_data(ticker, n_observations):

    """Extract table data from database. Calculate returns.

    Parameters
    ----------
    ticker : str
        The ticker symbol of the stock (also table name in database).

    n_observations : int
        Number of observations to return.

    Returns
    -------
    pd.Series
        Name will be `"return"`. There will be no `NaN` values.
    """
    # Get table from database
    df = repo.read_table(table_name=ticker, limit=n_observations+1)


    # Sort DataFrame ascending by date
    df.sort_index(ascending=True, inplace=True)


    # Create "return" column
    df["return"] = pd.to_numeric(
        df["close"], errors="coerce").pct_change()*100


    # Return returns
    return df["return"].dropna()


# In[15]:


from model import GarchModel
y_msft = wrangle_data(ticker="MSFT", n_observations=100000)

print("y_msft type:", type(y_msft))
print("y_msft shape:", y_msft.shape)
y_msft.head()


# Get data for 8 Aug 2022
#data_2023_18_17 = (y_msft["2023-08-17"])
#data_2023_18_17


# In[16]:


#Calculate the per minute volatility for y_mtnoy, and assign the result to mtnoy_per_minute_volatility
msft_per_minute_volatility = y_msft.std()

print("msft_per_minute_volatility type:", type(msft_per_minute_volatility))
print("Microsoft Corporation Per Minute Volatility:", msft_per_minute_volatility)


# In[17]:


#Calculate the daily volatility for y_msft, and assign the result to msft_daily_volatility.
msft_daily_volatility = msft_per_minute_volatility * np.sqrt(1440)

print("msft_daily_volatility type:", type(msft_daily_volatility))
print("Microsoft Corporation Daily Volatility:", msft_daily_volatility)


# In[18]:


msft_annual_volatility = msft_daily_volatility * np.sqrt(252)

print("msft_annual_volatility type:", type(msft_annual_volatility))
print("Microsoft Corporation Annual Volatility:", msft_annual_volatility)


# Create a time series line plot for y_msft. Be sure to label the x-axis "Time", the y-axis "Returns", and use the title "Time Series of Microsfot Corporation Returns"

# In[19]:


# Create `fig` and `ax`
sns.set_style('darkgrid')
fig, ax = plt.subplots(figsize=(9, 4))

# Plot `y_mtnoy` on `ax`
y_msft.plot(ax=ax, label="per_minute return")
# Add axis labels

plt.xlabel("Day-Time")
plt.ylabel("Returns")

# Add title
plt.title("Time Series of Microsfot Corporation Returns")


# Create an ACF plot of the squared returns for MSFT. Be sure to label the x-axis "Lag [minutes]", the y-axis "Correlation Coefficient", and use the title "ACF of Microsoft Corporation Squared Returns".

# In[20]:


# Create `fig` and `ax`

sns.set_style('darkgrid')
fig, ax = plt.subplots(figsize=(9, 4))
# Create ACF of squared returns
plot_acf(y_msft**2, ax=ax)

# Add axis labels
plt.xlabel("Lag [minutes]")
plt.ylabel("Correlation Coefficient")


# Add title
plt.title("ACF of MSFT Squared Returns")


# Create an PACF plot of the squared returns for MSFT. Be sure to label the x-axis "Lag [minutes]", the y-axis "Correlation Coefficient", and use the title "PACF of Microsoft Corporation Squared Returns".

# In[21]:


#Create fig and ax
sns.set_style('darkgrid')
fig, ax = plt.subplots(figsize=(9, 4))
# Create ACF of squared returns
plot_pacf(y_msft**2, ax=ax)

# Add axis labels
plt.xlabel("Lag [minutes]")
plt.ylabel("Correlation Coefficient")


# Add title
plt.title("PACF of MSFT Squared Returns")


# In[22]:


#Create a training set y_msft_train that contains the first 80% of the observations in y_msft.
cutoff_test = int(len(y_msft) * 0.8)
y_msft_train = y_msft.iloc[:cutoff_test].sort_index(ascending=True)

print("y_msft_train type:", type(y_msft_train))
print("y_msft_train shape:", y_msft_train.shape)


# In[23]:


y_msft_train.dropna(inplace=True)


# Build and fit a GARCH model using the data in y_msft. Try different values for p and q, using the summary to assess its performance.

# In[24]:


# Build and train model
model = arch_model(
y_msft_train,
p=1,
q=1,
rescale=False
).fit(disp=0)
print("model type:", type(model))

# Show model summary
model.summary()


# Plot the standardized residuals for your model. Be sure to label the x-axis "Time", the y-axis "Value", and use the title "MSFT GARCH Model Standardized Residuals".

# In[25]:


# Create `fig` and `ax`
sns.set_style('darkgrid')
fig, ax = plt.subplots(figsize=(9,4))

# Plot standardized residuals
model.std_resid.plot(ax=ax, label="Standardized Residuals")

# Add axis labels
plt.xlabel("Day-Time")
plt.ylabel("Value")

# Add legend
plt.legend();


# Create an ACF plot of the squared, standardized residuals of the model. Be sure to label the x-axis "Lag [Time: Minutes]", the y-axis "Correlation Coefficient", and use the title "ACF of MSFT GARCH Model Standardized Residuals".

# In[26]:


sns.set_style('darkgrid')
fig, ax = plt.subplots(figsize=(9, 4))

# Create ACF of squared, standardized residuals
plot_acf(model.std_resid**2, ax=ax)

# Add axis labels
plt.xlabel("Lags [Time: Minutes]")
plt.ylabel("Correlation Coefficient ")
# Add title
plt.title("ACF of MSFT GARCH Model Standardized Residuals")


# # Model Deployment

# Change the fit method of the GarchModel class so that, when the model is done training, two more attributes are added to the object: self.aic with the AIC for the model, and self.bic with the BIC for the model.

# In[27]:


# Import `build_model` function
from main import build_model

# Build model using new `MTNOY` data
model = build_model(ticker="MSFT", use_new_data=False)

# Wrangle `MTNOY` returns
model.wrangle_data(n_observations=100000)



# Fit GARCH(1,1) model to data
model.fit(p=1, q=1)

# Does model have AIC and BIC attributes?
assert hasattr(model, "aic")
assert hasattr(model, "bic")


# In[28]:


# Import `FitIn` class and `fit_model` function
from main import FitIn, fit_model

# Instantiate `FitIn` object
request = FitIn(ticker="MSFT", use_new_data=False, n_observations=100000, p=1, q=1)

# Build model and fit to data, following parameters in `request`
fit_out = fit_model(request=request)

# Inspect `fit_out`
fit_out


# Create a post request to hit the "/fit" path running at "http://localhost:8008". You should train a GARCH(1,1) model on 100000 observations of the MSFT data you already downloaded. Pass in your parameters as a dictionary using the json argument. The grader will evaluate the JSON of your response.

# In[29]:


# URL of `/fit` path
url = "http://localhost:8008/fit"

# Data to send to path
json = {
    "ticker": "MSFT",
    "use_new_data":False,
    "n_observations": 100,
    "p": 1,
    "q":1
}
# Response of post request
response = requests.post(url=url, json=json)
# Inspect response
print("response code:", response.status_code)
response.json()


# In[38]:


# URL of `/predict` path
url = "http://localhost:8008/predict"
# Data to send to path
json = {"ticker": "MSFT", "n_minutes": 66}
# Response of post request
response = requests.post(url, json=json)
print("response type:", type(response))
print("response status code:", response.status_code)


# In[39]:


response.json()


# Go to the command line, navigate to the directory for this project, and start your app server by entering the following command.
# 
# uvicorn main:app --reload --workers 1 --host localhost --port 8008
# Remember how the AlphaVantage API had a "/query" path that we accessed using a get HTTP request? We're going to build similar paths for our application. Let's start with an MVP example so we can learn how paths work in FastAPI.

# In[ ]:




