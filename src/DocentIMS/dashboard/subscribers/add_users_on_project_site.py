# -*- coding: utf-8 -*-
import requests
from plone import api
from io import BytesIO
import base64
from  ..interfaces import IDocentimsSettings


def handler(obj, event):
    """ Event handler which will add users to project sites
    Not registered to content type since no content will be added to site
    """
    
    if obj.portal_type == "Project":
        project_url = obj.project_url
        user_list = obj.add_users
        
        #Dummy password, TO DO: Change / get from some settings
        # auth = ("admin", "admin")
        basik =  api.portal.get_registry_record('dashboard', interface=IDocentimsSettings) or ''
        users_endpoint = f"{project_url}/@users"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            'Authorization': f'Basic {basik}'
        }

        for userid in user_list:
            user = api.user.get(userid=userid)

            if user is None:
                print(f"⚠️ User '{userid}' not found")
                continue

            # Plone PAS user properties
            username = user.getUserName()
            fullname = user.getProperty("fullname")
            email = user.getProperty("email")
            first_name = user.getProperty("first_name")
            
            api.group.add_user(groupname='PrjTeam', username=username)
            

            payload = {
                "email": email,
                "fullname": fullname,
                "username": username, 
                "sendPasswordReset": True,
                "last_name" : user.getProperty("last_name"),
                "first_name" : first_name,
                # "your_team_role" : user.getProperty("your_team_role"),
                "your_team_role" : '--',
                "office_phone_number" : user.getProperty("office_phone_number"),
                "cellphone_number" : user.getProperty("cellphone_number"),
                "company" : user.getProperty("company"),
                "description" : user.getProperty("description"),
                "groups" : [{"@id": "PrjTeam"}]
            }
            
            
            response = requests.post(users_endpoint, headers=headers, json=payload)
            
            
            
            # Add image to user and add user to group
            
            if response.status_code in (200, 201):  # 201 = created
                
                # user successfully added, lets send email
                #code to send email here
                
                
                # Add user to group:
                # TO DO: Keep only one when I know why users are not added with email instead of random username
                group_endpoint = f"{project_url}/@groups/PrjTeam"
                group_response = requests.patch(group_endpoint, headers=headers, json={"users": {username: 'true'} })
                groups_response = requests.patch(group_endpoint, headers=headers, json={"users": {response.json().get('username'): 'true'} })               
                
                #something =  api.portal.get_registry_record('something', interface=IDocentimsSettings) or ''

                
                dashboard_manager_fullname = ''
                dashboard_manager_company = ''
                
                # 1. Find group
                group = api.group.get(groupname="DashboardManagers")
                if group:
                    members = group.getMemberIds()
                    
                    # 2. Find first person
                    if members:
                        user = api.user.get(userid=members[0])
                        
                        if user:
                            # 3. Full name
                            dashboard_manager_fullname = user.getProperty("fullname", "")
                            
                            # 4. Company
                            dashboard_manager_company = user.getProperty("company", "")

                # print(dashboard_manager_fullname)
                # print(dashboard_manager_company)
                
                api.portal.send_email(
                    recipient       = email,
                    subject         = "Welcome to Docent Dashboard site",
                    body            = f"""  Hello {first_name},\nMy name is {dashboard_manager_fullname}, and I manage the Dashboard for all \nprojects. The Dashboard gives you a convenient, central place to view and access all your projects. You'll see more once you get started.\nYou're receiving this email because you've been added to your first project with <Docent Client name>.\n Welcome to the team!\n To get started, please follow these three steps:\n Follow this link <Standard Plone Registration Link to DB> to register with the Dashboard.\n Once registered, return to the Dashboard and review the Help files to familiarize yourself with the system.\nYou will receive a separate email from the project site with instructions on signing up for your specific project.\nThanks for taking a few minutes to get set up. If you have any questions, don't hesitate to reach out.\n Best regards,\n {dashboard_manager_fullname}\n {dashboard_manager_company}"""
                )
                
                # Upload portrait if exists
                portal_membership = api.portal.get_tool('portal_membership')
                portrait = portal_membership.getPersonalPortrait(userid) 
                if portrait and hasattr(portrait, 'data'):
                    portrait_endpoint = response.json()['@id']
                    portrait_bytes = portrait.data # the binary image, None if it is the 'default image'
                    
                    if portrait_bytes:                        
                        portrait_mime = getattr(portrait, "contentType", "image/jpeg")
                        # filename = portrait.__name__ or "portrait"
                        filename =  "portrait"
                        portrait_b64 = base64.b64encode(portrait_bytes).decode("utf-8")
                        
                        r = requests.patch(portrait_endpoint, 
                                        headers= headers,
                                        json={'portrait': {'content-type': portrait_mime , 
                                                            'data': portrait_b64, 
                                                            'encoding': "base64", 
                                                            'filename': filename}}, 
                                        )
                        
                        if r.status_code == 204:
                            print(f"✅ Portrait for '{userid}' uploaded successfully")
                        else:
                            print(f"⚠️ Failed to upload portrait for '{userid}'")
            elif response.status_code == 409:
                print(f"⚠️ User {username} already exists")
            else:
                print(f"❌ Error creating {username}: {response.status_code} {response.text}")
                