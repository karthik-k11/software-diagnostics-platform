console.log("Software Diagnostics Platform Loaded");

document.addEventListener("DOMContentLoaded", () => {

    const links = document.querySelectorAll(
        '.sidebar-nav a[href^="#"]'
    );

    links.forEach(link => {

        link.addEventListener("click", event => {

            event.preventDefault();

            links.forEach(item => {
                item.classList.remove("active-link");
            });

            link.classList.add("active-link");

            const target = document.querySelector(
                link.getAttribute("href")
            );

            if(target){

                target.scrollIntoView({
                    behavior:"smooth",
                    block:"start"
                });

            }

        });

    });

    if(links.length > 0){

        links[0].classList.add(
            "active-link"
        );

    }

    const exportButton =
        document.getElementById("exportButton");

    const exportMenu =
        document.getElementById("exportMenu");

    if(exportButton){

        exportButton.addEventListener(
            "click",
            () => {

                exportMenu.style.display =
                    exportMenu.style.display === "block"
                    ? "none"
                    : "block";

            }
        );

    }

});