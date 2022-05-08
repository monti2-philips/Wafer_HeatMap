import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import gridspec
import seaborn as sns
import numpy as np

class Plotter_Tx():
    def __init__(self,df_amb,df_hot,location,asic_list,sfc):
        self.df_amb = df_amb
        self.df_hot = df_hot
        self.location = location
        self.asic_list = asic_list
        self.sfc = sfc

    def row_conv(self,row):
        old = list(range(1,10,1))
        new = list(range(9,0,-1))
        row_dict = dict(zip(old, new))
        new_row = row_dict[row]
        return new_row

    def plot_wafers(self):
        
        amb_keys = list(self.df_amb.keys())
        hot_keys = list(self.df_hot.keys())
        amb_key = amb_keys[-1]
        hot_key = hot_keys[-1]
        print(f'Ambient Key: {amb_key}')
        print(f'Hot Key: {hot_key}')

        size = tuple(np.array((24,15))*0.75) # for rotated
        fig = plt.figure(figsize=size,dpi=300,constrained_layout=True)
        title = f'{self.sfc} - {amb_key} - Ambient vs Hot Wafer HeatMaps'
        fig.suptitle(title,fontsize='xx-large')
        subfigs = fig.subfigures(ncols=2,nrows=1,edgecolor='black',linewidth=1.0,frameon=True)
        subfig1 = subfigs[0]
        subfig2 = subfigs[1]
        subfig1.suptitle('Ambient',fontsize='x-large')
        subfig2.suptitle('Hot',fontsize='x-large')
        
        spec1 = gridspec.GridSpec(ncols=13, nrows=9,
                            wspace=0.025, hspace=0.025,
                            figure=subfig1)
        spec2 = gridspec.GridSpec(ncols=13, nrows=9,
                            wspace=0.025, hspace=0.025,
                            figure=subfig2)

        for row in range(1,10):
            for col in range(1,14):
                if f'{row:03.0f}_{col:03.0f}' in self.asic_list:
                    
                    ax1 = subfig1.add_subplot(spec1[self.row_conv(row)-1,col-1])
                    ax2 = subfig2.add_subplot(spec2[self.row_conv(row)-1,col-1])
                                
                    amb_temp = self.df_amb[amb_key]
                    amb_temp.set_index(amb_temp.loc[:,'ProductSN'].str.slice(-7),inplace=True)
                    amb_temp.sort_index(inplace=True)
                    
                    hot_temp = self.df_hot[hot_key]
                    hot_temp.set_index(hot_temp.loc[:,'ProductSN'].str.slice(-7),inplace=True)
                    hot_temp.sort_index(inplace=True)
            
                    asic = f'{row:03.0f}_{col:03.0f}'
                    amb_array = amb_temp.iloc[amb_temp.index.get_loc(asic),amb_temp.columns.get_loc('Tx Element[0]'):].to_numpy()
                    hot_array = hot_temp.iloc[hot_temp.index.get_loc(asic),hot_temp.columns.get_loc('Tx Element[0]'):].to_numpy()
                    
                    #### Creation of Matrix representing R=40, C=75 ASIC
                    
                    amb_elements = np.reshape(amb_array,[40,75])
                    hot_elements = np.reshape(hot_array,[40,75])
                    
                    avg_amb = amb_elements.mean()
                    norm_amb_elements = amb_elements/avg_amb
                    norm_amb_elements = np.rot90(norm_amb_elements)
                    
                    avg_hot = hot_elements.mean()
                    norm_hot_elements = hot_elements/avg_hot
                    norm_hot_elements = np.rot90(norm_hot_elements)
                    
                    newcmp = colors.LinearSegmentedColormap.from_list("mycmap", ['#000000','#B9B9B9','#FFFFFF'])\
                        .with_extremes(over='red', under='blue')
                        # .with_extremes(over='#ff0000', under='#91fbfe')
                    
                    sns.heatmap(norm_amb_elements.astype(np.float64),
                                ax=ax1,
                                square=True,
                                cmap=newcmp,
                                vmin=0.75,
                                vmax=1.25,
                                cbar=False)
                    
                    sns.heatmap(norm_hot_elements.astype(np.float64),
                                ax=ax2,
                                square=True,
                                cmap=newcmp,
                                vmin=0.75,
                                vmax=1.25,
                                cbar=False)
            
                    ax1.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    ax2.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    print(f'{row}:{col} added')
                else:
                    ax1 = subfig1.add_subplot(spec1[self.row_conv(row)-1,col-1],frame_on=False)
                    ax1.annotate(f'{row}:{col}',xy=(0.5, 0.5), xycoords='axes fraction',
                        va='center', ha='center')
                    
                    ax2 = subfig2.add_subplot(spec2[self.row_conv(row)-1,col-1],frame_on=False)
                    ax2.annotate(f'{row}:{col}',xy=(0.5, 0.5), xycoords='axes fraction',
                        va='center', ha='center')
                    
                    ax1.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    ax2.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                
        plot_path = self.location
        fig.savefig(plot_path+r'\\'+f'{self.sfc} - {amb_key}',
                    dpi=300,
                    bbox_inches='tight')
        plt.close(fig)

class Plotter_Rx():
    def __init__(self,df_hot,location,asic_list,sfc):
        self.df_hot = df_hot
        self.location = location
        self.asic_list = asic_list
        self.sfc = sfc

    def row_conv(self,row):
        old = list(range(1,10,1))
        new = list(range(9,0,-1))
        row_dict = dict(zip(old, new))
        new_row = row_dict[row]
        return new_row

    def plot_wafers(self):
        
        hot_keys = list(self.df_hot.keys())
        hot_key = hot_keys[-1]
        print(f'Hot Key: {hot_key}')

        size = tuple(np.array((24,15))*0.75) # for rotated
        fig = plt.figure(figsize=size,dpi=300,constrained_layout=True)
        title = f'{self.sfc} - {hot_key} - Ambient vs Hot Wafer HeatMaps'
        fig.suptitle(title,fontsize='xx-large')
        subfigs = fig.subfigures(ncols=2,nrows=1,edgecolor='black',linewidth=1.0,frameon=True)
        subfig1 = subfigs[0]
        subfig2 = subfigs[1]
        subfig1.suptitle('Ambient No Longer Performs Rx Tests',fontsize='x-large')
        subfig2.suptitle('Hot',fontsize='x-large')
        
        spec1 = gridspec.GridSpec(ncols=13, nrows=9,
                            wspace=0.025, hspace=0.025,
                            figure=subfig1)
        spec2 = gridspec.GridSpec(ncols=13, nrows=9,
                            wspace=0.025, hspace=0.025,
                            figure=subfig2)

        for row in range(1,10):
            for col in range(1,14):
                if f'{row:03.0f}_{col:03.0f}' in self.asic_list:
                    
                    ax2 = subfig2.add_subplot(spec2[self.row_conv(row)-1,col-1])
                    
                    hot_temp = self.df_hot[hot_key]
                    hot_temp.set_index(hot_temp.loc[:,'ProductSN'].str.slice(-7),inplace=True)
                    hot_temp.sort_index(inplace=True)
            
                    asic = f'{row:03.0f}_{col:03.0f}'
                    hot_array = hot_temp.iloc[hot_temp.index.get_loc(asic),hot_temp.columns.get_loc('Rx Element[0]'):].to_numpy()
                    
                    #### Creation of Matrix representing R=40, C=75 ASIC
                    
                    hot_elements = np.reshape(hot_array,[40,75])
                    
                    avg_hot = hot_elements.mean()
                    norm_hot_elements = hot_elements/avg_hot
                    norm_hot_elements = np.rot90(norm_hot_elements)
                    
                    newcmp = colors.LinearSegmentedColormap.from_list("mycmap", ['#000000','#B9B9B9','#FFFFFF'])\
                        .with_extremes(over='red', under='blue')
                        # .with_extremes(over='#ff0000', under='#91fbfe')
                    
                    sns.heatmap(norm_hot_elements.astype(np.float64),
                                ax=ax2,
                                square=True,
                                cmap=newcmp,
                                vmin=0.5,
                                vmax=1.5,
                                cbar=False)

                    ax1 = subfig1.add_subplot(spec1[self.row_conv(row)-1,col-1],frame_on=True)
                    ax1.annotate(f'{row}:{col}',xy=(0.5, 0.5), xycoords='axes fraction',
                        va='center', ha='center')

                    ax1.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    ax2.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    print(f'{row}:{col} added')
                else:
                    ax1 = subfig1.add_subplot(spec1[self.row_conv(row)-1,col-1],frame_on=False)
                    ax1.annotate(f'{row}:{col}',xy=(0.5, 0.5), xycoords='axes fraction',
                        va='center', ha='center')

                    ax2 = subfig2.add_subplot(spec2[self.row_conv(row)-1,col-1],frame_on=False)
                    ax2.annotate(f'{row}:{col}',xy=(0.5, 0.5), xycoords='axes fraction',
                        va='center', ha='center')

                    ax1.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                    ax2.tick_params(left = False, right = False , labelleft = False,
                                labelbottom = False, bottom = False)
                
        plot_path = self.location
        fig.savefig(plot_path+r'\\'+f'{self.sfc} - {hot_key}',
                    dpi=300,
                    bbox_inches='tight')
        plt.close(fig)

if __name__ == '__main__':
    pass