import pandas
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit
import numpy as np

def get_icon_url(passengers):
    try:
        passengers = int(passengers)
    except(ValueError, TypeError):
        passengers = 0

    low_demand_icon = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cpath%20fill%3D%22%23D7DCE1%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201m4.988%200-.002%206%202.496-.016c.55%200%201.004-.466%201.004-.984V9c0-1.134-.866-2-2-2h-.526c-.55%200-.972.45-.972%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205m4.968%200C14.337%205%2015%204.337%2015%203.484%2015%202.664%2014.337%202%2013.484%202%2012.664%202%2012%202.663%2012%203.484%2012%204.337%2012.663%205%2013.484%205%22%2F%3E%3Cpath%20fill%3D%22%23646973%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm3.016-8C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E"
    medium_demand_icon = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cpath%20fill%3D%22%23D7DCE1%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201m4.988%200-.002%206%202.496-.016c.55%200%201.004-.466%201.004-.984V9c0-1.134-.866-2-2-2h-.526c-.55%200-.972.45-.972%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205m4.968%200C14.337%205%2015%204.337%2015%203.484%2015%202.664%2014.337%202%2013.484%202%2012.664%202%2012%202.663%2012%203.484%2012%204.337%2012.663%205%2013.484%205%22%2F%3E%3Cpath%20fill%3D%22%23646973%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E"
    high_demand_icon = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%3E%3Cpath%20fill%3D%22%23FF7A00%22%20fill-rule%3D%22evenodd%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201m4.988%200-.002%206%202.496-.016c.55%200%201.004-.466%201.004-.984V9c0-1.134-.866-2-2-2h-.526c-.55%200-.972.45-.972%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205m4.968%200C14.337%205%2015%204.337%2015%203.484%2015%202.664%2014.337%202%2013.484%202%2012.664%202%2012%202.663%2012%203.484%2012%204.337%2012.663%205%2013.484%205%22%2F%3E%3C%2Fsvg%3E"

    if passengers < 5 :
        return "Low Demand Expected", low_demand_icon
        #return low_demand_icon
    elif 5 <= passengers < 10 :
        return "Medium Demand Expected", medium_demand_icon
        #return medium_demand_icon
    else:
        return "High Demand Expected", high_demand_icon
        #return high_demand_icon
    
def get_project_description():
    return """
    #### How VGI-Flexi users move.  

    - **Dynamic Demand Analysis**: Visualize the most popular bus stops, identifying areas of high demand at different times of the day.
    - **Dynamic Trip Analysis**: Track and analyze ridership patterns over time, helping to identify trends and fluctuations.
    - **Dynamic Revenue Analysis**: Explore the paths taken by buses, allowing for a deeper understanding of service coverage and efficiency.
    - **Report Generation**: Automatically generate comprehensive reports, summarizing the findings from the demand and route analysis for further insights and decision-making.

    Part of official VGI Hackathon 2024.
    """

def get_multibar_graph_data(dataset):
    col_1, col_2 = streamlit.columns([1, 1])
    with col_1:
        # Step 2: Group by both pickup_day and passenger_status to get the counts for valid and cancelled bookings
        status_counts = dataset.groupby(['pickup_day', 'passenger_status'])['booking_id'].count().unstack(fill_value=0)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # Define the order for the days of the week
        status_counts = status_counts.reindex(day_order)

        # Step 2: Plot the data as a multiline graph
        fig, ax = plt.subplots(figsize=(6, 4))
         
        # Plot lines for 'Cancelled' and 'Trip completed'
        status_counts['Cancelled'].plot(ax=ax, label='Cancelled', color='red', marker='o')
        status_counts['Trip completed'].plot(ax=ax, label='Trip completed', color='green', marker='o')

        # Adding labels and title
        ax.set_xlabel('Day of the Week')
        ax.set_ylabel('Count')
        ax.set_title('Bookings vs Cancellation')
        # ax.legend()

        # Step 3: Show plot in Streamlit
        streamlit.pyplot(fig)
    with col_2:
        pass
    
    return status_counts
