# Capstone Project - Cryptocurrency Charting Application

This is my first Capstone project undertaken during my Software Engineering bootcamp at Springboard. The primary goal of my Capstone project was to apply the knowledge gained from the bootcamp, including Python, HTML/Jinja, and Flask, and to challenge myself by learning something new. For this project, I delved into InfluxDB to achieve my goal.

## Project Overview

### Objective

The objective of this project was to create an application that fetches minute-to-minute Bitcoin price data from an API, stores the data, and displays it using a customizable chart powered by InfluxDB.

### Implementation

1. **Webpage and User System:**
   - Created a Flask webpage with a user system.
   - Chart access is restricted to signed-in users.
   - Users are prompted to create an account before gaining access to the Bitcoin chart.

2. **InfluxDB and Docker:**
   - Self-taught InfluxDB and Docker for the application's functionality.
   - The app.py utilizes the cryptocompare API to fetch Bitcoin prices once per minute.
   - Prices are stored in the InfluxDB database while the Flask application is running.

3. **API Used:**
   - Utilized the [CryptoCompare API](https://min-api.cryptocompare.com/documentation).
   - Offers up to 100,000 free pulls per month.

4. **Chart Display:**
   - Integrated Chart.js to display the InfluxDB chart on the Flask application.
   - Customizable chart with time on the X-axis and Bitcoin price on the Y-axis.

### Required API Keys

To run this application on your local machine, you need two personal API keys:

- **InfluxDB API Key:**
  - Obtain the admin API key upon creating a new organization in InfluxDB.
  - Save the key immediately, as it won't be visible again.
  - Note: The API key received upon creating your bucket is not the one needed.

- **CryptoCompare API Key:**
  - Obtain your personal API key by creating an account on [CryptoCompare](https://min-api.cryptocompare.com/pricing).
  - Select a service model, with a free option providing 100,000 free pulls per month.
  - Protect this API key if you plan on uploading to GitHub, as it could be misused.

### Note on InfluxDB Organization and Bucket Names

If you plan to recreate this project for yourself, consider the following for your InfluxDB organization and bucket names in the `app.py` file:

1. **Default Names:**
   - If you prefer not to change names in the `app.py`, simply name your organization and bucket in InfluxDB as 'btcCharter' upon creation.

2. **Custom Names:**
   - If you want to use your custom names for the InfluxDB organization and bucket, make sure to update the `app.py` accordingly.
   - Replace the placeholder names with your chosen organization and bucket names in the code.

Feel free to customize the names to suit your preferences and ensure seamless integration with your InfluxDB setup.

### Future Updates

I plan to implement the following updates in the future:

- **Automatic Chart Updates:**
  - Add the ability for the application to automatically update while the chart is active.

- **Grafana Integration:**
  - Integrate Grafana Charts instead of the InfluxDB chart for a more visually appealing and customizable experience.

Feel free to modify and expand upon this README to suit your project's evolving needs.