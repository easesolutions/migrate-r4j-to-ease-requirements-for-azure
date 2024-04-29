let list = document.getElementsByClassName("label")
list[0].parentElement.className = "root"
for (var i = 1; i < list.length; i++) {
    if (list[i].nextElementSibling != null) {
        list[i].getElementsByTagName("icon")[0].className = "parent-close"
    } else {
        list[i].getElementsByTagName("icon")[0].className = "item"
    }
    list[i].addEventListener("click", someFunction);
}

function someFunction() {
    let childList = this.nextElementSibling;
    if (childList.style.display === "block") {
        this.getElementsByTagName("icon")[0].className = "parent-close"
        if (this.getElementsByTagName("span")[0].className != "issue fa-check-square")
            this.getElementsByTagName("span")[0].className = "folder fa-folder"
        childList.style.display = "none";
    } else {
        this.getElementsByTagName("icon")[0].className = "parent-open"
        if (this.getElementsByTagName("span")[0].className != "issue fa-check-square")
            this.getElementsByTagName("span")[0].className = "folder fa-folder-open"
        childList.style.display = "block";
    }
}