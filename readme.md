# Snap2Site

Snap2Site is a web application that allows users to upload images, process them, and generate web page templates based on the uploaded images.

## Features

- Upload photos
- Generate web page templates
- Customize generated templates

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/kaizeroman/Snap2site
    ```

2. Install dependencies:

    ```bash
    pip install roboflow
    pip install flask
    ```

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Upload an image by clicking the "Upload Photo" button.

4. Click the "Continue" button to process the uploaded image.

5. Once processing is complete, the generated web page template will be displayed.

6. Edit the webpage template by selecting page palette and fonts

7. Once edited, your final Snap2Site webpage html code and preview is displayed

## Folder Structure
SNAP2SITE/ 
│
├── static/             # Static assets (images)
│   └── logo.png
│   └── bg.png
│
├── templates/          # HTML codes
│   └── generate.html
│   └── index.html
│   └── start.html
│   └── snap2site-result.html
│
├── app.py              # Flask application
├── README.md           # Project documentation
│
└── unseen-set/         # Unseen dataset (website screenshots)

## Files
- index.html: Introduces the website to the user, serves as the landing page of the website

- start.html: Enables users to upload a screenshot of the webpage they want to transform to a template

- generate.html: Displays the html code and preview of the webpage template, and enables the user to add color palette and fonts for  the template

- app.py: contains the backend part of the website using Flask
