// const handleOnMouseMove = e => {
//     const { currentTarget: target } = e;

//     const rect = target.getBoundingClientRect(),
//         x = e.clientX - rect.left,
//         y = e.clientY - rect.top;

//     target.style.setProperty("--mouse-x", `${x}px`);
//     target.style.setProperty("--mouse-y", `${y}px`);
// }

// for (const deal of document.querySelectorAll(".card")) {
//     deal.onmousemove = e => handleOnMouseMove(e);
// }

for (const element of document.getElementsByClassName("cards")) {
    element.onmousemove = e => {
        for (const card of document.getElementsByClassName("card")) {

            const rect = card.getBoundingClientRect(),
                x = e.clientX - rect.left,
                y = e.clientY - rect.top;

            card.style.setProperty("--mouse-x", `${x}px`);
            card.style.setProperty("--mouse-y", `${y}px`);
        }
    }
}

// const container = document.querySelector(".instagram-post");
// const scrollLeftBtn = document.getElementById("scrollLeft");
// const scrollRightBtn = document.getElementById("scrollRight");

// // Function to update button visibility
// function updateButtons() {
//     scrollLeftBtn.style.display = container.scrollLeft > 0 ? "block" : "none";
//     scrollRightBtn.style.display =
//         container.scrollLeft + container.clientWidth < container.scrollWidth ? "block" : "none";
// }

// // Scroll event listener
// container.addEventListener("scroll", updateButtons);

// // Click events for buttons
// scrollLeftBtn.addEventListener("click", () => {
//     container.scrollBy({ left: -500, behavior: "smooth" });
// });

// scrollRightBtn.addEventListener("click", () => {
//     container.scrollBy({ left: 500, behavior: "smooth" });
// });

// // Initial check on page load
// updateButtons();

const phoneNumber = "+421918215490";
const phoneLink = document.getElementById("phone-link");

console.log(phoneLink);

function isMobileDevice() {
    return /Mobi|Android|iPhone/i.test(navigator.userAgent);
}

console.log(isMobileDevice());

if (isMobileDevice()) {
    phoneLink.href = `tel:${phoneNumber}`;
} else {
    console.log("here")
    phoneLink.href = "#";
    phoneLink.addEventListener("click", function (event) {
        event.preventDefault();
        navigator.clipboard.writeText(phoneNumber)
            .then(() => alert("Phone number copied to clipboard!"))
            .catch(err => console.error("Error copying phone number:", err));
    });
}

