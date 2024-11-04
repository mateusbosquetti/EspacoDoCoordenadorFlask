document.addEventListener('DOMContentLoaded', function () {
    const $html = document.querySelector('html');
    const $button = document.querySelector('#dark-mode-toggle');

    const darkMode = localStorage.getItem('dark-mode');
    if (darkMode === 'enabled') {
        $html.classList.add('dark-mode');
        $button.textContent = 'Light Mode';
    } else {
        $button.textContent = 'Dark Mode';
    }

    $button.addEventListener('click', function (event) {
        event.preventDefault();

        $html.classList.toggle('dark-mode');
        if ($html.classList.contains('dark-mode')) {
            localStorage.setItem('dark-mode', 'enabled');
            $button.textContent = 'Light Mode';
        } else {
            localStorage.setItem('dark-mode', 'disabled');
            $button.textContent = 'Dark Mode';
        }
    });
});