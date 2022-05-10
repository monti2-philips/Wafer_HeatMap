import glob
import os
import sys
import shutil
import time
from datetime import datetime

import lxml.etree as ET
import pandas as pd


class Parser():
    def __init__(self, location, asic_list, sfc):
        self.location = location
        self.asic_list = asic_list
        self.sfc = sfc

    def process_data(self):
        '''
        Function used to:
            1) Call Main 'Process_Data' Function to begin data analysis
            2) Writes DataCon text to DataCon Group TextBrowser

        Parameters
        ----------
        location : Path
            Input Directory to find Test Data XML files
        asic_list : List
            List of ASIC from configuration file
        sfc : String
            SFC - 6 characters

        Returns
        -------
        df_amb : DataFrame
            DataFrame of Baseline Results
        df_hot : DataFrame
            DataFrame of Elevated Results

        '''
        start_start = time.time()
        self.check_sfc()

        start_time = time.time()
        # Collect Files at Input Directory
        file_list = self.collect_files(self.location, self.sfc)
        print('File Collection took {0:.0f} seconds.'.format(
            time.time() - start_time))

        start_time = time.time()
        # Sort Files into Elevated and Baseline Lists
        list_amb, list_hot = self.sort_files(file_list)
        print('File Sort took {0:.0f} seconds.'.format(
            time.time() - start_time))
        print(f'Found {len(list_amb)} Baseline Test Data files.')
        print(f'Found {len(list_hot)} Elevated Test Data files.')

        # Check Dataset --> Do all  ASIC (that are used) datasets exist for both elevated and baseline?
        data_check, list_amb, list_hot, asic_list_len, count_in_amb, count_in_hot = self.check_dataset(self.asic_list,
                                                                                                       list_amb, list_hot)
        if data_check == False:
            print(f'Results were not found for {asic_list_len} ASICs of Baseline and Elevated Tests.\
                    \nBaseline Files: {count_in_amb}\
                    \nElevated Files: {count_in_hot}\
                    \nPlease contact Engineering for support.')
            sys.exit(1)

        print(
            f'Found {len(list_amb)} Baseline Test Data files that match ASIC List.')
        print(
            f'Found {len(list_hot)} Elevated Test Data files that match ASIC List.')

        # Checks for Temp Folder
        path = self.check_temp_folder()

        start_time = time.time()
        # Copies files in Amb and Elevated Lists to Temp Folder on Hard Drive
        self.copy_files(list_amb, path, 'Baseline')
        self.copy_files(list_hot, path, 'Elevated')
        print('File Copy took {0:.0f} seconds.'.format(
            time.time() - start_time))

        # Collects file paths for Temp Folder Files and resorts int Amb and Elevated Lists
        list_amb, list_hot = self.collect_copy_files(path)

        start_time = time.time()
        # Creates List of Tests
        test_list_tx = self.create_test_list('Tx')
        test_list_rx = self.create_test_list('Rx')
        # Parses XML files on hard drive to create dictionary entries for each test
        df_amb = self.create_data_dict(
            list_amb, test_list_tx, 'Baseline', 'Tx')
        df_hot = self.create_data_dict(
            list_hot, test_list_tx, 'Elevated', 'Tx')
        df_rx = self.create_data_dict(list_hot, test_list_rx, 'Elevated', 'Rx')
        self.keys_match(df_amb, df_hot)
        print('Data Parsing took {0:.0f} seconds.'.format(
            time.time() - start_time))

        start_time = time.time()
        # Deletes Temp Folder and all files within
        self.delete_files(path)
        print('Deleting Files took {0:.0f} seconds.'.format(
            time.time() - start_time))

        end_end = time.time()
        duration = end_end-start_start
        print('Total Time: {0:.0f} minutes and {1:.0f} seconds'.format(
            duration//60, duration % 60))

        return df_amb, df_hot, df_rx

    def check_sfc(self):
        file_list = self.collect_files(self.location, self.sfc)
        bases = [os.path.basename(x).split('-')[0].split('_')[0]
                 for x in file_list]
        sfcs = list(set(bases))
        sfcs = [x[:6] for x in sfcs]
        sfcs = list(set(sfcs))

        if len(sfcs) < 1:
            print('No SFC matching that value')
            sys.exit(1)
        return

    def collect_files(self, location, sfc):
        '''
        Gather files that match SFC and Die Tests in location provided location and all sub-folders of location.
        Return list of file paths.

        Parameters
        ----------
        location : Path
            Input Directory
        sfc : String
            SFC of Wafer that is input by operator

        Returns
        -------
        file_list : List of Paths
            File List of Elevated and Baseline XML files

        '''
        sfc = sfc.strip().upper()
        path = location + '\\**\\' + sfc + '*' + 'Die Test Baseline' + '*' + '.xml'
        file_list_amb = glob.glob(path, recursive=True)
        path = location + '\\**\\' + sfc + '*' + 'Die Test Elevated' + '*' + '.xml'
        file_list_hot = glob.glob(path, recursive=True)
        file_list = file_list_amb + file_list_hot

        # Remove files that have "Aborted" in name
        file_list = [x for x in file_list if "ABORTED" not in x.upper()]

        return file_list

    def sort_files(self, file_list):
        '''
        Sorts Files based on Date/Time and presence of "Die Test Baseline" and "Die Test Elevated" markers in file name.

        Parameters
        ----------
        file_list : List of Paths

        Returns
        -------
        list_amb : List of Paths
            File List of Baseline Test Results (XML)
        list_hot : List of Paths
            File List of Elevated Test Results (XML)

        '''
        file_paths = [os.path.abspath(x) for x in file_list]
        split_list = [os.path.split(x)[-1] for x in file_list]
        sfc_probe = ['-'.join(x.split('-')[0:2]).upper() for x in split_list]

        df = pd.DataFrame(data=sfc_probe, columns=['SFC_Probe'])
        df['Paths'] = file_paths
        df['String'] = split_list
        df['datetime'] = df['String'].apply(self.get_datetime)

        amb = []
        hot = []

        set_sfc_probe = []
        [set_sfc_probe.append(x) for x in sfc_probe if x not in set_sfc_probe]

        for x in range(len(set_sfc_probe)):
            temp = df[df['SFC_Probe'] ==
                      set_sfc_probe[x]].reset_index(drop=True)
            # Sorts list and puts most recent at top
            temp1 = temp.sort_values(
                by='datetime', ascending=False, na_position='last')
            latest = temp1.iloc[0, :]

            if 'DIE TEST ELEVATED' in latest.loc['SFC_Probe'].upper():
                try:
                    hot.append(latest['Paths'])
                except:
                    print('No Elevated File Found for {}'.format(
                        set_sfc_probe[x]))
                    continue
            elif 'DIE TEST BASELINE' in latest.loc['SFC_Probe'].upper():
                try:
                    amb.append(latest['Paths'])
                except:
                    print('No Baseline File Found for {}'.format(
                        set_sfc_probe[x]))
                    continue

        list_amb = amb
        list_hot = hot

        return list_amb, list_hot

    def check_dataset(self, asic_list, list_amb, list_hot):
        asic_list_len = len(asic_list)
        count_in_amb = 0
        count_in_hot = 0
        amb = [x for x in list_amb if os.path.basename(
            x).split('-')[0][-8:].strip() in asic_list]
        hot = [x for x in list_hot if os.path.basename(
            x).split('-')[0][-8:].strip() in asic_list]

        count_in_amb = len(amb)
        count_in_hot = len(hot)

        return ((count_in_amb == len(asic_list)) & (count_in_hot == len(asic_list))), amb, hot, asic_list_len, count_in_amb, count_in_hot

    def check_temp_folder(self):
        '''
        Checks if Temporary Folder 'tmp_HotChuck' already exists at the User CDrive location.

        Returns
        -------
        path : Path
            Path to Temporary Folder

        '''
        parent = os.path.expanduser('~')
        child = 'tmp_HotChuck'
        path = os.path.join(parent, child)
        if os.path.isdir(path):  # Does the directory exist
            if len(os.listdir(path)) != 0:  # Does it contain files
                self.delete_files(path)
                os.makedirs(path)
        else:
            os.makedirs(path)
        return path

    def copy_files(self, file_list, to_path, AMB_or_HOT):
        '''
        Takes in file list from Collect_Files function and utilizes shutil library to copy files to Temporary Folder.

        Parameters
        ----------
        file_list : List of Paths
            File List of Elevated and Baseline XML files
        to_path : Path
            Temporary Folder r"C:/Users/User_Name/tmp_HotChuck"
        AMB_or_HOT : String
            'Baseline' or 'Elevated' for console printing.

        Returns
        -------
        None.
        '''
        file_list_base = [os.path.basename(f) for f in file_list]
        file_list_new = [os.path.join(to_path, f) for f in file_list_base]
        for i in range(len(file_list)):
            shutil.copyfile(file_list[i], file_list_new[i])
            print('{}/{} {} has been stored temporarily.'.format(i,
                  len(file_list), AMB_or_HOT))
        return

    def collect_copy_files(self, location):
        '''
        Collects all files from Temporary Folder and resorts into Baseline and Elevated Lists.

        Parameters
        ----------
        location : Path
            Path to Temporary Folder [C:/Users/User_Name/tmp_HotChuck]

        Returns
        -------
        list_amb : List of Paths
            File List of Baseline Test Results (XML)
        list_hot : List of Paths
            File List of Elevated Test Results (XML)

        '''
        path = location + '\\*.xml'
        file_list = glob.glob(path)
        list_amb, list_hot = self.sort_files(file_list)

        return list_amb, list_hot

    def delete_files(self, path):
        '''
        Deletes Temporary Folder and all internal files.

        Parameters
        ----------
        path : Path
            Path to Temporary Folder.

        Returns
        -------
        None.

        '''
        shutil.rmtree(path)
        return

    def get_datetime(self, file_name):
        '''
        Retrieves Date/Time object from File Name for each test result passed.

        Parameters
        ----------
        file_name : String
            String Representation of File Path

        Returns
        -------
        datetime_object : datetime object
            Date/Time in MM-DD-YYYY HH:MM:SS

        '''
        string = file_name.split('-')[2].strip()[:15]
        datetime_object = datetime.strptime(string, '%m%d%Y %H%M%S')
        return datetime_object

    def create_test_list(self, tx_rx):
        '''
        Creates list of 17 tests.

        Returns
        -------
        test_list : List of Lists
            List of [Test, Measurement]

        '''
        test_list = []
        final_test = [f'{tx_rx} Element Peak-Peak', 'Pk-Pk']
        test_list.append(final_test)

        return test_list

    def create_data_dict(self, list_of_data_files, list_of_tests, AMB_or_HOT, tx_rx):
        '''
        Creates Dictionary of {Test:DataFrame} for each Test.

        Parameters
        ----------
        list_of_data_files : List of Test Result files
            Typically list_amb or list_hot
        list_of_tests : List of Tests
            Created by Function Create_Test_List
        AMB_or_HOT : String
            'Baseline' or 'Elevated' for console printing.

        Returns
        -------
        df_dict : Dictionary of {Test:DataFrame} Pairs

        '''

        df_dict = {}

        for test in list_of_tests:
            df = self.parse_xml_all(list_of_data_files, test, tx_rx)
            df.reset_index(drop=True)
            df_dict[test[0]+'___'+test[1]] = df

            print('{} added to {} DataFrame.'.format(test, AMB_or_HOT))
        return df_dict

    def parse_xml_all(self, file_list, test, tx_rx):
        '''
        Function to loop through test result file (XML) and gather needed data for the given test.

        Parameters
        ----------
        file_list : List of Paths
        test : List of Test and Measurement

        Returns
        -------
        results : DataFrame
            DataFrame with Prober Row_Column as index and numeric test data set to float.

        '''
        i = 1
        for f in file_list:
            tree = ET.parse(f)
            root = tree.getroot()

            temp = {}

            for child in root.findall('./Setup'):
                temp['Timestamp'] = child.find('Timestamp').text
                temp['ReportRevision'] = child.find('ReportRevision').text
                temp['Operator'] = child.find('Operator').text
                temp['Equipment'] = child.find('Equipment').text
                temp['PlatformTestSW'] = child.find('PlatformTestSW').text
                temp['ProductTestSW'] = child.find('ProductTestSW').text
                temp['Product'] = child.find('Product').text
                temp['ProcessStep'] = child.find('ProcessStep').text
                temp['LotNumber'] = child.find('LotNumber').text
                temp['ProductSN'] = child.find('ProductSN').text

            for child in root.findall('./Summary'):
                temp['OverallResult'] = child.find('OverallResult').text

            for child in root.findall('./Detail/Entry[Name="'+test[0]+'"]/Group[Measurement="'+test[1]+'"]/..'):
                temp['TestResult'] = child.find('Result').text

            for child in root.findall('./Detail/Entry[Name="'+test[0]+'"]/Group[Measurement="'+test[1]+'"]/Record/Value'):
                temp[child.attrib['Record']] = child.text

            # Constructing DataFrame
            if i == 1:
                temp1 = pd.DataFrame.from_dict(temp, orient='index', columns=[
                                               root.find('./Setup/ProductSN').text])
                result = temp1
            elif i == 2:
                temp2 = pd.DataFrame.from_dict(temp, orient='index', columns=[
                                               root.find('./Setup/ProductSN').text])
                result = pd.concat([temp1, temp2], axis=1)
            else:
                temp2 = pd.DataFrame.from_dict(temp, orient='index', columns=[
                                               root.find('./Setup/ProductSN').text])
                result = pd.concat([result, temp2], axis=1)

            # print('{}/{} has been parsed.'.format(i,len(file_list)))

            i += 1

        results = result.T
        results.iloc[:, results.columns.get_loc(
            f'{tx_rx} Element[0]'):] = results.iloc[:, results.columns.get_loc(f'{tx_rx} Element[0]'):].astype('float')
        return results

    def keys_match(self, df_amb, df_hot):
        '''
        Function to make sure Keys match between Data Dictionaries.
        Key Error is raised if not matching.

        Parameters
        ----------
        df_amb : Dictionary
            Dictionary from Baseline Test Results
        df_hot : Dictionary
            Dictionary from Elevated Test Results.

        Raises
        ------
        KeyError

        Returns
        -------
        None.

        '''
        if df_amb.keys() != df_hot.keys():
            raise KeyError('Keys between Baseline and Elevated do not match')


if __name__ == '__main__':
    pass
