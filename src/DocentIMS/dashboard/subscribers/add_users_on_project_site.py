# -*- coding: utf-8 -*-
import requests
from plone import api
from io import BytesIO
import base64
from  ..interfaces import IDocentimsSettings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.utils import formataddr
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.interface.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IMailSchema
from Acquisition import aq_inner
# from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from ..mailing import build_message
from ..mailing import dashboard_manager_info
import logging


logger = logging.getLogger(__name__)

# Timeout (seconds) for outbound calls to project sites, so a dead/slow
# project host cannot hang the user-add event handler (and its ZODB
# transaction) indefinitely.
REQUEST_TIMEOUT = 10

# Guard A: the userids this connector has already provisioned on its project
# site, stored as a hidden annotation on the Project. Re-saving the connector
# only acts on users NOT in this set, so existing members are never re-added
# or re-emailed. Only users that were added successfully are remembered, so a
# failed add is retried on the next save.
PROVISIONED_KEY = 'DocentIMS.dashboard.provisioned_users'


def _safe_json(response):
    """Return the response body as a dict, or {} if it is not JSON.

    Project sites can reply with a non-JSON or error body (e.g. on 409), and
    that must never raise and abort the whole batch.
    """
    try:
        data = response.json()
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def handler(obj, event):
    """ Event handler which will add users to project sites
    Not registered to content type since no content will be added to site
    """

    if obj.portal_type != "Project":
        return

    project_url = obj.project_url
    # Prefer the dedicated, editable "Project Title" field entered on the
    # Add Project Connection form; fall back to the object Title.
    project_title = getattr(obj, 'project_title', None) or obj.Title()
    user_list = obj.add_users or []

    # Guard A: only process users not already provisioned for this connector.
    annotations = IAnnotations(obj)
    provisioned = list(annotations.get(PROVISIONED_KEY, []))
    pending = [userid for userid in user_list if userid not in provisioned]
    if not pending:
        return

    basik = api.portal.get_registry_record('dashboard', interface=IDocentimsSettings) or ''
    users_endpoint = f"{project_url}/@users"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'Authorization': f'Basic {basik}'
    }

    created_users = []
    failed_users = []  # list of (name, reason) tuples
    newly_provisioned = []  # userids added successfully this run

    for userid in pending:
        # Guard B: one user's failure must never abort the batch or leave the
        # form with no feedback. Anything unexpected becomes a "could not add"
        # line and the loop continues with the next user.
        try:
            user = api.user.get(userid=userid)

            if user is None:
                logger.warning("User '%s' not found", userid)
                failed_users.append((userid, "not found on the dashboard"))
                continue

            # Plone PAS user properties
            username = user.getUserName()
            fullname = user.getProperty("fullname")
            email = user.getProperty("email")
            first_name = user.getProperty("first_name")
            groups = api.group.get_groups(username=username)
            first_time = 'PrjTeam' not in [g.id for g in groups]

            last_name = user.getProperty("last_name")
            company = user.getProperty("company")
            portal = api.portal.get()

            # Generate the reset token Plone uses internally
            pas_reset = getToolByName(portal, 'portal_password_reset')
            reset_info = pas_reset.requestReset(userid)
            token = reset_info['randomstring']

            portal_url = portal.absolute_url()
            reset_url = f"{portal_url}/passwordreset/{token}?userid={userid}"

            payload = {
                "email": email,
                "fullname": fullname,
                "username": username,
                # Dont send password reset, we should include it in our email below
                "sendPasswordReset": True,
                "last_name": last_name,
                "first_name": first_name,
                # "your_team_role" : user.getProperty("your_team_role"),
                "office_phone_number": user.getProperty("office_phone_number"),
                "cellphone_number": user.getProperty("cellphone_number"),
                "company": company,
                "description": user.getProperty("description"),
                "groups": [{"@id": "PrjTeam"}],
                "notes": user.getProperty("notes", ''),
                "properties": {
                    "email": email,
                    "fullname": fullname,
                    "last_name": last_name,
                    "first_name": first_name,
                    # "your_team_role" : user.getProperty("your_team_role"),
                    "office_phone_number": user.getProperty("office_phone_number"),
                    "cellphone_number": user.getProperty("cellphone_number"),
                    "company": company,
                    "description": user.getProperty("description"),
                    "notes": user.getProperty("notes")
                }
            }

            response = requests.post(users_endpoint, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)

            # Add image to user and add user to group
            if response.status_code in (200, 201, 409):  # 201 = created, 409 = already present
                body = _safe_json(response)

                # user successfully added, add them to team group on dashboard
                api.group.add_user(groupname='PrjTeam', username=username)

                # Add user to the project-site team group.
                group_endpoint = f"{project_url}/@groups/PrjTeam"
                requests.patch(group_endpoint, headers=headers, json={"users": {username: 'true'}}, timeout=REQUEST_TIMEOUT)
                # If the project site created the account under a different
                # login than we sent, add that one too (defensive).
                resp_username = body.get('username')
                if resp_username and resp_username != username:
                    requests.patch(group_endpoint, headers=headers, json={"users": {resp_username: 'true'}}, timeout=REQUEST_TIMEOUT)

                portal = api.portal.get()
                portal_url = portal.absolute_url()
                register_url = f"{portal_url}/register"

                # Dashboard manager = first user holding the "Dashboard Manager"
                # role (blank when no user holds it).
                dashboard_manager_fullname, dashboard_manager_company = \
                    dashboard_manager_info()

                # Different mail for first and next project
                mail_subject = "Welcome to a New Project"
                mail_message = api.portal.get_registry_record('email_message_returning', interface=IDocentimsSettings) or ''

                if first_time:
                    mail_subject = 'Welcome to Docent Dashboard site'
                    mail_message = api.portal.get_registry_record('email_message', interface=IDocentimsSettings) or ''
                # raw_message = mail_message.raw  if we can get rich text to work
                raw_message = mail_message

                # Note add these to 'email_pre_view' too
                # To do: resuse them
                context_vars = {
                    "portal_url": portal_url,
                    "register_url": register_url,
                    "email": email,
                    "fullname": fullname,
                    "username": username,
                    "last_name": last_name,
                    "first_name": first_name,
                    "company": company,
                    "dashboard_manager_company": dashboard_manager_company,
                    "dashboard_manager_fullname": dashboard_manager_fullname,
                    "portal": portal,
                    "project_url": project_url,
                    "project_title": project_title,
                    "project_name": project_title,
                    "user_name": username,
                    "username": username,
                    "reset_url": reset_url,
                    "dashboard_set_password_url": reset_url,
                }

                # DO variable substitution of mail body
                message = build_message(raw_message, obj, context_vars)

                registry = getUtility(IRegistry)

                mailhost = getToolByName(portal, "MailHost")
                if not mailhost:
                    raise ComponentLookupError(
                        "You must have a Mailhost utility to \
                    execute this action"
                    )

                message_html = MIMEText(message, 'html', _charset='UTF-8')

                # Outbound-only "do not reply" sender. Keep the configured
                # sender domain (the SMTP2GO-verified domain) but force a
                # do-not-reply local part and display name, and add headers
                # that discourage replies and stop auto-responders (RFC 3834).
                configured_from = api.portal.get_registry_record('plone.email_from_address') or ''
                from_domain = configured_from.split('@')[-1] if '@' in configured_from else 'docentdashboard.org'
                noreply_address = f'do-not-reply@{from_domain}'
                noreply_sender = formataddr(('Do Not Reply', noreply_address))

                message_html['Subject'] = mail_subject
                message_html['From'] = noreply_sender
                message_html['To'] = email
                message_html['Reply-To'] = noreply_sender
                message_html['Auto-Submitted'] = 'auto-generated'

                mailhost.send(message_html.as_string())

                # Upload portrait if exists. Use the created object's @id from
                # the response body; skip safely if it isn't present.
                portal_membership = api.portal.get_tool('portal_membership')
                portrait = portal_membership.getPersonalPortrait(userid)
                portrait_endpoint = body.get('@id')
                if portrait and hasattr(portrait, 'data') and portrait_endpoint:
                    portrait_bytes = portrait.data  # binary image, None if 'default image'

                    if portrait_bytes:
                        portrait_mime = getattr(portrait, "contentType", "image/jpeg")
                        filename = "portrait"
                        portrait_b64 = base64.b64encode(portrait_bytes).decode("utf-8")

                        r = requests.patch(portrait_endpoint,
                                           headers=headers,
                                           json={'portrait': {'content-type': portrait_mime,
                                                              'data': portrait_b64,
                                                              'encoding': "base64",
                                                              'filename': filename}},
                                           timeout=REQUEST_TIMEOUT,
                                           )

                        if r.status_code == 204:
                            logger.info("Portrait for '%s' uploaded successfully", userid)
                        else:
                            logger.warning("Failed to upload portrait for '%s'", userid)

                created_users.append(fullname or username)
                newly_provisioned.append(userid)

            elif response.status_code == 500:
                logger.error("Project site error 500 creating %s: %s", username, response.text)
                failed_users.append((fullname, "the project site reported a server error"))
            elif response.status_code == 401:
                failed_users.append((fullname, "wrong project-site username/password (fix the 'Basic' credential)"))
            elif response.status_code == 403:
                failed_users.append((fullname, "the project-site account lacks permission to add members (needs Manager)"))
            elif response.status_code == 400:
                # plone.restapi returns 400 when the user already exists.
                failed_users.append((fullname, "most likely already on the project"))
            else:
                logger.error(
                    "Error adding %s to project %s: %s %s",
                    username, project_url, response.status_code, response.text,
                )
                failed_users.append((fullname, f"unexpected response from the project site (HTTP {response.status_code})"))

        except Exception:
            logger.exception("Unexpected error adding '%s' to project %s", userid, project_url)
            failed_users.append((userid, "an unexpected error (see the instance log)"))

    # Guard A: remember the users we added successfully so a later save does
    # not re-add or re-email them.
    if newly_provisioned:
        annotations[PROVISIONED_KEY] = provisioned + newly_provisioned

    # One consolidated message listing everyone who could not be created, then
    # the per-user "added and mailed" notices below it.
    if failed_users:
        reasons = {reason for _, reason in failed_users}
        names = ", ".join(str(name) for name, _ in failed_users)
        if len(reasons) == 1:
            api.portal.show_message(
                message=f"Not created ({reasons.pop()}): {names}. No emails sent to these users",
                type='warning',
            )
        else:
            detail = "; ".join(f"{name} ({reason})" for name, reason in failed_users)
            api.portal.show_message(
                message=f"Not created — {detail}. No emails sent to these users",
                type='warning',
            )
    if created_users:
        api.portal.show_message(
            message=f"Added: {', '.join(created_users)}. Welcome email sent to these users",
            type='info',
        )
