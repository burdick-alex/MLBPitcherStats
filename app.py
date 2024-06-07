from flask import Flask, render_template, request
# # from pybaseball import playerid_lookup, statcast_pitcher
from pybaseball import  playerid_lookup
from pybaseball import  statcast_pitcher
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # The user has entered a name and submitted the form
        player_name = request.form['name']
        player_id, found_player_name = get_player_id(player_name)
        pitch_data = get_pitch_data(player_id)
        print( pitch_data.columns)
        chart = generate_chart(pitch_data)
        return render_template('home.html', chart=chart, player_name=found_player_name)
    else:
        # The user is visiting the page for the first time
        return render_template('home.html')

def get_player_id(name):
    # Use pybaseball to get the player's ID from their name
    first, last = name.lower().split(' ')
    player = playerid_lookup(last, first,fuzzy=True).iloc[0]
    found_player_name = f"{player['name_first']} {player['name_last']}"
    return player['key_mlbam'], found_player_name

def get_pitch_data(player_id):
    # Use pybaseball to get the player's pitch data
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    return statcast_pitcher(f'{str(current_year - 3)}-01-01', f'{current_year}-{current_month}-{current_day}', player_id)

def generate_chart(pitch_data):
    # Check if pitch_data is a pandas DataFrame
    # if isinstance(pitch_data, pd.DataFrame):
    # pitch_data = pitch_data.groupby("pitch_type").release_speed.agg("mean")

    fig, axs = plt.subplots(4,2, )
    fig.set_figheight(20)
    fig.set_figwidth(30)
    

    pitch_list = pitch_data[
        (pitch_data['balls'] == 0) & 
        (pitch_data['strikes'] == 0) &
        (pitch_data['stand'] == 'R')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0, ax= axs[0,1]).set_title('First Pitch % to Righty')

    pitch_list = pitch_data[
        (pitch_data['balls'] == 0) & 
        (pitch_data['strikes'] == 0) &
        (pitch_data['stand'] == 'L')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0, ax=axs[0,0]).set_title('First Pitch % to Lefty')

    pitch_list = pitch_data[
        (pitch_data['strikes'] == 2) &
        (pitch_data['stand'] == 'L')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[1,0]).set_title('2 Strikes Pitch % to Lefty')

    pitch_list = pitch_data[
        (pitch_data['strikes'] == 2) &
        (pitch_data['stand'] == 'R')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[1,1]).set_title('2 Strikes Pitch % to Righty')

    pitch_list = pitch_data[
        (pitch_data['stand'] == 'L')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[2,0]).set_title('Pitch % Overall Lefty')

    pitch_list = pitch_data[
        (pitch_data['stand'] == 'R')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[2,1]).set_title('Pitch % Overall, Righty')

    pitch_list = pitch_data[
        (pitch_data['balls'] > 1) & 
        (pitch_data['strikes'] <= 1) &
        (pitch_data['stand'] == 'L')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[3,0]).set_title('Need a Strike Pitch % Overall Lefty')

    pitch_list = pitch_data[
        (pitch_data['balls'] > 1) & 
        (pitch_data['strikes'] <= 1) &
        (pitch_data['stand'] == 'R')
    ]['pitch_name']
    cnts = pitch_list.value_counts() 
    cnts = cnts / cnts.sum()
    cnts.plot.bar(rot=0,ax=axs[3,1]).set_title('Need a Strike Pitch % Overall, Righty')

    # ax.bar(range(len(pitch_data)), pitch_data, tick_label=list(pitch_data.keys()))
    io_buf = io.BytesIO()
    plt.savefig(io_buf, format='png')
    io_buf.seek(0)
    return base64.b64encode(io_buf.read()).decode()

if __name__ == '__main__':
    app.run(debug=True, template_folder='templates')