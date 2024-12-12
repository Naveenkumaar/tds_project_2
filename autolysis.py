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

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from io import StringIO
from sklearn.cluster import KMeans


# Read the API token from environment variables
def get_token():
    try:
        return os.environ["AIPROXY_TOKEN"]
    except KeyError:
        print("Error: AIPROXY_TOKEN environment variable is not set.")
        sys.exit(1)

def generate_readme(df):
    return f"""
    You're an helpful assistant that generates the results strictly in the below format for the given user input, not just returning the format.
    # Analysis Report
    
    ## Dataset Overview
    The dataset contains {df.shape[0]} rows and {df.shape[1]} columns, providing insights into the data attributes and patterns.
    
    ## Analysis Summary
    - **Pairplot**: <Understand the user input related to Pairplot and Highlights relationships between numeric attributes>.
    - **Boxplot**: <Understand the user input related to BoxPlot and Shows distribution and potential outliers in numeric data>.
    - **Heatmap**: <Understand the user input related to Heatmap and Visualizes correlations among numeric variables>.
    - **Cluster Analysis**: <Understand the user input related to Cluster_analysis and Highlights clusters in data based on key numeric attributes>.
    
    ## Key Insights
    1. <Significant correlations observed between key attributes in Heatmap and Pairplot>.
    2. <Outliers detected in numeric attributes indicating anomalies from BoxPlot>.
    3. <Clustered patterns suggesting distinct group behaviors from cluster_analysis>.
    
    ## Implications of Findings
    - <Utilize insights for data-driven decision-making in Heatmap and Pairplot>.
    - <Address anomalies for improved data quality from the Boxplot>.
    - <Leverage cluster analysis for targeted strategies from cluster_analysis>.
    
    """

def create_alternative_visualizations(df, folder):
    try:
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 8))

        # Visualization 1: Pairplot for numerical columns
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            sns.pairplot(df[numeric_cols])
            plt.savefig(f"{folder}/pairplot.png", dpi=100)
            plt.close()
            print("Pairplot saved.")

        # Visualization 2: Boxplot
        if len(numeric_cols) > 0:
            sns.boxplot(data=df[numeric_cols])
            plt.xticks(rotation=90, ha='right')
            plt.title("Boxplot of Numeric Columns")
            plt.savefig(f"{folder}/boxplot.png", dpi=100)
            plt.close()
            print("Boxplot saved.")

        # Visualization 3: Heatmap of Correlation Matrix
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Matrix Heatmap")
            plt.savefig(f"{folder}/heatmap.png", dpi=100)
            plt.close()
            print("Heatmap saved.")

        # Visualization 4: Cluster Analysis
        if len(numeric_cols) > 1:
            kmeans = KMeans(n_clusters=5)
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            # df['Cluster'] = kmeans.fit_predict(df[numeric_cols].dropna())
            df['Cluster'] = kmeans.fit_predict(df[numeric_cols])
            sns.scatterplot(x=numeric_cols[0], y=numeric_cols[1], hue='Cluster', data=df, palette="viridis")
            plt.title("Cluster Analysis")
            plt.savefig(f"{folder}/cluster_analysis.png", dpi=100)
            plt.close()
            print("Cluster analysis saved.")

    except Exception as e:
        print(f"Error while generating alternative visualizations: {e}")

def main():
    print("Hello from project2!")

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
            print("Insights from the generated charts done successfully...")
        else:
            print(f"Error: {response.status_code}")

    # Final narration generation
    image1, image2, image3, image4 = [file.split('/')[-1] for file in file_list[:4]]
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"{generate_readme(df)}"},
            {"role": "user", "content": f"chart name is {image1} and chart description is {image_description[0]} and chart name is {image2} and chart description is {image_description[1]} and chart name is {image3} and chart description is {image_description[2]} and chart name is {image4} and chart description is {image_description[3]} and {json.dumps(message)}"}
        ]
    }
    
    response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        output = response_json['choices'][0]['message']['content']
        print("Final content of analysis has been generated successfully.")
    else:
        print(f"Error: {response.status_code}")

    with open(f"{folder}/README.md", 'w') as file:
        file.write(output)
        print("Program run completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        main()
    else:
        print("Usage: uv run autolysis.py <CSV_FILENAME>")
