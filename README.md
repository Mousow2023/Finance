# CS50x Finance Project

## Overview

The **CS50x Finance** project is a web application that allows users to simulate a stock trading platform. Users can create accounts, log in, and manage a portfolio by buying and selling stocks using real-time stock data. This project is built with **Python (Flask)** on the backend and **HTML/CSS** for the frontend, along with a **SQLite** database to store user data and transactions. Real-time stock prices are retrieved using the **IEX Cloud API**.

## Features

- **User Registration and Authentication**: Users can create an account and securely log in.
- **Stock Lookup**: Search for real-time stock prices by entering the stock symbol.
- **Buy Stocks**: Purchase shares of a stock, which will be deducted from the user's cash balance.
- **Sell Stocks**: Sell previously purchased shares and update the user's cash balance.
- **Portfolio Overview**: View current holdings, including stock symbols, the number of shares owned, and their current value.
- **Transaction History**: Track all buy and sell transactions with timestamps.
- **User Dashboard**: Displays the user's cash balance and portfolio with real-time stock prices.

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, Jinja (Flask's templating engine)
- **Database**: SQLite
- **APIs**: IEX Cloud API for stock prices
- **Version Control**: Git

## Prerequisites

Before running this project, ensure you have the following installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/)
- An API key from [IEX Cloud](https://iexcloud.io/) for stock price data

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cs50-finance.git
cd cs50-finance
