# SNS-purchase-analysis
Quantitative Analysis of the Impact of Social Media on Consumer Purchasing Behavior

## Overview

This research investigates how social media (X) affects purchase intention and consumer behavior.

Using posts collected from X (formerly Twitter) and Google Trends data, this research aims to quantitatively analyze the relationship between social media activity and consumer behavior.

## Research Objectives

-Collect posts from X using the X API.
-Analyze user behavior and engagement.
-Extract topics and analyze sentiment from posts.
-Investigate temporal patterns and relationships with Google Trends data.
-Analyze information diffusion through social network structures.

## Research Methods

-Data Collection: X API, Tweepy
-Natural Language Processing: Text preprocessing, topic extraction, sentiment analysis
-Time Series Analysis: Analysis of post activity and Google Trends search interest
-Network Analysis: Analysis of user interactions and information diffusion
-Visualization: Visualization of analytical results

## Technologies

-Python
-Tweepy
-Git / Github
-Google Trends

## Project Structure

SNS-Analysis/
├── src/
│   ├── collect/        # X post data collection
│   ├── preprocess/     # Text preprocessing
│   ├── analysis/       # Data analysis
│   ├── visualization/  # Data visualization
│   └── utils/          # Configuration and utilities
├── data/               # Collected and processed data
├── result/             # Analysis results
├── .gitignore
├── requirements.txt
└── README.md

## Environment

Python

## Development Status

This project is currently under development.

The data collection module is being developed with an emphasis on modular design, error handling, and reproducibility. Further analysis modules will be implemented and expanded as the research progresses.

## Author

Kazuma Furuishi