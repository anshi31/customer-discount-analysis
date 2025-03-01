import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Load customer data
customers = pd.read_csv('data/customers.csv')
customers.head()


# Load orders data
orders = pd.read_csv('data/orders1.csv')
orders.head()

# Load sales data
sales = pd.read_csv('data/sales_data.csv')
sales.head()

## **Task 1**: Segment customers into high-value, frequent, and occasional buyers using K-Means clustering.


# Add avg_order_value to differentiate between frequent small buyers and occasional big spenders
# Calculate average order value
customers['avg_order_value'] = customers['total_spend'] / customers['num_orders']


# Add recency_days (days since last order) to identify active vs inactive buyers.
# Convert last_order_date to datetime
customers['last_order_date'] = pd.to_datetime(customers['last_order_date'])
    
# Calculate recency in days
latest_date = customers['last_order_date'].max()
customers['recency_days'] = (latest_date - customers['last_order_date']).dt.days

# Select relevant features for clustering
X = customers[['total_spend', 'num_orders', 'avg_order_value', 'recency_days']]


# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Using n_clusters=3 as per requirement to segment into high-value, frequent, and occasional buyers
kmeans = KMeans(n_clusters=3, random_state=42)
customers['segment'] = kmeans.fit_predict(X_scaled)


# Compute the average values per cluster
segment_analysis = customers.groupby('segment').mean(numeric_only=True)

# Sort to ensure "High-Value" buyers are recent & spend the most - New buyers should rank higher
segment_analysis = segment_analysis.sort_values(by=['total_spend', 'num_orders', 'recency_days'], 
                                              ascending=[True, True, False])

# Assign cluster labels correctly
segment_labels = {
    segment_analysis.index[0]: 'Occasional Buyer',  # Lowest spend & orders
    segment_analysis.index[1]: 'Frequent Buyer',   # Mid-range
    segment_analysis.index[2]: 'High-Value Buyer'  # Highest spend & orders
}

# Map the cluster labels to customer data
customers['segment_label'] = customers['segment'].map(segment_labels)
customers.head()

# Visualizing Customer Segments
plt.figure(figsize=(8, 6))
sns.scatterplot(data=customers, x='num_orders', y='total_spend', hue='segment_label', palette='viridis')
plt.xlabel("Number of Orders")
plt.ylabel("Total Spend")
plt.title("Customer Segments")
plt.show()


## **Task 2**: Analyze sales trends to identify peak ordering periods.

orders['order_date'] = pd.to_datetime(orders['order_date'], format='%d-%m-%Y')

# Orders by month
orders['month'] = orders['order_date'].dt.strftime('%b')
monthly_orders = orders.groupby('month').size().reset_index(name='count')

# Orders by day
orders['day'] = orders['order_date'].dt.strftime('%A')
daily_orders = orders.groupby('day').size().reset_index(name='count')

# Sales by category
category_sales = sales.groupby('category')['revenue'].sum().reset_index()

# Sales by region
region_sales = sales.groupby('region')['revenue'].sum().reset_index()

# Find peaks
peak_month = monthly_orders.loc[monthly_orders['count'].idxmax()]
peak_day = daily_orders.loc[daily_orders['count'].idxmax()]
top_region = region_sales.loc[region_sales['revenue'].idxmax()]

print("Key Insights:")
print(f"Peak Month: {peak_month['month']} with {peak_month['count']} orders")
print(f"Peak Day: {peak_day['day']} with {peak_day['count']} orders")
print(f"Top Region: {top_region['region']} with {top_region['revenue']:,.2f} in sales")



# Sales by Day of the Week
plt.figure(figsize=(8, 4))
sns.barplot(x='day', y='count', data=daily_orders, palette='coolwarm')
plt.xlabel("Day of the Week")
plt.ylabel("Number of Orders")
plt.title("Sales by Weekday")
plt.xticks(rotation=45)
plt.show()


## **Task 3**: Visualize customer segments and order patterns using graphs.

# Scatter Plot: Total Spend vs. Number of Orders (Customer Segmentation)
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=customers['num_orders'],
    y=customers['total_spend'],
    hue=customers['segment'],  # Segments from K-Means
    palette='Set1'
)
plt.xlabel("Number of Orders")
plt.ylabel("Total Spend")
plt.title("Customer Segmentation Based on Spending & Order Frequency")
plt.legend(title="Customer Segment")
plt.grid()
plt.show()


# Customer Segment Distribution (Pie Chart)
plt.figure(figsize=(6, 6))
segment_counts = customers['segment'].value_counts()
labels = [segment_labels.get(i, f"Cluster {i}") for i in segment_counts.index]  # Handle missing labels
plt.pie(segment_counts, labels=labels, autopct='%1.1f%%', colors=['blue', 'orange', 'green'])
plt.title('Customer Segment Distribution')
plt.show()

# Merge orders with customer segmentation info
orders['month_num'] = orders['order_date'].dt.month
monthly_segment_orders = orders.merge(customers[['customer_id', 'segment_label']], on='customer_id')

# Group by month (using month_num for sorting) and segment_label
monthly_segment_orders = monthly_segment_orders.groupby(['month_num', 'month', 'segment_label']).size().reset_index(name='count')

# Visualize monthly trends by customer segment
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_segment_orders.sort_values('month_num'), x='month', y='count', hue='segment_label', marker='o')
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.title("Monthly Order Trends by Customer Segment")
plt.show()