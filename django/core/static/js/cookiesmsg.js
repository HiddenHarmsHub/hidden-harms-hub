function getCookie(name) {
    // Convert cookies string to list
    let c_list = document.cookie.split("; "),
        i = 0,
        c,
        c_name,
        c_value;
    // Loop through cookies list to find a match
    for (let i = 0; i < c_list.length; i += 1) {
        // Find cookie
        c = c_list[i].split('=');
        c_name = c[0];
        c_value = c[1];
        // Return cookie value if cookie name matches
        if (c_name === name) {
            return c_value;
        }
    }
    // If no cookie found with given name, return null
    return null;
}


// Show a message about cookies to user if they have not yet agreed

document.cookie = '';

// If user hasn't yet agreed to cookies
if (getCookie('cookieMessageApprove') !== '1') {

    // Generate HTML message
    const cookieDiv = document.createElement('div');
    cookieDiv.id = 'cookie-message-popup';
    cookieDiv.textContent = 'This website uses cookies. By using this website, you accept our use of cookies. See our ';
    const cookiePolicyLink = document.createElement('a');
    cookiePolicyLink.href = '/cookies/';
    cookiePolicyLink.textContent = 'cookies policy';
    cookieDiv.append(cookiePolicyLink);
    const tailText = document.createTextNode(' for more information.');
    cookieDiv.append(tailText);
    const cookieAccept = document.createElement('button');
    cookieAccept.id = 'cookie-message-popup-accept';
    cookieAccept.textContent = 'Accept';
    cookieDiv.append(cookieAccept);

    // Add the HTML message to the page
    document.getElementById('main').append(cookieDiv);

}

// Add event listener for 'accept' button to set the cookie and hide the message
try {
        document.getElementById("cookie-message-popup-accept").addEventListener("click", function () {
        document.cookie = "cookieMessageApprove=1; expires=Mon, 31 Dec 2040 23:59:59 GMT; path=/; Secure;";
        document.getElementById("cookie-message-popup").style.display = "none";
    });
} catch (ignore) {
    // Ignore error, as it's expected to fail when user has already approved (as cookie popup won't show)
}
