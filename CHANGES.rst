Changelog
=========


1.0a1 (unreleased)
------------------

- Actually remove the standard "Title" and "Summary" fields from the Project
  form on existing sites by stripping the plone.basic / plone.dublincore /
  plone.namefromtitle behaviors from the FTI (added upgrade step
  1002 -> 1003); reimporting the type info alone could not drop them.
  [docentims]

- Fix a dormant broken import (OrderedSelectFieldWidget) in content/project.py
  that crashed instance startup once the module was imported at ZCML load
  time. Import it from z3c.form.browser.orderedselect.
  [docentims]

- Rework the Add Project Connection form: remove the standard "Title" field
  and add required "Project Title", "Project Short Name" and "Project Very
  Short Name" fields (and make "Add Employee(s)" required), so this data is
  entered on the dashboard instead of the action item configuration. The
  object title and id are now derived from "Project Title", which is also
  used by the welcome emails. Added upgrade step 1001 -> 1002 to reimport the
  Project type.
  [docentims]

- Remove "Preferences" and stock "Dashboard" actions from the user pulldown
  for all users. Added upgrade step 1000 -> 1001 to reimport actions on
  existing sites.
  [docentims]

- Initial release.
  [espenmn]
