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
            
            api.group.add_user(group='PrjTeam', user=user)

            payload = {
                "email": email,
                "fullname": fullname,
                # "username": email, 
                "sendPasswordReset": True,
                "last_name" : user.getProperty("last_name"),
                "first_name" : user.getProperty("first_name"),
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
                print(f"✅ User {email} created")
                
                # Add user to group:
                # TO DO: Keep only one when I know why users are not added with email instead of random username
                group_endpoint = f"{project_url}/@groups/PrjTeam"
                group_response = requests.patch(group_endpoint, headers=headers, json={"users": {username: 'true'} })
                groups_response = requests.patch(group_endpoint, headers=headers, json={"users": {response.json().get('username'): 'true'} })               
                
                
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
                print(f"⚠️ User {email} already exists")
            else:
                print(f"❌ Error creating {email}: {response.status_code} {response.text}")
                