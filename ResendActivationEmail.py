
"""

Below is a list of steps that this script completes:
    1) Reach out to the Okta API to grab a list of users that have not completed their account activation
    2) Identify the user ID value of those users
    3) Send the activation email to those users

"""
import os
import time
import requests

""" Colorama library used to color text and make it nicer to look it """
from colorama import init as colorama_init
from colorama import Fore
colorama_init()

start_time = time.time() #used to calculate the total time it took to run the script

""" Environment variables for the API key and Okta tenant URL """
""" If you decide to hardcode the API key below, comment out lines 23-27 """
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv() #looks for the .env file
load_dotenv(dotenv_path) #loads the .env file as environment variables
api_token = os.getenv("API_KEY") #uses the new API_KEY environment variable as api_token
okta_tenant_url = os.getenv("OKTA_DOMAIN")

# Use the lines below to hard-code the API key and Okta tenant URL
# api_token = "abc123"
# okta_tenant_url = "example.okta.com"

""" Specifies the headers for the API call as described in the Okta documentation """
headers = {
    'Content-Type': 'application/json',
    'Accept' : 'application/json',
    'Authorization' : 'SSWS ' + api_token
}


""" Calls the Okta API and stores the information in the result variable. Then pulls the json data into users """
try:
    print('\nAttempting API query to grab users...')
    result = requests.get(f"https://{okta_tenant_url}/api/v1/users?filter=status+eq+%22PROVISIONED%22",headers=headers)
    links = result.links #this is used for pagination
    users = result.json()


    """ If the response code is successful [200] then print the confirmation """
    if str(result) == "<Response [200]>":
        print(f"{Fore.GREEN}The API query was successful " + str(result) + f"{Fore.RESET}")


    """ Pagination loop to scroll through multiple pages of the API result """
    print('Scrolling through API result pages...')
    while 'next' in links:
        url = links['next']['url']
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        next_users = result.json()
        users += next_users
        links = result.links


    """ For loop that evaluates each user, grabs the okta user_id, then posts an API call to reactivate and send an email to each user """
    print(f'Found {str(len(users))} users. Attempting to send activation emails...')
    emails_sent = 0 #used to count the number of emails sent
    for user in users:
        user_id = user['id']
        try:
            api_post = requests.post(f'https://{okta_tenant_url}/api/v1/users/{user_id}/lifecycle/reactivate?sendEmail=true',headers=headers)
            if str(api_post) == '<Response [200]>':
                emails_sent += 1
        except:
            print(f"{Fore.RED}The API POST had an issue " + str(api_post) + f"{Fore.RESET}")


    """ Prints the number of emails sent """
    print(f'{Fore.CYAN}Number of reactivation emails sent: {str(emails_sent)}{Fore.RESET}')


except: #If there is a problem with the API query, it will hit this except clause and will print the response code
    print(f"{Fore.RED}The API query had an issue {str(result)}{Fore.RESET}")


""" Calculate and print the total time it took to run the script. """
end_time = time.time()
total_time = round(end_time - start_time,2)
print(f'\n{Fore.YELLOW}This script finished in {str(total_time)} seconds.\n {Fore.RESET}')

