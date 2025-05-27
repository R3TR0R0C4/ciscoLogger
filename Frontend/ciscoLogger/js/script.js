$(document).ready(function() {
    let hoverTimer; // To manage the delay before showing tooltip
    let currentAjaxRequest = null; // To manage active AJAX request for tooltip

    // Function to load main switch interface data
    function loadSwitchData(switchIp) {
        $('#content-area').html('<p class="loading-message">Loading data for ' + switchIp + '...</p>');
        $.ajax({
            url: 'get_switch_data.php',
            type: 'GET',
            data: { switch_ip: switchIp },
            dataType: 'json',
            success: function(response) {
                if (response.error) {
                    $('#content-area').html('<p class="error-message">Error: ' + response.error + '</p>');
                    return;
                }
                if (response.length === 0) {
                    $('#content-area').html('<p>No data found for switch ' + switchIp + '.</p>');
                    return;
                }

                let tableHtml = '<table><thead><tr>';
                const columnsToDisplay = Object.keys(response[0]).filter(key => key !== 'id');

                columnsToDisplay.forEach(key => {
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    tableHtml += '<th>' + formattedKey + '</th>';
                });
                tableHtml += '</tr></thead><tbody>';

                response.forEach(row => {
                    let rowClass = '';
                    if (row.status === 'Not connected') {
                        rowClass = 'status-not-connected';
                    } else if (row.status === 'Shutdown') {
                        rowClass = 'status-shutdown';
                    }

                    tableHtml += '<tr class="' + rowClass + '">';
                    columnsToDisplay.forEach(key => {
                        tableHtml += '<td>' + (row[key] !== null ? htmlEscape(row[key]) : '') + '</td>';
                    });
                    tableHtml += '</tr>';
                });
                tableHtml += '</tbody></table>';
                $('#content-area').html(tableHtml);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#content-area').html('<p class="error-message">Error loading data: ' + textStatus + ' - ' + errorThrown + '</p>');
            }
        });
    }

    // Basic HTML escaping function
    function htmlEscape(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Tab click handler
    $('#tabs-container').on('click', '.tab-button', function() {
        $('.tab-button').removeClass('active');
        $(this).addClass('active');

        const switchIp = $(this).data('switch-ip');
        loadSwitchData(switchIp);
    });

    // Initial page load: click the first tab
    if ($('.tab-button').length > 0) {
        $('.tab-button').first().click();
    }

    // --- Tooltip Logic ---

    // Mouse enters tab button
    $('#tabs-container').on('mouseenter', '.tab-button', function() {
        const $thisButton = $(this);
        const ip_address = $thisButton.data('switch-ip');

        // Clear any existing timer to prevent multiple tooltips/requests
        clearTimeout(hoverTimer);
        if (currentAjaxRequest) {
            currentAjaxRequest.abort(); // Abort previous AJAX if still running
            currentAjaxRequest = null;
        }

        // Start timer for 3 seconds
        hoverTimer = setTimeout(function() {
            // Fetch device info
            currentAjaxRequest = $.ajax({
                url: 'get_device_info.php', // New PHP endpoint
                type: 'GET',
                data: { ip_address: ip_address },
                dataType: 'json',
                success: function(deviceInfo) {
                    currentAjaxRequest = null; // Clear request after success

                    if (deviceInfo.error) {
                        // Handle error, maybe a small red text near cursor
                        console.error("Error fetching device info:", deviceInfo.error);
                        return;
                    }

                    if ($.isEmptyObject(deviceInfo)) {
                         // No data found for this IP
                        console.warn("No device info found for IP:", ip_address);
                        return;
                    }

                    // Create tooltip content
                    let tooltipContent = '<div class="tooltip-content">';
                    tooltipContent += '<p><strong>IP Address:</strong> ' + htmlEscape(deviceInfo.ip_address) + '</p>';
                    tooltipContent += '<p><strong>Hostname:</strong> ' + htmlEscape(deviceInfo.hostname) + '</p>';
                    if (deviceInfo.location) {
                        tooltipContent += '<p><strong>Location:</strong> ' + htmlEscape(deviceInfo.location) + '</p>';
                    }
                    if (deviceInfo.model) {
                        tooltipContent += '<p><strong>Model:</strong> ' + htmlEscape(deviceInfo.model) + '</p>';
                    }
                    tooltipContent += '</div>';

                    // Create tooltip element
                    let $tooltip = $('<div class="custom-tooltip"></div>').html(tooltipContent);
                    $('body').append($tooltip); // Append to body to ensure it's on top

                    // Position the tooltip relative to the hovered button
                    const buttonOffset = $thisButton.offset();
                    const buttonWidth = $thisButton.outerWidth();
                    const buttonHeight = $thisButton.outerHeight();

                    // Position below and slightly right of the button
                    $tooltip.css({
                        top: buttonOffset.top + buttonHeight + 10, // 10px below button
                        left: buttonOffset.left,
                        position: 'absolute',
                        zIndex: 1000 // Ensure it's on top of other elements
                    }).fadeIn(200); // Fade in for a smoother appearance

                },
                error: function(jqXHR, textStatus, errorThrown) {
                    currentAjaxRequest = null; // Clear request after error
                    if (textStatus === "abort") {
                        console.log("AJAX request for tooltip aborted.");
                        return; // Do nothing if aborted intentionally
                    }
                    console.error("AJAX Error fetching device info:", textStatus, errorThrown);
                }
            });
        }, 400); // 3000 milliseconds = 3 seconds delay
    });

    // Mouse leaves tab button
    $('#tabs-container').on('mouseleave', '.tab-button', function() {
        clearTimeout(hoverTimer); // Clear the timer if mouse leaves before delay
        if (currentAjaxRequest) {
            currentAjaxRequest.abort(); // Abort the AJAX request if it's still running
            currentAjaxRequest = null;
        }
        $('.custom-tooltip').remove(); // Immediately remove the tooltip
    });
});