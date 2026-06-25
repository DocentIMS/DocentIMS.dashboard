// Dashboard meetings calendar.
// Extracted from app_view.pt. Guarded so it safely no-ops on any page
// that does not render the calendar markup.
(function () {
  var calendarEl = document.getElementById('calendar');
  if (!calendarEl || typeof FullCalendar === 'undefined') {
    return;
  }

  // Toggle the calendar panel.
  $('#toggler').click(function () {
    $('#calendardiv').toggleClass('opacity0');
  });

  // 🎨 Category colors
  const categoryColors = {
    'Project Team Meeting': 'red',
    'Community Meeting': 'green',
  };

  // Active filters
  let activeCategories = [];

  // Meetings store (updated after inject)
  let meetings = [];

  // Convert to FullCalendar format
  function getFilteredEvents() {
    return meetings
      .filter(m => activeCategories.includes(m.category))
      .map(m => ({
        title: m.title,
        start: m.start,
        end: m.end,
        backgroundColor: categoryColors[m.category],
        borderColor: categoryColors[m.category],
        extendedProps: { category: m.category },
      }));
  }

  // 📅 Init calendar (ONLY ONCE)
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    height: 'auto',
    events: function (fetchInfo, successCallback) {
      successCallback(getFilteredEvents());
    },
  });

  calendar.render();

  function bindFilters() {
    document.querySelectorAll('#filters input').forEach(cb => {
      cb.addEventListener('change', () => {
        activeCategories = Array.from(
          document.querySelectorAll('#filters input:checked')
        ).map(el => el.value);
        calendar.refetchEvents();
      });
    });
  }

  // 🎛️ Initial filter handling
  bindFilters();

  // ✅ Rebuild from injected meeting data after each pat-inject
  document.addEventListener('pat-inject-success', function () {
    // 1. Read meetings
    meetings = Array.from(
      document.querySelectorAll('#meetings .meeting')
    ).map(el => ({
      title: el.dataset.title,
      start: el.dataset.start,
      end: el.dataset.end,
      category: el.dataset.category.trim(),
      location: el.dataset.location,
      url: el.dataset.url,
    }));

    // 2. Unique categories
    const categories = [...new Set(meetings.map(m => m.category))];

    // 3. Build filters UI
    const filtersContainer = document.getElementById('filters');
    filtersContainer.innerHTML = '';
    categories.forEach(cat => {
      const label = document.createElement('label');
      label.style.marginRight = '1rem';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = cat;
      checkbox.checked = true;

      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(' ' + cat));
      filtersContainer.appendChild(label);
    });

    // 4. Set active categories
    activeCategories = categories;

    // 5. Re-bind filter events
    bindFilters();

    // 6. Refresh calendar
    calendar.refetchEvents();
  });
})();
