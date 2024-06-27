# RoastMyWebsite

RoastMyWebsite is a Streamlit web application that humorously critiques your website. It uses OpenAI's GPT-4 model to generate roasts based on the website's content and appearance.

## Features

- Scrapes website content using requests.
- Captures a screenshot of the website using Selenium.
- Provides humorous critiques in "Mild", "Medium", and "Spicy" tones.
- Uses OpenAI GPT-4 API for generating the roast.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/RoastMyWebsite.git
    cd RoastMyWebsite
    ```

2. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project directory and set your OpenAI API key:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

Run the Streamlit application:

```sh
streamlit run roastmywebsite.py
```

Then open ``http://localhost:8501`` in your web browser.
