import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv("D:\SPRING(1)\ENG\Final_Project_Signal\Final_Project_ENG\data\calories_burned_data.csv")
# print(df.head()) debug puporse
# print(df.columns)

#keep usefule columns
df = df[[
    'Age',
    'Height(cm)',
    'Weight(kg)',
    'BMI',
    'Average Heart Rate',
    'Distance(km)',
    'Calories Burned',
    'Running Time(min)',
]]

df.to_csv("D:\SPRING(1)\ENG\Final_Project_Signal\Final_Project_ENG\data\cleaned_data.csv", index=False)
#removes the stt columns
df = df.iloc[:, 1:]
# print(df.head())
