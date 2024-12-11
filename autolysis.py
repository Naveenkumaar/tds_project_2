# requires-python = ">=3.10"
# dependencies = [
#     "ipykernel",
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "requests",
#     "seaborn",
# ]
# ///

import sys
import requests
import json
import os
import glob
import base64
from io import StringIO
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Read the API token from environment variables
def get_token():
    try:
        return os.environ["AIPROXY_TOKEN"]
    except KeyError:
        print("Error: AIPROXY_TOKEN environment variable is not set.")
        sys.exit(1)

def generate_image_from_text_input(folder, text, df):
    text = text.replace("`", '')
    text = text.replace("python", '')
    cur_dic = os.getcwd()
    try:
        os.chdir(folder)
        exec(text)
        print(' Image Generated')
        return 'success image generated'
    except Exception as e:
        print(e)
        return f'Python code has failed with the error {e}'
    finally:
        os.chdir(cur_dic)

def create_alternative_visualizations(df, folder):
    try:
        sns.set(style="whitegrid")
        plt.figure(figsize=(10, 6))

        # Visualization 1: Pairplot for numerical columns
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            sns.pairplot(df[numeric_cols])
            plt.savefig(f"{folder}/pairplot.png")
            plt.close()
            print("Pairplot saved.")

        # Visualization 2: Boxplot
        if len(numeric_cols) > 0:
            sns.boxplot(data=df[numeric_cols])
            plt.title("Boxplot of Numeric Columns")
            plt.savefig(f"{folder}/boxplot.png")
            plt.close()
            print("Boxplot saved.")

        # Visualization 3: Heatmap of Correlation Matrix
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Matrix Heatmap")
            plt.savefig(f"{folder}/heatmap.png")
            plt.close()
            print("Heatmap saved.")

    except Exception as e:
        print(f"Error while generating alternative visualizations: {e}")

def main():
    print("Hello TDS Project 2")

    token = get_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Upload the file manually
    print("Please upload your CSV file.")

    df = pd.read_csv(filename, encoding='latin-1')
    folder = filename.split('/')[-1].replace('.csv', '')

    # Create the folder with file name to store the results
    try:
        os.mkdir(folder)
        print('Folder created successfully')
    except:
        print('Folder already present')

    current_directory = os.getcwd()
    folder = os.path.join(current_directory, folder)

    message = ''
    buffer = StringIO()
    df.info(buf=buffer)
    text = buffer.getvalue()

    message = {'dataframe column details': text}
    text = df.describe().to_dict()
    message['dataframe describe'] = text

    # Generate alternative visualizations directly
    create_alternative_visualizations(df, folder)

    # Convert images to base64
    file_list = glob.glob(f"{folder}/*.png")
    image_list = []
    for image in file_list:
        with open(image, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            image_list.append(encoded_image)

    image_description = []
    for image in file_list:
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": f"You will be given a chart from {filename} dataset, get insights from this {image.split('/')[-1]} image"},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}", "detail": "low"}}
                ]}
            ]
        }

        response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            image_description.append(response_json['choices'][0]['message']['content'])
            print("Insights from the generated charts have been generated successfully.")
        else:
            print(f"Error: {response.status_code}")

    # Final narration generation
    image1, image2, image3 = [file.split('/')[-1] for file in file_list[:3]]
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"You will be given details {filename}, along with 3 chart descriptions. Describe the dataset, analysis, insights, and implications."},
            {"role": "user", "content": json.dumps(message)},
            {"role": "user", "content": f"chart name is {image1} and chart description is {image_description[0]}"},
            {"role": "user", "content": f"chart name is {image2} and chart description is {image_description[1]}"},
            {"role": "user", "content": f"chart name is {image3} and chart description is {image_description[2]}"}
        ]
    }

    response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        output = response_json['choices'][0]['message']['content']
        print("Analysis has been generated successfully.")
    else:
        print(f"Error: {response.status_code}")

    with open(f"{folder}/README.md", 'w') as file:
        file.write(output)
        print("Code run successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]  # Get the file name from the command-line argument
        main(filename,get_token())
    else:
        print("Usage: python autolysis.py <CSV_FILENAME>")
