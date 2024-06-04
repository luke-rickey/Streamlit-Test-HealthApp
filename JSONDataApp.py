import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import json
import numpy as np
import math

#Import the json file from your directory into read_json to make a dataframe
#data = pd.read_json('/content/jsonformatter.json')

#Only include service_code with 23, found through searching dataframe filtering by substring
def contain_23(x):
  result = False
  if type(x) is list:
    result = "23" in x
  return result

#Only include rows with provided npi
def contain_npi(provider_row, npi_row):
  result = False
  if type(npi_row) is list:
    if npi in npi_row:
      return provider_row
    if npi2 in npi_row:
      return provider_row
  return result

#Only include rows with provided provider_reference number
def contain_reference_number(listOfNumbers, num, num2):
  result = False
  if type(listOfNumbers) is list:
    if num in listOfNumbers:
      return True
    if num2 in listOfNumbers:
      return True
  return result

#Change Negotiated Rates Values to the RVU Conversion.
def change_by_RVU(x):
  return (x/RVU_Value)

#Main Code Definition
def MainDataApp(json_File):
  xstsa = 5
  with open(json_File, 'r') as f:
    data3 = json.load(f)
  #df = pd.json_normalize(data2, 'negotiated_rates')

  #Normalizes to Get only the columns we want
  df = pd.json_normalize(data3, 'negotiated_rates')
  df1 = (df.pop('negotiated_prices').explode().apply(pd.Series))
  df = pd.concat([df, df1], axis=1)
  df = df.drop(df.columns[[1, 3]], axis=1)

  #Get rid of Institutional Values
  df = df[df['billing_class'] == billing_type]
  if billing_type == "professional":
    df = df[df['service_code'].apply(contain_23)]

  #############################################FirstLine
  with open('jsonl_Mar012024_First_Line.json', 'r') as f:
    data2 = json.load(f)

  #Normalizes to Get only the columns we want
  df2 = pd.json_normalize(data2, 'provider_references')
  df3 = (df2.pop('provider_groups').explode().apply(pd.Series))
  df2 = pd.concat([df2, df3], axis=1)
  df2 = df2.drop(df2.columns[[1]], axis=1)
  #############################################
  
  if npi != None:
    df9 = df2.apply(
      lambda row: contain_npi(row['provider_group_id'], row['npi']),
      axis=1
    )
    list_of_provider_reference = df9.loc[df9 != False].index.tolist()
    index_of_provider_reference = list_of_provider_reference[0]
    actual_provider_reference = df9[index_of_provider_reference]
    if npi2 != None:
      index_of_provider_reference2 = list_of_provider_reference[1]
      actual_provider_reference2 = df9[index_of_provider_reference2]
      df = df[df['provider_references'].apply(contain_reference_number, args=(actual_provider_reference, actual_provider_reference2,))]
    else:
      df = df[df['provider_references'].apply(contain_reference_number, args=(actual_provider_reference, npi2,))]

  references_column = df['negotiated_rate']
  new_values = references_column.apply(change_by_RVU)
  df['negotiated_rate'] = new_values

  #Change Negotiated Rates Values to be formatted in $ amount.
  df['negotiated_rate'] = df['negotiated_rate'].apply(lambda x: float("{:.2f}".format(x)))
  df['negotiated_rate'] = '$' + df['negotiated_rate'].astype(str)

  return df


#result = pd.concat([df, df2], axis=1)
#print(df.columns.tolist())
#Downloads the CSV into the project directory
#df2.to_csv('Provider_Group_NPI_InNetMar012024.csv', encoding='utf-8')


#Deploy website
def main():
  st.set_page_config(page_title="JSON Data Formatter", page_icon=":necktie:")
  st.header("JSON Data Formatter :necktie:")
  global billing_type
  billing_type = "Professional"
  billing_selector = st.selectbox("Choose between Professional or Institutional Billing:", ("professional", "institutional"))
  billing_type = billing_selector

  global json_File, RVU_Value
  RVU_Value = 2.800
  rvu_dict = {'jsonformatter12001.json': 2.800, 'jsonformatter12002.json': 3.370, 'jsonformatter12011.json': 3.350, 'jsonformatter12013.json': 3.490,
              'jsonformatter92950.json': 9.840, 'jsonformatter93010.json': 0.240, 'jsonformatter99236.json': 6.120, 'jsonformatter99283.json': 2.110,
              'jsonformatter99284.json': 3.560, 'jsonformatter99285.json': 4.420, 'jsonformatter99291.json': 8.160, 'jsonformatter99292.json': 3.560}
  json_File_selector = st.selectbox("Choose Billing Code:", ('jsonformatter12001.json', 'jsonformatter12002.json', 'jsonformatter12011.json', 'jsonformatter12013.json',
                                                     'jsonformatter92950.json', 'jsonformatter93010.json', 'jsonformatter99236.json', 'jsonformatter99283.json', 
                                                     'jsonformatter99284.json', 'jsonformatter99285.json', 'jsonformatter99291.json', 'jsonformatter99292.json'))
  json_File = json_File_selector
  RVU_Value = rvu_dict[json_File]

  global npi, npi2
  npi = None
  number = st.number_input("Insert the NPI you would like the data for, then press enter:", value=None, step=1, placeholder="Type a number...")
  npi = number
  npi2 = None
  number2 = None
  npi_comparison = st.selectbox("Select the number of NPIs you would like to view:", ('1', '2'))
  if npi_comparison == '2':
    number2 = st.number_input("Insert the second NPI you would like the data for, then press enter:", value=None, step=1, placeholder="Type a number...")
  if number2 is not None:
    npi2 = number2

  if st.button("Get Default Data"):
    df = MainDataApp(json_File)
    st.dataframe(df)



if __name__ == '__main__':
  main()
