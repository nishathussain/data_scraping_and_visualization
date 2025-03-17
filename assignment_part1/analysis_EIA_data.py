#!/usr/bin/env python
import pandas, os, glob, datetime
import plotly.express as px
import plotly.graph_objects as go
BASE_DIR='./processed'
all_files= [file for file in glob.glob(BASE_DIR+'/202[3|4]/*/*', recursive=True) if os.path.isfile(file)] # 2023/4 files
actual_file ='./processed/2025/mar/mar2025_base.csv' # select latest file for Actuals

## actual data for the period 2023/2024
actual=pandas.read_csv(actual_file)
actual['ds']=pandas.to_datetime(actual['ds'])
actual=actual[(actual['forecast']==0) & (actual['ds'].dt.year.isin([2023,2024])) ].rename(columns={'values':'actual'})[['ds', 'actual']]
## load forecasts
forecast=pandas.DataFrame()
for file in all_files:
    day_of_forecast= datetime.datetime.strptime(os.path.basename(file).split('_')[0],'%b%Y')
    day_of_forecast= str(day_of_forecast.year)+'-'+str(day_of_forecast.month).zfill(2)+'-'+str(day_of_forecast.day).zfill(2)
    tmp=pandas.read_csv(file)
    tmp=tmp[tmp['forecast']==1]             # forecast data only
    tmp['date_of_forecast']=day_of_forecast # date on which forecast was done
    tmp.loc[:,'forecast_horizon'] = tmp['forecast'].expanding().sum()
    tmp.drop(columns=['forecast'],inplace=True)
    forecast=pandas.concat([forecast,tmp], axis=0)
forecast['ds']=pandas.to_datetime(forecast['ds'])
forecast['date_of_forecast']=pandas.to_datetime(forecast['date_of_forecast'])
forecast.rename(columns={'values':'forecast'},inplace=True)

var=forecast.groupby('forecast_horizon').var(numeric_only=True).reset_index().rename(columns={'forecast':'variance'})
var=var[var['forecast_horizon']<13] # max forecast horizon of 1 year

fig =px.line(var, x='forecast_horizon', y='variance',title='Forecast Variance over forecasted horizon')\
.update_layout(xaxis_title="Forecast Horizon (in Months)", yaxis_title="Supply Forecast Variance <br>(million barrels per day)")
fig.show()
fig.write_image('./plots/variance_forecast_horison.png')

# ### 2. Q: What was the monthly deviation for the production estimate for December 2024 (forecast vs. actual expected today) over 2023 and 2024?
# Solution: Line Plot of December 2024 Forecasts Over Time with Actual<br>
# X-axis → Forecast Month (Jan 2023 to Dec 2024)<br>
# Y-axis → Forecasted Value for Dec 2024<br>
# This shows how the forecast for December 2024 evolved each month.
tmp=forecast[(forecast['ds']=='2024-12-01')]
act_dec_2024=actual[actual['ds']=='2024-12-01']['actual'].values[0]
fig= go.Figure()
fig.update_layout(title='Plot of December 2024 Forecasts Over Time with Actual')
fig.add_trace(go.Scatter(x=tmp["date_of_forecast"], y=tmp['forecast'],mode='markers',name='Forecasted Dec 2024'))
fig.add_trace(go.Scatter(x=[tmp['date_of_forecast'].min(), tmp['date_of_forecast'].max()], y=[act_dec_2024, act_dec_2024],mode='lines', name='Actual Dec 2024'))
fig.update_layout(xaxis_title="date of forecast", yaxis_title="Forecasted Supply Value for Dec 2024 <br>(million barrels per day)")
fig.show()
fig.write_image('./plots/December_2024_forecast_overtime_with_actual.png')

# ### 3. Q: What are the range of deviations? (Dec 2024)
# Solution: Range of deviation for Dec 2024 forecast<br>
# Box Plot of Forecast Errors for All Months<br>
# X-axis → Forecast Horizon (1M, 2M, … 12M ahead)<br>
# Y-axis → Forecast Error (Actual - Forecast)<br>

tmp=forecast[(forecast['ds']=='2024-12-01')]
print("Range of deviation for dec 2024 forecast")
print('Min: ',tmp['forecast'].min())
print('Max: ',tmp['forecast'].max())
print('Mean: ',tmp['forecast'].mean())
print('Median: ',tmp['forecast'].median())
print('Actual: ',act_dec_2024)

# ### 4. Q What is the average monthly deviation?
# Assuming: the ask is to find average monthly deviation for one month horizon forecast Vs actual value.<br> 
# Solution: Mean error for the Next month prediction.

forecast= forecast[forecast['ds']<'2025-01-01']
tmp= forecast.merge(actual, how='left',on='ds')
tmp=tmp[tmp['forecast_horizon']<13]
tmp['deviation'] = tmp['actual'] - tmp['forecast']
tmp = tmp.groupby(['forecast_horizon'])['deviation'].mean().reset_index()

print("Average monthly Deviation:",tmp['deviation'].mean(),"(million barrels per day)" )

fig= px.scatter(tmp, x='forecast_horizon', y='deviation',title='Average monthly deviation for each forecasting horizon', height=400, width=800)
fig.update_layout(xaxis_title="Forecast Horizon (in Months)", yaxis_title=" Actual - Forecast <br>(million barrels per day)")
fig.show()
fig.write_image('./plots/average_monthly_deviation_for_each_forecast_horizon.png')

tmp= forecast.merge(actual, how='left',on='ds')
tmp=tmp[tmp['forecast_horizon']<13]
tmp['deviation'] = tmp['actual'] - tmp['forecast']

fig=px.box(tmp,x="forecast_horizon", y='deviation',title='Box plot deviation in monthly forecast')
fig.update_layout(xaxis_title='Forecast Horizon (in Months)',yaxis_title='Actual - Forecast <br>(million barrels per day)')
fig.show()
fig.write_image('./plots/boxplot_monthly_deviation_forecast_horizon.png')

# ### 5. Q Plot the various forecast iterations on a chart.
# Lets plot last two years of data each line represents start of forecast 

forecast= forecast[forecast['ds']<'2025-01-01']
tmp= forecast.merge(actual, how='left',on='ds')
tmp['date_of_forecast']=pandas.to_datetime(tmp['date_of_forecast'])
tmp['date_of_forecast']=tmp['date_of_forecast'].dt.strftime("%b %y")

print('Line plot of each forecasting iteration \n ---------------------------------------')
fig=px.line(tmp, x='ds', y='forecast',color='date_of_forecast',height=400,width=800)
fig.add_trace(go.Scatter(x=actual['ds'],y=actual['actual'],mode='lines',line_color='black', name='Actual Production'))
fig.update_layout(xaxis_title='Date',yaxis_title='US crude oil production <br>(million barrels per day)')
fig.update_layout(legend=dict(    orientation="h",    yanchor="bottom",
    y=1.02,    xanchor="right",    x=1 ))
fig.show()
fig.write_image('./plots/line_plot_of_each_forecasting_iteration.png')

df= pandas.pivot_table(forecast, values=['forecast'] ,index = ['date_of_forecast'], columns=['ds']) 
df.index = df.index.strftime('%b %y') # Change index format
temp_col=list(df.columns)             # Change column date format
for ii in range(len(temp_col)):
    temp_col[ii]=(temp_col[ii][0],temp_col[ii][1].strftime("%b %y"))
df.columns= pandas.MultiIndex.from_tuples(temp_col, names=[None, 'ds'])
df.to_csv('./summary_table.csv')
df.head(10)

