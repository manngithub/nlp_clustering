import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


def consider_customer(data, customer):
    """
    This function takes data from all the customer; consider the data for a specified customer and filter the rest
    
    :type data: Pandas dataframe
    :param data: customer data from simulation
    
    :return: dataframe selection for a specified customer
    """
    return data.loc[data.Customer == customer].reset_index(drop=True)

def initial_text_processing(data, column):
    """
    Write text processing steps here
    
    :type data: Pandas dataframe
    :param data: customer data from simulation
    
    :type column: string
    :param column: Customer_Tag column in data dataframe
    
    :return: dataframe after performing data cleaning steps on the speficied column
    """
    df = data.copy()
    df[column] = df[column].str.strip() # remove any spaces before and after the string for specified column
    return df

def extract_all_patterns(cdata, parent_key, n, p_list, location, threshold):  
    """
    This function extract starting or ending pattern from the given tags
    
    :type cdata: list
    :param cdata: list of Customer_Tags
    
    :type parent_key: string
    :param parent_key: Identified common pattern for cdata
    
    :type n: int
    :param n: string selection of length n from "starting" or "ending"
    
    :type p_list: list 
    :param p_list: list of identified patterns
    
    :type location: string
    :param location: "starting" or "ending"
    
    :type threshold: int
    :param threshold: least number of tags necessary for any identified pattern
    
    :return: tuple(nested dictionaries (like tree) of identified patterns, list of identified patterns)
    """
    #print(parent_key)
    #print(cdata)
    if location == 'starting':
        potential_patterns = list(set([tag[0:n] for tag in cdata])) # find unique strings of length n from starting
    else: # 'ending'
        potential_patterns = list(set([tag[-n:] for tag in cdata])) # find unique strings of length n from ending
    pp_dict = {}
    for pp in potential_patterns:
        if location == 'starting':
            cdata_pp = [tag for tag in cdata if tag[0:n] == pp]
        else: # 'ending'
            cdata_pp = [tag for tag in cdata if tag[-n:] == pp]
        if len(cdata_pp) < threshold:
            pp_dict[pp] = parent_key # end point for this branch
            p_list.append(parent_key)
            #print(pp, parent_key)
        else:
            # recursively keep looking for any pattern
            pp_dict[pp] = extract_all_patterns(cdata_pp, pp, n+1, p_list, location, threshold)[0] # (key, value) for dictionary
    return (pp_dict, p_list)

def identify_tag_pattern(tag, patterns, location):
    """
    This function output the longest string match as pattern for the specified tag
    
    :type tag: string
    :param tag: customer tag
    
    :type patterns: list
    :param patterns: sorted patterns (descending order by length)
    
    :return: longest pattern from the sorted patterns
    """
    if location == 'Starting':
        for pattern in patterns:
            if tag.startswith(pattern):
                return pattern
    else: # location == 'ending'
        for pattern in patterns:
            if tag.endswith(pattern):
                return pattern
            
def record_customer_patterns(data, customer, threshold_starting, threshold_ending, overwrite_thresholds):
    """
    This function select the single customer dataframe and create two new columns for starting and ending patterns for each tag
    
    :type data: Pandas dataframe
    :param data: customer data from simulation  
    
    :type threshold_starting: int
    :param threshold_starting: least number of tags necessary for any identified starting pattern
    
    :type threshold_ending: int
    :param threshold_ending: least number of tags necessary for any identified ending pattern
    
    :return: tuple (customer dataframe with two new columns of starting and ending pattern for each tag, starting pattern dictionary, ending pattern dictionary)
    """
    # select data for the specified customer
    cdata_df = consider_customer(data, customer)
    
    # clean data for the specified column
    cdata_df = initial_text_processing(cdata_df, column = 'Customer_Tag')
    
    # create list of all customer tags
    cdata = cdata_df.Customer_Tag.tolist() 
    
    # Overwrite threshold_starting and threshold_ending
    if overwrite_thresholds == True:
        # threshold_starting = number of tags/5 ; means 5 patterns from beginning of the string
        # threshold_ending = number of tags/2 ; means 2 patterns from ending of the string
        threshold_starting = cdata_df.shape[0]/5
        threshold_ending = cdata_df.shape[0]/2
    
    # extract patterns from all customers tags
    pp_dict_starting, p_list_starting = extract_all_patterns(cdata, '', 1, [], "starting", threshold_starting) 
    pp_dict_ending, p_list_ending = extract_all_patterns(cdata, '', 1, [], "ending", threshold_ending) 
    
    """
    p_list_starting(list): list of identified starting patterns from the customer data
    p_list_ending(list): list of identified ending patterns from the customer data
    """

    # Sort the extracted patterns by length in descending order
    patterns_starting = sorted(list(set(p_list_starting)), key=len)[::-1] # take unique patterns and sort them by length
    patterns_ending = sorted(list(set(p_list_ending)), key=len)[::-1] # take unique patterns and sort them by length

    # Record the corresponding starting and ending pattern for each customer tag
    cdata_df['Starting_Pattern'] = cdata_df['Customer_Tag'].apply(identify_tag_pattern, \
                                                                  patterns = patterns_starting, location = 'Starting')
    cdata_df['Ending_Pattern'] = cdata_df['Customer_Tag'].apply(identify_tag_pattern, \
                                                                patterns = patterns_ending, location = 'Ending')
    
    return (cdata_df, pp_dict_starting, pp_dict_ending)