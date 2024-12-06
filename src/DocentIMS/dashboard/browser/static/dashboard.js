
$(document).ready(function () {
    // Cache selectors to improve performance
    const $navLinks = $(".nav-item > a");
    const $navLinksFirst = $(".nav-item > a.active");
    const $projectSelect = $(".projectselect");
    const $loader = $(".loader");

    // Handle click events on navigation links
    $navLinks.on("click", function () {
        //$(".projectPreview").fadeOut(100);
        $(".projectPreview").css('opacity', '0.35');
        $navLinks.removeClass("active"); // Remove 'active' class from all links
        $(this).addClass("active"); // Add 'active' class to the clicked link
        document.querySelector(".pat-inject.active").addEventListener("pat-inject-success", (e) => {
            $(".projectPreview").fadeIn(500);
            $(".projectPreview").css('opacity', '1');
        })

        // Hide project selection section
        $projectSelect.hide();

        // Show loader message and fade it out after 2.5 seconds
        $loader.html("<p>Loading…</p>").fadeOut(2500);
    });

    // Trigger click event on the first navigation link to set it as active
    setTimeout(function () {
        $navLinksFirst.click();
    }, 100); // 1000 milliseconds = 1 second

});