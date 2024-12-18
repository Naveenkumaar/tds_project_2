# requires-python = ">=3.10"
# dependencies = [
#     "ipykernel",
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "requests",
#     "seaborn",
#     "cchardet",
#     "httpx",
#     "pandas",
# ]
# ///

import sys
import requests
import json
import os
import glob
import base64

from pathlib import Path
import sys
 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
 
from io import StringIO
import math



# Read the API token from environment variables
def get_token():
    try:
        return os.environ["AIPROXY_TOKEN"]
    except KeyError:
        print("Error: AIPROXY_TOKEN environment variable is not set.")
        sys.exit(1)

def generate_readme(df):
     return f"""
    ## Analysis Report
    ## Dataset Overview
    You're an helpful assistant that generates the results strictly in the below format for the given user input,I have a dataset containing [number] records with the following attributes: [list key columns]. The dataset provides information related to [brief description of the dataset’s purpose or domain].
    Key attributes include like important metrics or dimensions.
    The dataset contains {df.shape[0]} rows and {df.shape[1]} columns, providing insights into the data attributes and patterns.
      1.<Highlight key attributes and their importance>.
      2.<Identify any missing or irregular data points>.
      
    ## Analysis Summary
    - **Pairplot**: <Provide the summary results of the  Pairplot and Highlights relationships between numeric attributes>.
    - **Boxplot**: <Provide the summary results related to BoxPlot and Shows distribution and potential outliers in numeric data>.
    - **Heatmap**: <Provide the summary results related to Heatmap among numeric variables>.
    - **statistical overview**: <Compute descriptive statistics for all numerical columns.Analyze key relationships between metrics (e.g., correlations, trends, or interactions between columns)>.
    - **overall analysis**: <Explore unique or categorical values for diversity or coverage insights>.
    
    ## Key Insights
    1. <Summarize significant findings, such as patterns, trends, correlations, or anomalies>.
    2. <Include observations on critical drivers, if any (e.g., factors impacting engagement or ratings)>.
    
    ## Implications of Findings
    - <Suggest actionable strategies or interventions based on the analysis results>.
    - <Highlight opportunities for improvement or optimization within the dataset’s domain>.  
    
    """
 
def create_alternative_visualizations(df, folder):
    try:
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 8))
        
        # Visualization 1: Histogram for numerical columns
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        num_cols = len(numeric_cols)
        rows = math.ceil(num_cols / 3)  # Adjust number of columns per row if needed
        fig, axes = plt.subplots(rows, 3, figsize=(15, 5 * rows))  # 3 columns per row
        axes = axes.flatten()  # Flatten for easy iteration
        for i, col in enumerate(numeric_cols):
            sns.histplot(df[col], bins=30, ax=axes[i], kde=True)  # Add kde=True for density overlay
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel("Frequency")
        # Hide any unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.savefig(f"{folder}/subplots_histograms.png", dpi=100)
        plt.close()
        print("Subplots histograms saved.")

        # Visualization 2: Boxplot
        if len(numeric_cols) > 0:
            sns.boxplot(data=df[numeric_cols])
            plt.xticks(rotation=90, ha='right')
            plt.title("Boxplot of Numeric Columns")
            plt.savefig(f"{folder}/boxplot.png", dpi=100)
            plt.close()
            print("Boxplot saved.")
 
        # Visualization 3: Clustermap with Correlation Matrix
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            sns.clustermap(corr_matrix, annot=True, cmap="coolwarm", fmt=".1f")
            plt.title("Correlation Matrix clustermap")
            plt.savefig(f"{folder}/clustermap.png", dpi=100)
            plt.close()
            print("clustermap saved.")
  
    except Exception as e:
        print(f"Error while generating alternative visualizations: {e}")


def detect_encoding(filepath):
    """Detect encoding without additional package."""
    with open(filepath, 'rb') as f:
        raw_data = f.read(10000)  # Read a portion of the file
    encodings = ["utf-8", "utf-16", "latin1"]  # Common encodings to try
    for encoding in encodings:
        try:
            raw_data.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"  # Fallback to utf-8
 
def read_confidently(filename):
    """Detect encoding and return decoded text and encoding."""
    filepath = Path(filename)
    encoding = detect_encoding(filepath)
    with open(filepath, encoding=encoding) as f:
        text = f.read()
    return text, encoding

def get_csv_files(folder_path):
    files = os.listdir(folder_path)
    csv_files = [file for file in files if file.endswith('.csv')]
    return csv_files
 
def main():
    print("Hello from project2!")
 
    token = get_token()
 
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
 
    # Upload the file manually
    print("Please upload your CSV file.")

        
    for filename in filenames:
        try:
            dataset_path = "./datasets"
            actual_file_path = f"{dataset_path}/{filename}"         
            text, encoding = read_confidently(actual_file_path)
            df = pd.read_csv(actual_file_path, encoding = encoding)
            folder = filename.split('/')[-1].replace('.csv', '')
        except:
            dataset_path = "../datasets"
            actual_file_path = f"{dataset_path}/{filename}"
            text, encoding = read_confidently(actual_file_path)
            df = pd.read_csv(actual_file_path, encoding = encoding)
            folder = filename.split('/')[-1].replace('.csv', '')
    
        current_directory = os.path.dirname(__file__)
        folder = os.path.join(current_directory, folder)
    
        # Create the folder with file name to store the results
        try:
            os.mkdir(folder)
            print('Folder created successfully')
        except:
            print('Folder already present')
    
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
                print("Insights from the generated charts done successfully...")
            else:
                print(f"Error: {response.json()}")
         
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": generate_readme(df),
                },
                {
                    "role": "user",
                    "content": " ".join(
                        [
                            f"chart name is {file.split('/')[-1]} and chart description is {desc}"
                            for file, desc in zip(file_list[:len(image_description)], image_description)
                        ]
                    ) + f" and {json.dumps(message)}",
                },
            ],
        }
        response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", headers=headers, json=data)
    
        if response.status_code == 200:
            response_json = response.json()
            output = response_json['choices'][0]['message']['content']
            print("Final content of analysis has been generated successfully.")
        else:
            output = str(response.json())
            print(f"Error: {response.json()}")
    
        with open(f"{folder}/README.md", 'w') as file_:
            file_.write(output)
            print("Program run completed successfully.")
 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
        main()
    else:
        print("Usage: uv run autolysis.py <CSV_FILENAME>")
