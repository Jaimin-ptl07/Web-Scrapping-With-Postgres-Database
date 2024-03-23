import os
import requests
from bs4 import BeautifulSoup

def download_pdf(url, folder_path):
    try:
        # Extract the filename from the URL
        filename = os.path.join(folder_path, url.split('/')[-1])

        # Send a GET request to the PDF URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Save the PDF in the specified folder
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"PDF downloaded successfully: {filename}")
        else:
            print(f"Error: Unable to download PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def get_result_urls(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anchor tags within a specific class (modify as needed)
            result_elements = soup.find_all('a', href=True)

            # Extract the 'href' attribute from the result elements
            result_urls = [element['href'] for element in result_elements]

            return result_urls
        else:
            print(f"Error: Unable to fetch the page. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Replace the URL with the one you provided
    target_url = "https://www.ril.com/investors/financial-reporting"

    # Get the resulting URLs from the target website
    result_urls = get_result_urls(target_url)

    # Create a folder to save the PDFs
    folder_path = "reliance"
    os.makedirs(folder_path, exist_ok=True)

    # Download all PDFs into the "reliance" folder
    if result_urls:
        print("Downloading PDFs:")
        for pdf_url in result_urls:
            download_pdf(pdf_url, folder_path)
