
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
