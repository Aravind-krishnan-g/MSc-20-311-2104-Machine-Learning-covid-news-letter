#!/usr/bin/env python
# coding: utf-8

# ## IMPORTING LIBRARIES

# In[23]:


import pandas as pd
import streamlit as st # web application framework

# libraries for sending mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# to check validity of email addresses
import validators 


# ## MAIN CODE

# In[24]:


class mail_generator:
    
    def __init__(self):
        self.df=pd.read_csv(r'https://api.covid19india.org/csv/latest/state_wise_daily.csv') #load covid data
        self.df['Date_YMD']=pd.to_datetime(self.df['Date_YMD']) # convert to pandas timestamp
        self.df=self.df.drop(columns=['UN'],axis=0) # drop unnecessary column
        # states names wiith their respective codes
        self.codes={'India (overall)':'TT','Andaman and Nicobar Islands':'AN','Andhra Pradesh':'AP','Arunachal Pradesh':'AR',
                    'Assam' :'AS','Bihar':'BR','Chandigarh':'CH', 'Chhattisgarh':'CT',
                    'Dadra and Nagar Haveli':'DN','Daman and Diu':'DD','Delhi':'DL','Goa':'GA',
                    'Gujarat':'GJ','Haryana':'HR','Himachal Pradesh':'HP','Jammu and Kashmir':'JK',
                    'Jharkhand':'JH', 'Karnataka':'KA','Kerala':'KL','Ladakh':'LA','Lakshadweep':'LD',
                    'Madhya Pradesh':'MP','Maharashtra':'MH','Manipur':'MN','Meghalaya':'ML','Mizoram':'MZ',
                    'Nagaland':'NL','Orissa':'OR','Pondicherry':'PY','Punjab':'PB','Rajasthan':'RJ',
                    'Sikkim':'SK','Tamil Nadu':'TN','Telangana':'TG','Tripura':'TR','Uttar Pradesh':'UP',
                    'Uttarakhand':'UT','West Bengal':'WB'}
    
    # to get covid data regarding a particular region/state
    def get_state_data(self,state_code):
        
        this_date=pd.Timestamp.now().date() # gets current date
        if(any(self.df['Date_YMD'] == this_date)): # check whether data in current date is available
            latest_data_available = True
        else:
            latest_data_available = False
            
        last_date=self.df['Date_YMD'][self.df.index[-1]] # gets latest available date
        condition=(self.df['Date_YMD']==last_date)
        datafr=self.df[condition].reset_index()
        conf=datafr[state_code][0] # confirmed cases
        recov=datafr[state_code][1] # recovered cases
        death=datafr[state_code][2] # deceased cases
        return  [conf,recov,death,last_date.strftime('%Y-%m-%d'),latest_data_available] 
        
            
        
        
    # to sent automated mail 
    def sent_email(self,address,html_file,state,date):
        sender_address    = "covid.news.letter.india@gmail.com" 
        sender_password   = "covidnewsletter"
        recipient_address = address
        email_parts=address.split('@')
        recipient_name=email_parts[0]
        # Instance of MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = sender_address
        msg['To'] = recipient_address
        msg['Subject'] = " Covid news letter "
        intro='Hello '+ recipient_name+','+' here is an update related to covid cases. '
        body = "Daily covid cases in "+state+' as on '+date+" :"
        msg.attach(MIMEText(intro,'plain'))
        msg.attach(MIMEText(body,'plain'))
        msg.attach(MIMEText(html_file,'html')) # covid data
        
        # connecting to server
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(sender_address, sender_password ) # login credentials
            text = msg.as_string()
            server.sendmail(sender_address, recipient_address, text)
            st.success('Email sent successfully') # display success message
            server.quit()
        except:
            st.error("SMPT server connection error") # display error message
            
            
    def display(self):
        
        st.title("Daily covid news letter") # setting title
        exp= st.beta_expander("About") # 'About' section contains details about the project
        exp.write(" This project was done as a part of Msc-Problem solving with python course.") 
        exp.write("You can check out the work at [github](https://github.com/Aravind-krishnan-g/MSc-20-311-2104-Machine-Learning-covid-news-letter)")
        
        states=list(self.codes.keys()) # list of state names
        state=st.selectbox('Select a state you want\(You have an option to get overall India stats\)',states)
        data_collected = self.get_state_data(self.codes[state]) # getting covid data
        if(state and not data_collected[-1]): 
            if st.checkbox('Check for today\'s data'): # check for latest information
                st.info('Today\'s covid data is not available at the moment. Fetching the latest data from the server.')
            
        if(state):
            address=st.text_input("Enter your mail id") # enter email id
            if(not validators.email(address) and address): st.error('Please enter a valid email address!!')
            dict_data={'Confirmed':[str(data_collected[0])],
                       'Recovered':[str(data_collected[1])],
                       'Deceased' :[str(data_collected[2])]                     
                       }
            df=pd.DataFrame.from_dict(dict_data)
            df.index=['Number of cases']
            if(st.button('Send newsletter') and validators.email(address)):
                with st.spinner('sending...'):
                    self.sent_email(address,df.to_html(),state,data_collected[-2])
                
        
        
        


# ## DRIVER CODE

# In[25]:


class_obj=mail_generator() # creating class object
class_obj.display() # running web app

