# BoilerMake Project

Welcome to the **Pizza Buddy** repository! This project was created as part of the BoilerMake hackathon. 

This README provides an overview of the project, instructions for setting up the development environment, and guidelines for contributing.

## Table of Contents

- [About the Project](#about-the-project)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Contributors](#contributors)

## About the Project

This project aims to provide an interface for users who want to order Pizza from Domino's by talking to a chat bot powered by ChatGPT that can remember previous orders, 
the users' tastes, and the taste of the users' friends (who they have orderd pizza for). The extention can also make suggestions based on the party's dietary restrictions, keeping everyone happy!

## Technologies Used

This project leverages the following technologies:

- **Frontend**: Javascript, HTML, and Tailwind CSS
- **Backend**: FastAPI
- **Database**: JSON based Storage

## Getting Started

To get a local copy up and running, follow these simple steps.

1. Clone this repository using `git clone https://github.com/william-parodi/BoilerMakeProject.git`
2. CD into the repository and the backend folder by executing `cd PizzaBuddy/backend` in the terminal
3. After entering the directory, run the command `pip install -r requirements.txt` to install all the requirements to run the backend
4. Navigate back to the root directory and create the file ".env" and write `OPENAI_API_KEY={INSERT OPENAI API KEY}`
5. To set up the environmment to run the backend run `python -m venv fastapi-env`
6. To enter the environment and run the backend, enter the commmand `.venv/Scripts/activate && cd backend && uvicorn app.main:app --reload`
7. Now, enter `chrome://extensions` and enable developer mode.
8. Select the "Load Unpacked" Option and navigate to the repository and select the folder "gpt-extension"
9. Now, you are able to launch Pizza Buddy on the Domino's webpage to chat and make your favorite pizza orders!

### Prerequisites

Before you begin, ensure you have Python version 3 installed and an ChatGPT API Key

## Contributors
Aditya Chatterjee, Divij Agarwal, William Parodi, Aditya Mishra
