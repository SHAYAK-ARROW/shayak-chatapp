// ============ DARK MODE ============

// localStorage theke theme poreh apply kora
function applyTheme() {
    var theme = localStorage.getItem('theme');

    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

// theme switch korar function (toggle button er jonno)
function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');

    if (current === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// shob page e load howar shathe shathe theme apply kore deya
applyTheme();


// ============ AVATAR ============

// name er first letter return korbe (capital)
function getInitial(name) {
    if (name.length === 0) {
        return "?";
    }

    return name.charAt(0).toUpperCase();
}

// name theke ekta color return korbe (shobshomoy same name e same color)
function getAvatarColor(name) {
    var colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899"];
    var total = 0;
    var i = 0;

    while (i < name.length) {
        total = total + name.charCodeAt(i);
        i = i + 1;
    }

    var index = total % colors.length;
    return colors[index];
}

// page er shob .avatar element e color ar letter set kora
function setupAvatars() {
    var avatars = document.getElementsByClassName('avatar');
    var i = 0;

    while (i < avatars.length) {
        var el = avatars[i];
        var name = el.getAttribute('data-name');

        if (name) {
            el.innerText = getInitial(name);
            el.style.backgroundColor = getAvatarColor(name);
        }

        i = i + 1;
    }
}
