# tds_project_2
LLM output
Project 2 - Automated Analysis
This project is due on 12 Dec 2024 EoD AoE. Results will be announced by 22 Dec 2024.

Your task is to:

Write a Python script that uses an LLM to analyze, visualize, and narrate a story from a dataset.
Convince an LLM that your script and output are of high quality.
This project is not just a test of what you learned. It also teaches you new things. Check the reading material below.

Write a Python script
Your submission must be a Python script, autolysis.py submitted via a Git repository.

The Python script must accept a single CSV filename like below. (Read about uv. Inline your dependencies.)

uv run autolysis.py dataset.csv
This should create, in your current directory, the following files:

A single Markdown file called README.md with results of your automated analysis, written as a story.
1-3 charts as PNG providing supporting data visualizations. Name them as *.png. Add the images in your README.md.
You can try this on these sample datasets:

goodreads.csv: 10,000 books from GoodReads with their genres, ratings, etc.
happiness.csv: Data from the World Happiness Report
media.csv: The course faculty's rating of movies, TV series, and books.
Notes:

Create a single Python script: Don't load other local scripts (e.g. utils.py) or files (e.g. system-prompt.txt). Keep the entire code in autolysis.py. This eases LLM evaluation.
Use your AI Proxy token. Your AI Proxy token now has a $2 limit. You may use it. If you run out of tokens, ask the TDS team for more. (But try and avoid that.)
Use the AIPROXY_TOKEN environment variable. DON'T commit your AI Proxy token to your repository. Instead, set the AIPROXY_TOKEN environment variable before running your script. Use os.environ["AIPROXY_TOKEN"] as the token in your script.
Stick to GPT-4o-Mini. This is the only generation model that AI Proxy currently supports. When this page says "LLM", it means GPT-4o-Mini.
Analyze the data
Your script should work with any valid CSV file.

Since you don't know in advance what the data looks like, don't make assumptions. Instead:

Do generic analysis that will apply to all datasets. For example, summary statistics, counting missing values, correlation matrices, outliers, clustering, hierarchy detection, etc.
Ask the LLM to analyze the data. Send the LLM your filename, column names & types, and additional context (like summary statistics, example values, etc.) to the LLM. Then
For code. Have the LLM give you Python code and run it. This is risky because LLM code might fail and your program might terminate. Use with caution.
For summaries. Have the LLM summarize your generic analysis. Use liberally.
For function calls. Have the LLM suggest specific function calls or analyses that will give you more insights, and run them. Use liberally. Read the OpenAI Function Calling docs.
Here are some ideas for analysis that may be insightful. Some of these are covered in this course, but don't limit yourself.

Outlier and Anomaly Detection: You might find errors, fraud, or high-impact opportunities.
Correlation Analysis, Regression Analysis, and Feature Importance Analysis: You might find what to improve to impact an outcome.
Time Series Analysis: You might find patterns that help predict the future.
Cluster Analysis: You might find natural groupings for targeted marketing or resource allocation.
Geographic Analysis: You might find where the biggest problems or opportunities are.
Network Analysis: You might find what to cross-sell or collaborate with.
Notes:

Don't send the entire dataset to the LLM: LLMs are bad at numbers - even arithmetic. Also, you'll run out of tokens. Instead, do your analysis in Python and send relevant summaries.
You can consult the LLM multiple times. If one analysis doesn't work, ask for another. Or, share the results of one analysis to help the next one.
Visualize your results
When you have your analysis, visualize the results.

For analysis that you wrote the code for, you know the structure of the output. So you can write functions to create the chart(s) for the structure they generate.

For example, if you create a correlation matrix, you can write a function to visualize it as a heatmap.

You need a Python-based library to create charts. We suggest Seaborn but you're welcome to use Matplotlib. We wouldn't recommend Bokeh, Plotly or Altair unless you know how to get them to work without a browser.

You could get creative and ask the LLM to generate the code for your chart based on the data. This is risky because LLM code might fail and your program might terminate. Use with caution.

Notes:

Export as PNG. Save all your charts as PNG files (with different file names) in the current directory.
Don't send the entire analysis to the LLM. You might run out of tokens. Send only what might be significant analysis.
Narrate a story
Use the LLM to write a story about your analysis. You can pass it your data structure, analysis, and even your charts. Have it describe:

The data you received, briefly
The analysis you carried out
The insights you discovered
The implications of your findings (i.e. what to do with the insights)
Save this as README.md.

Notes:
Keep images small. 512x512 px images are ideal. That's the size of 1 tile. Or, send detail: low to reduce cost. Read the LLM Vision Models module and the OpenAI Vision API docs
Submit your script
Create a new public repository in your GitHub account with an MIT license.
Add your code: autolysis.py
Create directories called goodreads/, happiness/, and media/.
Run your script on the respective CSV files and commit the output in that directory. (Don't commit the input CSVs. Just README.md and *.png files.)
Commit and push these.
