# -*- coding: utf-8 -*-
import requests
from plone import api


def handler(obj, event):
    """ Event handler which will add users to project sites
    Not registered to content type since no content will be added to site
    """
    
    if obj.portal_type == "Project":
    
        project_url = obj.project_url
        user_list = obj.add_users
        
        #TO DO: Change
        auth = ("admin", "admin")
        users_endpoint = f"{project_url}/@users"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
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

            payload = {
                "email": email,
                "fullname": fullname,
                "sendPasswordReset": True
            }
            
            
            
            response = requests.post(users_endpoint, auth=auth, headers=headers, json=payload)

            if response.status_code in (200, 201):  # 201 = created
                print(f"✅ User {email} created")
            elif response.status_code == 409:
                print(f"⚠️ User {email} already exists")
            else:
                print(f"❌ Error creating {email}: {response.status_code} {response.text}")
                