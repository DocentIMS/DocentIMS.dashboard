Changelog
=========


1.0a1 (unreleased)
------------------

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
