
$(document).ready(function () {
    // Cache selectors to improve performance
    const $navLinks = $(".nav-item > a");
    const $projectSelect = $(".projectselect");
    const $loader = $(".loader");

    // Handle click events on navigation links (switching projects)
    $navLinks.on("click", function () {
        $(".projectPreview").css('opacity', '0.35');
        $navLinks.removeClass("active"); // Remove 'active' class from all links
        $(this).addClass("active"); // Add 'active' class to the clicked link

        // Hide project selection prompt and show a brief loader
        $projectSelect.hide();
        $loader.html("<p>Loading…</p>").fadeOut(2500);
    });

    // Whenever a project panel finishes injecting — whether it was
    // autoloaded on page open (the active pill carries
    // `trigger: autoload`) or clicked — reveal it and drop the
    // "select project" prompt. This replaces the old, timing-fragile
    // setTimeout click that often failed to load on first open.
    document.addEventListener("pat-inject-success", function () {
        $projectSelect.hide();
        $loader.hide();
        $(".projectPreview").css('opacity', '1').fadeIn(300);
    });
});


// On the email-settings control panel, inject a "Send test email" box right
// under the first email message field. Sends in the background via the
// @@email-pre-view JSON endpoint. No-ops on every other page.
(function () {
    function init() {
        var anchor = document.getElementById('formfield-form-widgets-email_message');
        if (!anchor) {
            var w = document.getElementById('form-widgets-email_message') ||
                    document.querySelector('[id*="email_message"]:not([id*="returning"])');
            anchor = w ? (w.closest('.field') || w) : null;
        }
        if (!anchor || document.getElementById('emailTestBox')) {
            return;
        }

        var token = document.querySelector('[name="_authenticator"]');
        token = token ? token.value : '';

        var box = document.createElement('div');
        box.id = 'emailTestBox';
        box.className = 'emailTestBox';
        box.innerHTML =
            '<label><strong>Send a test of this email to:</strong></label> ' +
            '<input type="email" id="emailTestAddr" placeholder="you@example.com" size="28"> ' +
            '<button type="button" id="emailTestSend" class="btn btn-primary plone-btn plone-btn-primary">Send test</button> ' +
            '<span id="emailTestMsg" class="emailTestMsg"></span>';
        anchor.parentNode.insertBefore(box, anchor.nextSibling);

        document.getElementById('emailTestSend').addEventListener('click', function () {
            var addr = (document.getElementById('emailTestAddr').value || '').trim();
            var msg = document.getElementById('emailTestMsg');
            if (!addr) { msg.textContent = 'Enter an email address.'; return; }
            msg.textContent = 'Sending…';
            var data = new URLSearchParams();
            data.set('send_test', '1');
            data.set('test_email', addr);
            data.set('ajax', '1');
            if (token) { data.set('_authenticator', token); }
            fetch(location.origin + '/email-pre-view', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: data.toString(),
                credentials: 'same-origin'
            }).then(function (r) { return r.json(); })
              .then(function (j) { msg.textContent = j.status || 'Done.'; })
              .catch(function () {
                  msg.textContent = 'Send failed — try the /email-pre-view page directly.';
              });
        });
    }

    if (document.readyState !== 'loading') { init(); }
    else { document.addEventListener('DOMContentLoaded', init); }
})();
