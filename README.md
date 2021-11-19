# Uber Pedestrian App Hosted on Heroku
The rationale behind this anaylsis is derived from my interest in learning new plotting techniques and wanting to tackle an intereactive plotly dash application. 
The core idea is how can i create a travel routing application that can be used to analyse statistical aspects of selected routes. 
Additionally, in light of covid and the numerous Melbourne lockdowns, I wanted to analyse pedestrian counts around the City of Melbourne so as to contrast city pedestrian density against that of 2020 and 2021.
___
**Plot Descriptions**
Dash: The plots below are all contained within a plotly interactive dash application using css and html to create, style and display various interactive features such as drop downs radioitems and sliders.

1. RadioItem: The uber/pedestuan radioitem allows the user to select which dataset they wish to plot. Notably, our dropdowns and sliders all update according to which dataset is selected.

1.	Graph-Type RadioItem: The Bar/Box and Heatmap/Covid-Bar radioitem allows the user to select which type of graph they wish to plot. Notably, the covid-bar is only applicable to the Pedestrian dataset.

1.	Source Dropdown: The source dropdown contains all the source locations for our uber movement data sorted according to their suburb. Additionally, this dropdown is all used as the source location of our sensors which are sorted alphabetically.

1.	Destination Dropdown: The destination dropdown contains all the destination locations for our uber movement data that corresponds to our filterted source search. If we select a specific source we only want to display their corresponding destinations as we do not want to allow a user to select a destination if that data does not exist. This requires the updating of our destination dropdown according to the available data. Additionally, we have sorted our destination dropdown by suburb. Notably, this alos serves as our Year selection for our pedestrian dataset so we can filter on specific years we wish to be graphed.

1.	Month Slider: The slider at the bottom of our plots controls the selection of specific months that we want plotted. Notably we have set first set our slider parameters and then ensure that they update according to the available data. If our specific location only consits of data for three months we only want to display these three months and ensure they are sorted.

1.	Weekday Dropdown: The weekday dropdown contains all the weekdays available for our selected source and destination pairs. We have ensured that only the weekdays that correspond to the available filterted data can be displayed and sorted the dropdown by weekday.

Plots: We have selected to display 6 different types of graphs. Importanlty, each graph can be filtered in numerous ways according to our dropdowns, slider and radioitems. Additionally, plot hover text acts as our legends in most cases

1.	Scattermapbox Uber: Similar to a chloropleth map, this graph is essentially a line graph plotting the Linestring data of the filtered dataset from soruce (green dot) to destination (red dot). Notably, the dataset can be filtered by: source, destination, month and weekday. The hovertemplate displays four variables which ustilise the mean, min, max and std functions on our mean travel time and standard deviation travel times columns displayed in minutes.

1.	Scattermapbox Pedestrian: Similar to a chloropleth map, this graph is essentially a scatterplot plotting the hourly count data from the filtered dataset according to source. Since we have filtered our datset by source we only see one dot at a time instead of all the scaterpoints. Notably, the dataset can be filtered by: source, Year, month and weekday. The hovertemplate displays four variables which ustilise the count, mean, min, max functions on our hourly count column displayed.

1.	Bar and Box: Our Top right graph allows the user to select either a Bar or Boxplot. Additionally, the user is able to filter the dataset according to which dataset they have selected. Notably, our Uber barplot is a stacked barplot showing both mean travel time and standard deviation travel time binned by hours. Selecting the boxplot allows the user to plot the distribution of our filtered data showing descriptive statistics associated with box plots. Notably, these plots change if you decide to flip trhough months and days of week for that unique source and destination. Our pedestiran dataset displays a barplot of hourly counts by hour and we can similarly flip through different years, months and days of week for that unique source and watch the graph change accordingly. Similarly a boxplot is available for this dataset.

2.	Heatmap and Covid-Bar: Our Bottom right graph allows the user to select either a Heatmap or facet barplot. Additionally, the user is able to filter the dataset according to which dataset they have selected. Notably, our Uber Heatmap displays Time of day and weekday coloured by mean travel time allowing us to display on which days and at which times mean travel time is the highest. Additionaly, filters apply. Notably, the covid bar is only availalbe for the pedestrians dataset. The pedestrian dataset can be plotted as a covid barplot allowing us to contrast 2020 and 2021 pedestrian hourly count for weekdays to other years for that source. Additionally, we can plot a similar heatmap for the pedestrian dataset a displaying on which days at at which times pedestiran counts are the highest and lowest.
___
# Heroku Link:

https://melbournerouting.herokuapp.com/
