(function (window, document) {

    // we fetch the elements each time because docusaurus removes the previous
    // element references on page navigation
    function getElements() {
        return {
            nav: document.getElementById('main-menu'),
            menu: document.getElementById('menu'),
            menuButton: document.getElementById('menu-button')
        };
    }

    function toggleClass(element, className) {
        var classes = element.className.split(/\s+/);
        var length = classes.length;
        var i = 0;

        for (; i < length; i++) {
            if (classes[i] === className) {
                classes.splice(i, 1);
                break;
            }
        }
        // The className is not found
        if (length === classes.length) {
            classes.push(className);
        }

        element.className = classes.join(' ');
    }

    function toggleAll() {
        var active = 'active';
        var elements = getElements();   
        toggleClass(elements.nav, active);
        toggleClass(elements.menu, active);
        toggleClass(elements.menuButton, active);
    }
    
    function handleEvent(e) {
        var elements = getElements();
        if (e.target.id === elements.menuButton.id || e.target.parentNode.id === elements.menuButton.id) {
            toggleAll();
            e.preventDefault();
        } else if (elements.menu.className.indexOf('active') !== -1) {
            toggleAll();
        }
    }
    
    document.addEventListener('click', handleEvent);

}(this, this.document));
