# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.namedfile.file import NamedBlobImage
import logging

logger = logging.getLogger(__name__)

# Folder (site-relative) holding the selectable preset icons.
PRESET_PATH = '/images/profile-icons'
# Folder where per-user uploaded icons are stored as Image content.
UPLOAD_PATH = '/images/user-icons'


class SetUserIcon(BrowserView):
    """Let the logged-in user choose a dashboard icon: pick a preset from
    PRESET_PATH or upload their own. The chosen image URL is stored in the
    'user_icon' member property. The Plone portrait is never touched.
    """

    status = ''

    def __call__(self):
        if self.request.get('REQUEST_METHOD') == 'POST' and \
                self.request.get('form.submitted'):
            self.handle_submit()
        return self.index()

    # -- data for the template --------------------------------------------

    def is_anonymous(self):
        return api.user.is_anonymous()

    def current_icon(self):
        member = api.user.get_current()
        return member.getProperty('user_icon', '') if member else ''

    def get_presets(self):
        """List the preset icons as {url, title} (url embeds the image)."""
        folder = api.content.get(path=PRESET_PATH)
        if folder is None:
            return []
        presets = []
        for brain in api.content.find(context=folder, portal_type='Image'):
            presets.append({
                'url': brain.getURL() + '/@@images/image',
                'title': brain.Title or brain.id,
            })
        return presets

    # -- form handling ----------------------------------------------------

    def handle_submit(self):
        if self.is_anonymous():
            self.status = 'Please log in first.'
            return
        member = api.user.get_current()
        choice = self.request.get('icon_choice', 'default')

        if choice == 'upload':
            url = self._store_upload(member.getId())
            if url:
                member.setMemberProperties({'user_icon': url})
                self.status = 'Your uploaded icon has been saved.'
            else:
                self.status = 'Please choose an image file to upload.'
        else:
            preset = self.request.get('preset', '')
            if preset:
                member.setMemberProperties({'user_icon': preset})
                self.status = 'Your icon has been set.'
            else:
                self.status = 'Please select one of the preset icons.'

    def _store_upload(self, userid):
        """Store the uploaded file as an Image under UPLOAD_PATH and return
        an embeddable URL, or None if nothing usable was uploaded."""
        fileupload = self.request.get('icon_file')
        filename = getattr(fileupload, 'filename', '')
        if not fileupload or not filename:
            return None
        data = fileupload.read()
        if not data:
            return None

        try:
            with api.env.adopt_roles(['Manager']):
                folder = api.content.get(path=UPLOAD_PATH)
                if folder is None:
                    parent = api.content.get(path='/images')
                    if parent is None:
                        logger.warning("No /images folder to store user icons")
                        return None
                    folder = api.content.create(
                        container=parent, type='Folder',
                        id='user-icons', title='User Icons')
                existing = folder.get(userid)
                if existing is not None:
                    api.content.delete(obj=existing)
                image = api.content.create(
                    container=folder, type='Image', id=userid,
                    title='%s icon' % userid)
                image.image = NamedBlobImage(data=data, filename=filename)
                image.reindexObject()
                return image.absolute_url() + '/@@images/image'
        except Exception as e:
            logger.warning("Could not store uploaded icon for %s: %s",
                           userid, e)
            return None
