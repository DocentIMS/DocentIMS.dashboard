# -*- coding: utf-8 -*-
import requests
from plone import api
from io import BytesIO
import base64


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
            #TO DO: other fields

            payload = {
                "email": email,
                "fullname": fullname,
                "sendPasswordReset": True
            }
            
            
            
            response = requests.post(users_endpoint, auth=auth, headers=headers, json=payload)
            

            if response.status_code in (200, 201):  # 201 = created
                print(f"✅ User {email} created")
                import pdb; pdb.set_trace()
                # Upload portrait if exists
                portal_membership = api.portal.get_tool('portal_membership')
                portrait = portal_membership.getPersonalPortrait(userid) 
                if portrait:
                    portrait_endpoint = f"{users_endpoint}/{username}" # /@portrait"
                    portrait_bytes = portrait.data       # the binary image
                    portrait_mime = getattr(portrait, "contentType", "image/jpeg")
                    filename = portrait.__name__ or "portrait"
                    portrait_b64 = base64.b64encode(portrait_bytes).decode("utf-8")
                    
                    # # Prepare PATCH payload
                    # portrait_payload = {
                    #     "portrait": {
                    #         "filename": portrait_filename,
                    #         "content-type": portrait_mime,
                    #         "encoding": "base64",
                    #         "data": portrait_b64
                    #     }
                    # }
                    
                    # r = requests.patch(portrait_endpoint, auth=auth, headers=headers, json=portrait_payload)


                    r = requests.patch(portrait_endpoint, 
                                       headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                       json={'portrait': {'content-type': portrait_mime , 
                                                          'data': portrait_b64, 
                                                          'encoding': "base64", 
                                                          'filename': filename}}, 
                                       auth=auth)
                    
                    if r.status_code == 204:
                        print(f"✅ Portrait for '{userid}' uploaded successfully")
                    else:
                        print(f"⚠️ Failed to upload portrait for '{userid}'")
            elif response.status_code == 409:
                print(f"⚠️ User {email} already exists")
            else:
                print(f"❌ Error creating {email}: {response.status_code} {response.text}")
                