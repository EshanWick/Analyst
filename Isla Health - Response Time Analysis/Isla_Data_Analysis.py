import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Load datasets from Excel files
patient_entries_df = pd.read_excel(r'C:\Users\eshan\Documents\Serious\Patient_Entries.xlsx')
audit_actions_df = pd.read_excel(r'C:\Users\eshan\Documents\Serious\Audit_Actions.xlsx')

# Convert date columns to datetime format
patient_entries_df['createdAt_time'] = pd.to_datetime(patient_entries_df['createdAt_time'], errors='coerce')
audit_actions_df['timeResponded'] = pd.to_datetime(audit_actions_df['timeResponded'], errors='coerce')

#print(patient_entries_df.isnull().sum())
#print(audit_actions_df.isnull().sum())

# Remove rows with missing critical entries
patient_entries_df = patient_entries_df.dropna(subset=['createdAt_time'])
audit_actions_df = audit_actions_df.dropna(subset=['patientId', 'timeResponded'])

### Remove near-duplicate entries based on time (within the same submission window)

# Sort by patientId and createdAt_time
patient_entries_df = patient_entries_df.sort_values(by=['patientId', 'createdAt_time'])

# Deduplicate entries that occur within a short time window per patient
# Here, we're grouping by patientId and checking time differences between consecutive entries
patient_entries_df['time_diff'] = patient_entries_df.groupby('patientId')['createdAt_time'].diff()

# Define a time threshold
threshold = pd.Timedelta(minutes=3)

# Keep only the first entry for each group of near-duplicates (entries within the same time window)
cleaned_patient_entries = patient_entries_df[(patient_entries_df['time_diff'].isna()) | (patient_entries_df['time_diff'] > threshold)].copy()

# Drop the time_diff column as it's no longer needed
cleaned_patient_entries = cleaned_patient_entries.drop(columns=['time_diff'])

### Merge the cleaned patient entries with audit actions

# Perform a merge based on 'patientId'
merged_df = pd.merge(cleaned_patient_entries, audit_actions_df, on='patientId', how='left')

# Ensure only valid responses (where timeResponded is after createdAt_time)
merged_df = merged_df[merged_df['timeResponded'] >= merged_df['createdAt_time']]

# Calculate the response time in days
merged_df['Response_time'] = (merged_df['timeResponded'] - merged_df['createdAt_time']) / pd.Timedelta(days=1)

# Sort by patientId, entryId, and Response_time to get the earliest valid response
merged_df = merged_df.sort_values(by=['patientId', 'entryId', 'Response_time'])

# Drop duplicates based on entryId to keep only the closest response per entry
closest_responses = merged_df.drop_duplicates(subset=['entryId'], keep='first')

# Calculate the total number of closest valid responses
total_valid_responses = len(closest_responses)

#print(f"Total number of closest valid responses: {total_valid_responses}")
#print(closest_responses.head())

###### ANALYSIS

### Bar Graph Team Response Times

bardf = closest_responses.groupby('team name')['Response_time'].mean().reset_index()
bardf = bardf.sort_values(by= 'Response_time')
#print(bardf)
plt.figure(1,figsize=(10,6))
ax = sns.barplot(x='team name',
            y= 'Response_time',
            hue = 'team name',palette='dark:orange',
            data = bardf)
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2,      # X-coordinate: center of the bar
            p.get_height() + 0.7,              # Y-coordinate: slightly above the top of the bar
            f'{p.get_height():.2f}',            # The value (height) of the bar
            ha="center")                        # Horizontally center the text
plt.title('Average Response Time by Team (in Days)')
plt.xlabel('Team Name')
plt.ylabel('Average Response Time (Days)')
plt.xticks(rotation=45)


##### Same graph but only data from a year ago

filtered_responses = closest_responses[closest_responses['createdAt_time'] >= '2013-06-01']
bardf_filtered = filtered_responses.groupby('team name')['Response_time'].mean().reset_index()
bardf_filtered = bardf_filtered.sort_values(by='Response_time')
plt.figure(5,figsize=(10, 6))
ax = sns.barplot(x='team name',
                 y='Response_time',
                 hue='team name', 
                 palette='dark:orange',
                 data=bardf_filtered)
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2,
            p.get_height() + 0.7,              
            f'{p.get_height():.2f}', 
            ha="center")
plt.title('Average Response Time by Team (in Days) - From June 2013')
plt.xlabel('Team Name')
plt.ylabel('Average Response Time (Days)')
plt.xticks(rotation=45)

#### Histogram distribution of response times

plt.figure(2,figsize=(10,6))
sns.histplot(closest_responses['Response_time'], bins=1000, kde=False, color='orange')
plt.xscale('log')  # Logarithmic scale for skewed data
# Add labels and title
plt.title('Distribution of Response Times (in Days)')
plt.xlabel('Response Time (Days)')
plt.ylabel('Frequency')

response_df = closest_responses.copy()


###### Days of the week response time

response_df['day_of_week'] = response_df['createdAt_time'].dt.day_name()
response_time_by_day = response_df.groupby('day_of_week')['Response_time'].mean().reset_index()
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
response_time_by_day['day_of_week'] = pd.Categorical(response_time_by_day['day_of_week'], categories=days_order, ordered=True)
response_time_by_day = response_time_by_day.sort_values('day_of_week')

plt.figure(3,figsize=(10,6))
ax1 = sns.barplot(x='day_of_week',
            y= 'Response_time',
            hue = 'day_of_week',palette='dark:orange',
            data = response_time_by_day)
for p in ax1.patches:
    ax1.text(p.get_x() + p.get_width() / 2,      # X-coordinate: center of the bar
            p.get_height() + 0.05,              # Y-coordinate: slightly above the top of the bar
            f'{p.get_height():.2f}',            # The value (height) of the bar
            ha="center") 
#sns.barplot(data=response_time_by_day, x='day_of_week', y='Response_time', hue = 'day_of_week',palette='dark:orange')
plt.title('Average Response Time by Day of the Week')
plt.xlabel('Day of the Week')
plt.ylabel('Average Response Time (Days)')



#### Lineplot Response time over time

response_df['year_month'] = response_df['createdAt_time'].dt.to_period('M')
response_time_by_month = response_df.groupby('year_month')['Response_time'].mean().reset_index()
response_time_by_month['year_month'] = response_time_by_month['year_month'].astype(str)
plt.figure(4,figsize=(10,6))
sns.lineplot(data=response_time_by_month, x='year_month', y='Response_time', marker='o', color = 'orange')
plt.title('Average Response Time Trends Over Time (Monthly)')
plt.xlabel('Month-Year')
plt.ylabel('Average Response Time (Days)')
plt.xticks(rotation=45)





######   Key Metrics

average_response_time = closest_responses['Response_time'].mean()
median_response_time = closest_responses['Response_time'].median()
max_response_time = closest_responses['Response_time'].max()
min_response_time = closest_responses['Response_time'].min()

# Define a threshold for outliers (e.g., responses longer than 30 days)
outliers = closest_responses[closest_responses['Response_time'] > 30]
outlier_count = len(outliers)

print(f"Average Response Time: {average_response_time:.2f} days")
print(f"Median Response Time: {median_response_time:.2f} days")
print(f"Max Response Time: {max_response_time:.2f} days")
print(f"Min Response Time: {min_response_time:.2f} days")
print(f"Number of Outliers (>30 days): {outlier_count}")
# total_submissions = len(closest_responses)
# total_responses = closest_responses['Response_time'].notna().sum()
# # print(f"Total number of submissions: {total_submissions}")
# # print(f"Total number of responses: {total_responses}")

##### For after May

average_response_time2 = filtered_responses['Response_time'].mean()
median_response_time2 = filtered_responses['Response_time'].median()
max_response_time2 = filtered_responses['Response_time'].max()
min_response_time2 = filtered_responses['Response_time'].min()

# Define a threshold for outliers (e.g., responses longer than 30 days)
outliers2 = filtered_responses[filtered_responses['Response_time'] > 30]
outlier_count2 = len(outliers2)

print(f"Average Response Time: {average_response_time2:.2f} days")
print(f"Median Response Time: {median_response_time2:.2f} days")
print(f"Max Response Time: {max_response_time2:.2f} days")
print(f"Min Response Time: {min_response_time2:.2f} days")
print(f"Number of Outliers (>30 days): {outlier_count2}")


# ### Resubmissions
submission_counts = closest_responses.groupby('patientId')['entryId'].nunique().reset_index(name='submission_count')
# Step 2: Sort by submission count to identify the most frequent submitters
submission_counts = submission_counts.sort_values(by='submission_count', ascending=False)
bins = [0, 5, 10, 20, 50, 100]
labels = ['1-5', '6-10', '11-20', '21-50', '51-100']
submission_counts['submission_group'] = pd.cut(submission_counts['submission_count'], bins=bins, labels=labels)
#submission_grouped_table = submission_counts[['patientId', 'submission_count', 'submission_group']]
submission_group_summary = submission_counts['submission_group'].value_counts().sort_index()
print("\nSummary of Patients Grouped by Submission Frequency:")
print(submission_group_summary)



# # Exporting key metrics to an Excel file
# with pd.ExcelWriter('Isla_Health_Report_Data.xlsx', engine='xlsxwriter') as writer:
#     # Exporting the patient submission bins
#     submission_counts.to_excel(writer, sheet_name='Patient_Submission_Bins', index=False)
    
#     # Exporting the closest responses for review
#     closest_responses.to_excel(writer, sheet_name='Closest_Responses', index=False)

#     # Exporting the outlier data (responses > 30 days)
#     outliers.to_excel(writer, sheet_name='Outliers', index=False)
# Export to Excel or CSV for accessibility
#submission_grouped_table.to_excel('patient_submission_bins2.xlsx', index=False)

plt.show()