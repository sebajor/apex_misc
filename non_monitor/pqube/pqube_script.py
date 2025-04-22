####!/alma/ACS-2021JUN/pyenv/versions/3.6.9/bin/python3
####!/alma/ACS-2021DEC/pyenv/versions/3.8.6/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
#import ipdb
import ftplib
import argparse
import sys, os


###
### The pqube is a power network recorder, it saves currents, voltage, power, etc from a
### triphasic system. The APEX pqube is connected to the power house in chajnantor.
### The pqube every day generates a daily report, this code allows you to get the data
###  and also to plot some curves.
###

data_folder = "pqube_data"
plot_folder = "pqube_plots"

parser = argparse.ArgumentParser(
    description="Script to plot and to get the data from the pqube.")

parser.add_argument("-g", "--get", dest="get_file", type=str, default=None,
    help="Flag to get the data from the ftp server, you must supply the date of the \
            file that you want to obtain in Y/M/D format")

parser.add_argument("-f", "--filenames", dest="filenames", nargs="*",
    help="filenames to plot")


##
## The pqube is configured to have the ip 10.0.6.110 and to have a http server 
## running. You can download the data from there. There is also a ftp server 
## runing in port 21 for control and the data transfer occurs in the port 22.
##

def plot_single_file(filename, axes_plot=[[16,15,17], [166,172], [53,54,55]], plot=True,
                     save_plot=None):
    #ax0 = [16,15,17]
    #ax1 = [106,109,112]	##this are the lines measurements
    #ax2 = [166,172]
    #ax3 = [53,54,55]
    #axes_plots = [ax0,ax1,ax2, ax3]
    df = pd.read_csv(filename, sep=',', skiprows=10)
    keys = list(df.keys())
    stamp = [datetime.datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in df[keys[0]]]
    fig, axes = plt.subplots(len(axes_plots), sharex=True)
    for i,ax in enumerate(axes.flatten()):
        for item in axes_plots[i]:
            ax.plot(stamp, df[keys[item]], label=keys[item])
        ax.grid()
        ax.legend()
    fig.set_tight_layout(True)
    plt.show()
    return fig, axes


def plot_multiple_files(filenames,axes_plot=[[16,15,17], [166,172], [53,54,55]], plot=True,
                        plot_folder="pqube_plots", show=True):
                        #axes_plot=[[16,15,17], [106,109,112], [166,172], [53,54,55]]):
    """
    filenames: list with the files names
    axes_plot: list that contain list with the indices of the pqube data that you want to plot. 
              Each list represent an axis where to plot
    """
    stamps = []
    data = []
    for i in range(len(axes_plot)):
        data.append(np.empty((0,len(axes_plot[i]))))

    for fil in filenames:
        df = pd.read_csv(fil, sep=',', skiprows=10)
        keys = list(df.keys())
        stamp = [datetime.datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in df[keys[0]]]
        stamps += stamp
        for i, indices in enumerate(axes_plot):
            key_names = [keys[x] for x in indices]
            data[i] = np.concatenate((data[i],np.array(df[key_names])))
    if(plot):
        fig, axes = plt.subplots(len(axes_plot), sharex=True, figsize=(17,13))
        for i, dat in enumerate(data):
            for j, values in enumerate(dat.T):
                axes[i].plot(stamps, values, label=keys[axes_plot[i][j]])
            axes[i].axhline(np.max(dat), ls='--', label='max %.2f'%np.max(dat), color='black')
            axes[i].axhline(np.min(dat), ls='--', label='min %.2f'%np.min(dat), color='red')
            axes[i].grid()
            axes[i].legend()
        axes[0].set_ylabel("A")
        axes[1].set_ylabel("kW")
        #axes[2].set_ylabel("Hz")
        axes[2].set_ylabel("V")
        fig.set_tight_layout(True)
        name = os.path.basename(filenames[0]).split(' ')[0]   #here I assume the Y/M/d Trends.csv name
        fig.savefig(os.path.join(plot_folder, name),dpi=100)
        if(show):
            plt.show()
        plt.close()
    return data


def get_pqube_ftp_data(date, filename=None, host='10.0.6.110', user='admin', passwd='admin',
                       data_folder="pqube_data"):
    """
    date should be in the format Year/month/day
    The ftp server sucks so it takes a while to transfer the file
    """
    date = datetime.datetime.strptime(date, '%Y/%m/%d')
    msg = date.strftime("%Y")+"/Month "+date.strftime("%m")+"/Day "+date.strftime("%d") +"/"+ \
          date.strftime("%Y-%m-%d")+" Trends-Stats/Spreadsheets/"+date.strftime("%Y-%m-%d")+ \
          " Trends.csv"
    print("Getting:")
    print(msg)
    if(filename is None):
        filename = date.strftime("%Y-%m-%d")+" Trends.csv"
        filename = os.path.join(data_folder, filename)
    ftp_client = ftplib.FTP(host, user, passwd)
    with open(filename, 'wb') as file:
        ftp_client.retrbinary('RETR '+msg, file.write)
    ftp_client.quit()


if __name__ == '__main__':
    ##create the folder if they dont exist
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(plot_folder, exist_ok=True)

    args = parser.parse_args()
    if(args.get_file is not None):
        print("This is super slow!")
        get_pqube_ftp_data(args.get_file, data_folder=data_folder)
        print("Got the file")
        sys.exit()
    ##now we plot the data
    #plot_multiple_files(args.filenames, plot_folder=plot_folder)
    #plot_multiple_files(args.filenames, plot_folder=plot_folder,axes_plot=[[106,109,112], [166,172], [53,54,55]] )

    plot_multiple_files(args.filenames, plot_folder=plot_folder,axes_plot=[[106,109,112], [166,172], [87,90,93]] )
